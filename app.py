import streamlit as st
from keras.models import model_from_json
from keras.applications import VGG16
from keras.applications import imagenet_utils
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array

import numpy as np
from PIL import Image
from Configuration import InferenceConfig
import mrcnn.model as modellib
import skimage.draw
from mrcnn import visualize
import time

def main():

    VGG16_model = VGG16(weights='imagenet', include_top=False,input_shape=(224, 224, 3))
    VGG16_model.summary()

    splashConfig = InferenceConfig()
    SplashModel = modellib.MaskRCNN(mode="inference", config=splashConfig,model_dir="")
    SplashModel.load_weights("SavedModels/SplashModelWeights.h5", by_name=True)

    json_file = open('SavedModels/model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights("SavedModels/scratchmodel.best.hdf5")

    st.markdown('#### This is a Car Damage Severity & Region Detection App by TPL Data Science Team')


    def car_severity_estimator(image_path,VGG16_model, model_severity):
        
            
        st.write ("Determining severity of damage...")
        #urllib.urlretrieve(image_path, 'save.jpg') # or other way to upload image
        img = load_img(image_path, target_size=(224, 224)) # this is a PIL image 
        x = img_to_array(img) # this is a Numpy array with shape (3, 256, 256)
        #x = x.reshape((1,) + x.shape)/255 # this is a Numpy array with shape (1, 3, 256, 256)
        x = np.expand_dims(x, axis=0)
        
        x = imagenet_utils.preprocess_input(x)
        
        features = VGG16_model.predict(x, batch_size=32)
        
        pred = model_severity.predict(features)
        pred_label = np.argmax(pred, axis=1)
       
        d = {0: 'Minor', 1: 'Moderate', 2: 'Severe'}
        for key in d.keys():
            if pred_label[0] == key:
                st.write("Severity assessment complete.")
                st.markdown("### Assessment: '{}' damage to vehicle".format(d[key]))
          

    #car_severity_estimator('/home/data/Projects/CarModelDetection/ImageAnalysis/data/raw/car-damage-dataset/data3a/test/minor_0088.JPEG', VGG16_model,loaded_model)

    def mark_detect(model,image_path=None):
        if image_path:
        
            # Read image
            image = skimage.io.imread(image_path)
            # Detect objects
            r = model.detect([image], verbose=1)[0]
            # Color splash
            splash = color_splash(image, r['masks'])
            # Save output
            import datetime
            file_name = "TempSplashImages/splash_{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
            skimage.io.imsave(file_name, splash)

            #Visualize results
            masked_image = visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'], ['bkground','damage'], r['scores'])
            file_name = "TempSplashImages/splash_boundry{:%Y%m%dT%H%M%S}.png".format(datetime.datetime.now())
            skimage.io.imsave(file_name, masked_image.astype(np.uint8))
            return file_name
    
        
    def color_splash(image, mask):
        """Apply color splash effect.
        image: RGB image [height, width, 3]
        mask: instance segmentation mask [height, width, instance count]

        Returns result image.
        """
        # Make a grayscale copy of the image. The grayscale copy still
        # has 3 RGB channels, though.
        gray = skimage.color.gray2rgb(skimage.color.rgb2gray(image)) * 255
        # We're treating all instances as one, so collapse the mask into one layer
        mask = (np.sum(mask, -1, keepdims=True) >= 1)
        # Copy color pixels from the original color image where mask is set
        if mask.shape[0] > 0:
            splash = np.where(mask, image, gray).astype(np.uint8)
        else:
            splash = gray
        return splash
    
    uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg','jpeg'])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        image.save("TestImages/test1.jpg",)
        
        car_severity_estimator('TestImages/test1.jpg', VGG16_model,loaded_model)
        masked_img = mark_detect(SplashModel,'TestImages/test1.jpg')

        image = Image.open(masked_img)
        
        st.image(image, caption='Damage Severity & Region estimate',use_column_width=True)

        
    




if __name__== '__main__':

   main()
   
