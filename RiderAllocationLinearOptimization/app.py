from flask import Flask,jsonify,request,render_template
import json
import os 
from DeliveryHub import DeliveryHub

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("input.html")

@app.route('/postjson', methods = ['POST','GET'])
def postJsonHandler():
    #print (request.is_json)
    content = request.get_json()
    #print (content)
    
    hubdata = DeliveryHub(content['HN'],
                          float(content['MR']),float(content['MC']),
                          float(content['RC']),float(content['CC']),
                          float(content['RCKM']),float(content['CCKM']),
                          float(content['DTC']),float(content['TORQ']))
    test = hubdata.CalculateOptimizedSolution()
    return jsonify(test)

if __name__ == '__main__':
    #app.run(port=5001, debug=True)
    if 'WINGDB_ACTIVE' in os.environ:
        app.debug = False    
    app.run(port=5001)        