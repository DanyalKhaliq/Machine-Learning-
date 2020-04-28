from flask import Flask, jsonify, request
from detecto import core, utils, visualize
import requests
import tempfile
import os
import json 
import numpy as np
import pandas as pd 
import random as rn
import tensorflow as tf
from keras.applications import VGG16
from keras.applications import imagenet_utils
from keras.models import model_from_json
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.models import load_model
from PIL import Image

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

vggModel = VGG16(weights='imagenet', include_top=False,input_shape=(224, 224, 3))
            
model_transfer = load_model("./SavedModels/model.hd5")

graph = tf.get_default_graph()

@app.route('/upload', methods=['POST'])
def upload():
    file_ = request.files['file']
    handle, filename = tempfile.mkstemp()
    print(filename)
    os.close(handle)
    file_.save(filename + '.jpg')
    data = checkIfCellExists(filename + '.jpg')
    return jsonify(data)

def checkIfCellExists(imagepath):
        image = utils.read_image(imagepath)
        model = core.Model()
        labels, boxes, scores = model.predict_top(image)
        if 'cell phone' in labels:
             
            #model_transfer.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

            i = labels.index('cell phone')
            print('Cell Found with probablity : %  ', str("{0:.2f}".format(scores[i].item())))
            print(labels,scores,boxes)
            #data  = cropImage(list(boxes[i])[0].item(),list(boxes[i])[1].item(),list(boxes[i])[2].item(),list(boxes[i])[3].item(),imagepath)
               
            data = mobile_damage_estimator(imagepath,model_transfer,vggModel)

            return {'Cell Detected' : 'Yes' , 'Cell Probablity' : str("{0:.2f}".format(scores[i].item()))
                    ,'DamageStatus':data['Damage Status'], 'Probablity':int(data['Probability']) - 1 }
        else:
            
            return {'Cell Detected' : 'No'}

def cropImage(xmin,ymin,xmax,ymax,imagepath):
        #crop image with above bbox
        with Image.open(imagepath) as im:
            im1 = im.crop((float(xmin), float(ymin), float(xmax), float(ymax))) 
            # Save the image in dir 
            im1.save('./CroppedImages/test1.jpg')
        with Image.open('./CroppedImages/test1.jpg') as cim:
            return getClassification('./CroppedImages/test1.jpg')
        
def mobile_damage_estimator(image_path, model_transfer,vggModel):

    global graph
    with graph.as_default():
        try:
   
            print ("Determining if damaged...")
            #urllib.urlretrieve(image_path, 'save.jpg') # or other way to upload image
            img = load_img(image_path, target_size=(224, 224)) # this is a PIL image 
            x = img_to_array(img) # this is a Numpy array with shape (3, 256, 256)
            #x = x.reshape((1,) + x.shape)/255 # this is a Numpy array with shape (1, 3, 256, 256)
            x = np.expand_dims(x, axis=0)
            
            x = imagenet_utils.preprocess_input(x)
            
            features = vggModel.predict(x, batch_size=32)
            
            pred = model_transfer.predict(features)
            
            pred_label = np.argmax(pred, axis=1)
            
            result = { "Damage Status": "NA", "Probability": 0.0}
            
            d = {0: 'NoDamage', 1: 'Damage'}
            
            for key in d.keys():
                if pred_label[0] == key:
                    print ("Assessment: {} to Mobile".format(d[key]))
                    result["Damage Status"] = d[key]
                    result["Probability"] = str("{0:.0f}".format(int(pred[0][key]*100)))
                    
            print(result)
            #view_images(image_path)
            return result
        except Exception as e:
            print(e)
        
def getClassification(imagePath):
        
        ### send the cropped image to classification model (damage or no-damage)
        #url = 'https://app.nanonets.com/api/v2/ImageCategorization/LabelFile/'

        #data = {'file': open(imagePath, 'rb'), 'modelId': ('', 'bea2ea7d-c0cb-4c37-879f-a5ceb01fa44f')}

        #response = requests.post(url, auth= requests.auth.HTTPBasicAuth('FJCXMDOI7G269nW0lzZ8gZp8AC9EGJOl', ''), files=data)

        #print(response.text)
        #breakpoint()

         ## get max probablity bbox
        #d = json.loads(response.text)
        #d = d['result'][0]['prediction']

        #maxProbablityItem = max(d, key=lambda x:x['probability'])
        #print(maxProbablityItem['label'] + ' Detected' , 'with probablity % ' + str("{0:.2f}".format(float(maxProbablityItem['probability']))))
        return maxProbablityItem


# if __name__ == '__main__':
#     app.run(host='0.0.0.0' ,port=8088)