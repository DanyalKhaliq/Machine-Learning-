from detecto import core, utils, visualize
from PIL import Image 
import os
import sys 
DIR = './MobileImages/'
entries = os.scandir(DIR)

print (len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]))
#print(sys.argv[1])
if len(sys.argv) > 1:
        
    image = utils.read_image(sys.argv[1])
    model = core.Model()
    labels, boxes, scores = model.predict_top(image)
    labels_set = set(labels) 
    #print(labels,scores)

    if "cell phone" in labels_set:
        ind = labels.index("cell phone")
    
        with Image.open(sys.argv[1]) as im:
            im1 = im.crop((float(boxes[ind][0]), float(boxes[ind][1]), float(boxes[ind][2]), float(boxes[ind][3]))) 
                # Save the image in dir 
            im1 = im1.save('./CroppedImages/test.jpg') 
                    
    visualize.show_labeled_image(image, boxes, labels)

else:
    
    for entry in entries:

        image_name = entry.name
        image = utils.read_image(DIR + image_name)
        model = core.Model()

        labels, boxes, scores = model.predict_top(image)
        print(image_name,labels)
        data_string = 'cell phone'
        labels_set = set(labels) 
        if data_string in labels_set : 
            #print ("Element Exists")
            ind = labels.index(data_string)
            
            #visualize.show_labeled_image(image, boxes[ind], labels[ind])

            with Image.open('./MobileImages/' + image_name) as im:
                im1 = im.crop((float(boxes[ind][0]), float(boxes[ind][1]), float(boxes[ind][2]), float(boxes[ind][3]))) 
                # Save the image in dir 
                im1 = im1.save('./CroppedImages/' + image_name) 
         

    
    
    
