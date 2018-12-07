import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from flask import Flask,jsonify,request,render_template
from pandas import DataFrame, Series
import numpy as np
import pandas as pd
import os 
from copy import copy
import seaborn as sns 
from threading import Thread
from io import BytesIO
import base64
from werkzeug import secure_filename
from concurrent.futures import ThreadPoolExecutor
import json

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
Data_FOLDER = os.path.join('DataDir')
executor = ThreadPoolExecutor(1)
app = Flask(__name__)
app.config['Data_FOLDER'] = Data_FOLDER;

static_folder = os.path.join('static')
app.config['static_folder'] = static_folder

target = os.path.join(APP_ROOT,'photo')
full_filename = os.path.join(app.config['Data_FOLDER'], 'RiderRoutes.csv')    
data = pd.read_csv(full_filename)
locations = sorted(set(list(data['Loc A'].unique()) + list(data['Loc B'].unique())))

best_delivery_routes = None 
finished = False
isTimeOptimized = None

@app.route('/')
def index():
    
    
    global finished
    finished = False
       
    global isTimeOptimized
    isTimeOptimized = None
    
    return render_template("show.html",result = data, locations=locations)


@app.route('/status')
def thread_status():
    global finished
    """ Return the status of the worker thread """
    return jsonify(dict(status=('finished' if finished else 'running')))

@app.route('/result')
def result():
    global best_delivery_routes
    """ Just give back the result of your heavy work """
    with open(os.path.join(app.config['Data_FOLDER'],secure_filename('data.txt')), 'w') as outfile:  
        json.dump(best_delivery_routes, outfile)    
        
    return jsonify({'Best Guess Routes': best_delivery_routes})

def getOptimalDist(locationsList):
   
    global finished
    finished = False
    
    global best_delivery_routes
    best_delivery_routes = None
       
    
    current_generation = create_generation(locationsList,population=200)
    fitness_tracking, best_guess, best_delivery_routes = evolve_to_solve(current_generation, 5, 80, 40, 0.5, 2, 5, verbose=True)
   
    finished = True
    
    #img = BytesIO()
    #sns.set()
    
    #ax = sns.lineplot(data=pd.DataFrame(fitness_tracking))
    #ax.set(ylabel='Min Distance', xlabel='Generation')    
    #plt.savefig(os.path.join(app.config['static_folder'], 'plot.png'))
    
@app.route('/GetBestRoutes',methods=['GET','POST'])
def getBestRoute():
    #Reset the variables that matter to API functionality 
    
    global best_delivery_routes 
    best_delivery_routes = None
    
    global finished
    finished = False
    
    global isTimeOptimized
    isTimeOptimized = None
    
    global startPoint
    op3_checked = False
    if request.form.get("savedBestRoute"):
        op3_checked = True    
    
    if op3_checked:
        with open(os.path.join(app.config['Data_FOLDER'],secure_filename('data.txt'))) as json_file:  
            data = json.load(json_file)        
        return jsonify({'Saved Routes': data}) , 201
    
    startPoint = request.args.get('startPoint')
    locationsToDeliver = locations if request.args.get('locations') is None else request.args.get('locations').split(',')
    
    isTimeOptimized = request.args.get('timeBased')
    executor.submit(getOptimalDist,locationsToDeliver)
    
    #with ThreadPoolExecutor(max_workers=3) as executor:
        #future = executor.submit(getOptimalDist, (locationsToDeliver))
    #print('Setting Finished True')
    #finished = True
    return render_template("Loading.html")

def create_guess(points,startPoint='None'):
    """
    Creates a possible path between all points, returning to the original.
    Input: List of point IDs
    """
    if startPoint == 'None':
        guess = copy(points)
        np.random.shuffle(guess)
        guess.append(guess[0])
    else:
        guess = copy(points)
        np.random.shuffle(guess)
        
        #logic for making the Given StartPoint , The Start and End Point and repalce the 
        #current SP and EP with index of Given SP
        oldStartPoint = guess[0]
        guess = list(guess)
        CurrnetIndexOfNewStartPoint = guess.index(startPoint)
        guess[0] = startPoint
        guess[CurrnetIndexOfNewStartPoint] = oldStartPoint
        guess.append(guess[0])
        
    return list(guess)




def create_generation(points, population=100):
    """
    Makes a list of guessed point orders given a list of point IDs.
    Input:
    points: list of point ids
    population: how many guesses to make
    """
    startPoint1 = 'None' if startPoint is None else startPoint
    generation = [create_guess(points,startPoint1) for _ in range(population)]
    return generation

def distance_between_locations(locA,locB,TimeBased=False):
    colName = 'Distance'
    if TimeBased:
        colName = 'Time'
        
    cost = data[((data['Loc A'] == locA) & (data['Loc B'] == locB) | 
            (data['Loc B'] == locA) & (data['Loc A'] == locB))][colName].values[0]
    return float(cost)

def fitness_score(guess):
    """
    Loops through the points in the guesses order and calculates
    how much distance the path would take to complete a loop.
    Lower is better.
    """
    score = 0
    isTimeOptimized1 = None if isTimeOptimized is None else isTimeOptimized
    for ix, point_id in enumerate(guess[:-1]):
        score += distance_between_locations(guess[ix],guess[ix+1],isTimeOptimized1)
    return score

