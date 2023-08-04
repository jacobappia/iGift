#pip install openai pandas numpy matplotlib tensorflow keras_core keras_cv flask pillow bs4 scikit-image

import openai
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import time
import keras_cv
from tensorflow import keras
import os
from PIL import Image



openai.api_key = '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'

# Function to get 3 recommended gift
def generate_gifts(prompt,context, max_tokens,temp):
    response=openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages= [
            {'role':'system','content':'you will be given attributes of a person and occasion, generate top 3 tangible gifts names that we can buy for the person and provide just the names of the gifts and do not describe the gifts'},
            {'role':'user','content':context},
            {'role': 'user','content':prompt}],
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=temp,
    )
    return response['choices'][0]['message']['content']




  # Function to generate 2nd image out of three images for all 3 gifts
def generate_images(gift,xla):
    
    model = keras_cv.models.StableDiffusion(img_width=512, img_height=512, jit_compile=xla)

    images = model.text_to_image(gift, batch_size=3, unconditional_guidance_scale=15) # stable diffusion model
    
    try:
        os.rmdir('./static/images')
    except:
        pass

    os.mkdir('./static/images')
    image_names=[]
    for i in range(len(images)):
        Image.fromarray(images[i]).save("./static/images/gen_image_"+i+".png")
        image_names.append("gen_image_"+i+".png")
        
    
    return image_names

 