import requests
from detecto import core, utils, visualize
import json 
import streamlit as st
from PIL import Image
import cv2
import numpy as np

def main():

    def checkIfCellExists(imagepath):
        image = utils.read_image(imagepath)
        model = core.Model()
        labels, boxes, scores = model.predict_top(image)
        if 'cell phone' in labels:
            i = labels.index('cell phone')
            st.write('Cell Found with probablity : %  ', str("{0:.2f}".format(scores[i].item())))
            print(labels,scores,boxes)
            cropImage(list(boxes[i])[0].item(),list(boxes[i])[1].item(),list(boxes[i])[2].item(),list(boxes[i])[3].item())
        else:
            st.write('Cell Not Detected')

        

    def cropImage(xmin,ymin,xmax,ymax):
        ###crop image with above bbox
        with Image.open('./MobileImages/test1.jpg') as im:
            im1 = im.crop((float(xmin), float(ymin), float(xmax), float(ymax))) 
            # Save the image in dir 
            im1.save('./CroppedImages/test1.jpg')
        with Image.open('./CroppedImages/test1.jpg') as cim:
            getClassification('./CroppedImages/test1.jpg')
            image = np.array(cim) 
            st.image(image, caption=f"Processed image", use_column_width=False,)
            
    
    def getClassification(imagePath):
        
        ### send the cropped image to classification model (damage or no-damage)
        url = 'https://app.nanonets.com/api/v2/ImageCategorization/LabelFile/'

        data = {'file': open(imagePath, 'rb'), 'modelId': ('', 'bea2ea7d-c0cb-4c37-879f-a5ceb01fa44f')}

        response = requests.post(url, auth= requests.auth.HTTPBasicAuth('FJCXMDOI7G269nW0lzZ8gZp8AC9EGJOl', ''), files=data)

        print(response.text)
        #breakpoint()

         ## get max probablity bbox
        d = json.loads(response.text)
        d = d['result'][0]['prediction']

        maxProbablityItem = max(d, key=lambda x:x['probability'])
        st.write(maxProbablityItem['label'] + ' Detected' , 'with probablity % ' + str("{0:.2f}".format(float(maxProbablityItem['probability']))))
 
    
    st.markdown('#### This is a Cell Phone Detection & Damage Detection App by TPL Data Science Team')
    
    ### Upload Image 
    uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg','jpeg'])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        image.save("MobileImages/test1.jpg",)
        checkIfCellExists('MobileImages/test1.jpg')


if __name__== '__main__':
    
    main()