def check_fitness(guesses):
    """
    Goes through every guess and calculates the fitness score. 
    Returns a list of tuples: (guess, fitness_score)
    """
    fitness_indicator = []
    for guess in guesses:
        fitness_indicator.append((guess, fitness_score(guess)))
    return fitness_indicator


def get_breeders_from_generation(guesses, take_best_N=10, take_random_N=5,
                                 verbose=False, mutation_rate=0.1):
    """
    This sets up the breeding group for the next generation. You have
    to be very careful how many breeders you take, otherwise your
    population can explode. These two, plus the "number of children per couple"
    in the make_children function must be tuned to avoid exponential growth or decline!
    """
    # First, get the top guesses from last time
    fit_scores = check_fitness(guesses)
    sorted_guesses = sorted(fit_scores, key=lambda x: x[1]) # sorts so lowest is first, which we want
    new_generation = [x[0] for x in sorted_guesses[:take_best_N]]
    best_guess = new_generation[0]
    best_route = sorted_guesses[:1]
    if verbose:
        # If we want to see what the best current guess is!
        print("Current Best Route: ",best_guess)

    # Second, get some random ones for genetic diversity
    for _ in range(take_random_N):
        ix = np.random.randint(len(guesses))
        new_generation.append(guesses[ix])

    # No mutations here since the order really matters.
    # If we wanted to, we could add a "swapping" mutation,
    # but in practice it doesn't seem to be necessary

    # Mutation 
#    mutatedPop = []
#    
#    for ind in range(0, len(new_generation)):
#        mutatedInd = mutate(new_generation[ind], mutation_rate)
#        mutatedPop.append(mutatedInd)

    np.random.shuffle(new_generation)
    return new_generation, best_guess, best_route

def make_child(parent1, parent2):
    """ 
    Take some values from parent 1 and hold them in place, then merge in values
    from parent2, filling in from left to right with cities that aren't already in 
    the child. 
    """
    list_of_ids_for_parent1 = list(np.random.choice(parent1, replace=False, size=len(parent1)//2))
    child = [-99 for _ in parent1]

    for ix in range(0, len(list_of_ids_for_parent1)):
        child[ix] = parent1[ix]
    for ix, gene in enumerate(child):
        if gene == -99:
            for gene2 in parent2:
                if gene2 not in child:
                    child[ix] = gene2
                    break
    child[-1] = child[0]
    return child

def make_children(old_generation, children_per_couple=1):
    """
    Pairs parents together, and makes children for each pair. 
    If there are an odd number of parent possibilities, one 
    will be left out. 

    Pairing happens by pairing the first and last entries. 
    Then the second and second from last, and so on.
    """
    mid_point = len(old_generation)//2
    next_generation = [] 

    for ix, parent in enumerate(old_generation[:mid_point]):
        for _ in range(children_per_couple):
            next_generation.append(make_child(parent, old_generation[-ix-1]))
    return next_generation

def mutate(individual, mutationRate):

    #originLocation = individual[0]

    for swapped in range(1,len(individual[1:-1])):
        if(random.random() < mutationRate):
            swapWith = int(random.random() * len(individual[1:-1]))

            city1 = individual[1:-1][swapped]
            city2 = individual[1:-1][swapWith]

            individual[1:-1][swapped] = city2
            individual[1:-1][swapWith] = city1

    return individual

def evolve_to_solve(current_generation, max_generations, take_best_N, take_random_N,
                    mutation_rate, children_per_couple, print_every_n_generations, verbose=False):
    """
    Takes in a generation of guesses then evolves them over time using our breeding rules.
    Continue this for "max_generations" times.
    Inputs:
    current_generation: The first generation of guesses
    max_generations: how many generations to complete
    take_best_N: how many of the top performers get selected to breed
    take_random_N: how many random guesses get brought in to keep genetic diversity
    mutation_rate: How often to mutate (currently unused)
    children_per_couple: how many children per breeding pair
    print_every_n_geneartions: how often to print in verbose mode
    verbose: Show printouts of progress
    Returns:
    fitness_tracking: a list of the fitness score at each generations
    best_guess: the best_guess at the end of evolution
    """
    print("Current Population Fitness Check: ", check_fitness(current_generation))
    fitness_tracking = []
    best_routes = []
    for i in range(max_generations):
        if verbose and not i % print_every_n_generations and i > 0:
            print("Generation %i: "%i, end='')
            print(len(current_generation))
            print("Current Best Score: ", fitness_tracking[-1])
            is_verbose = True
        else:
            is_verbose = False

        breeders, best_guess, best_route = get_breeders_from_generation(current_generation, 
                                                                        take_best_N=take_best_N, take_random_N=take_random_N, 
                                                            verbose=is_verbose, mutation_rate=mutation_rate)
        fitness_tracking.append(fitness_score(best_guess))
        best_routes.append(best_route)
        current_generation = make_children(breeders, children_per_couple=children_per_couple)

    return fitness_tracking, best_guess, best_routes




@app.route('/plot',methods=['POST'])
def show_plot():
    return render_template('Plot.html')  

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join(app.config['Data_FOLDER'],secure_filename(f.filename)))
        
        data = pd.read_csv(full_filename)
        return 'file uploaded successfully'

if __name__ == '__main__':
    #app.run(debug=True)
    import os
    if 'WINGDB_ACTIVE' in os.environ:
        app.debug = False    
    app.run()    
