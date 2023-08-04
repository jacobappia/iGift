


import numpy as np

"""##Web Scraping"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import random
import re
from PIL import Image
import os
import urllib
from skimage import io, transform
from skimage.metrics import mean_squared_error, structural_similarity
#CONVERT REFERNCE IMAGE TO RGB FORMAT
from skimage import color


class GetProducts():
    
    def __init__(self, budget, gift_name, image_path):
        self.budget = int(budget)
        self.gift_name=gift_name
        self.gen_image_path=image_path
        
        
        
        
    # Generate random float for budget
    def random_float(self,min_value, max_value):
        return random.uniform(min_value, max_value)

    # Function to webscrape and filter the products
    def webscrape_and_filter(self):
        # Create the eBay URL based on the gift name
        gifturl = 'https://www.ebay.com/sch/i.html?_nkw=' + self.gift_name.replace(' ', '+')

        # Make an HTTP request to get the HTML content of the URL
        response = requests.get(gifturl)
        html_content = response.content

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        cont = soup.find_all(attrs={'class': "s-item__wrapper clearfix"})

        
        products = []
        for i in cont:
            product = {'Title': re.sub(r'<[^>]+>', '', str(i.find(attrs={'class': "s-item__title"}))),
                    'Price': re.sub(r'<[^>]+>', '', str(i.find(attrs={'class': "s-item__price"}))),
                    'Image': i.find(attrs={'class': "s-item__image-wrapper image-treatment"}).img['src'],
                    'Link': i.find(attrs={'class': "s-item__link"})['href']}
            products.append(product)

        # Create a DataFrame to store the extracted data
        columns = ['Title', 'Price', 'Image', 'Link']
        df = pd.DataFrame(products, columns=columns)

        # Filter out products with invalid price format
        try:
            df['Price'] = df['Price'].str.replace('$', '')
        except ValueError as e:
            pass
            #df = df[~df['Price'].str.contains(r'\d+\.\d+ to \d+\.\d+', na=False)]

        # Convert 'Price' column to numeric
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

        # Drop rows with missing prices
        df = df.dropna(subset=['Price'])

        # Filter products based on the budget
        df = df[df['Price'] <= self.budget]

        # Sort the final DataFrame by price in ascending order
        result_df = df.sort_values(by='Price', ascending=True)
        result_df=result_df.iloc[-3:,:]
        return result_df



    # Define a function to download and save an image
    def save_image(self,image_url, file_name):
        with urllib.request.urlopen(image_url) as response:
            with open('./static/images/'+file_name, 'wb') as out_file:
                out_file.write(response.read())
    

    # Function to calculate the similarity scores
    def calculate_similarity(self,image_path, rgb_reference_image, reference_height, reference_width, _):
        image = io.imread(image_path)

        # Resize the image to the same shape as the reference image
        resized_image = transform.resize(image, (reference_height, reference_width, _), mode='constant')

        # Calculate similarity scores
        mse = mean_squared_error(rgb_reference_image, resized_image)
        ssim = structural_similarity(rgb_reference_image, resized_image, multichannel=True)
        return mse, ssim


    def getResult(self, total=3):
        
        result_df = self.webscrape_and_filter()
            
        for index, row in result_df.iterrows():
            image_url = row['Image']
            file_name = f"Image_{index}.jpg"  # Customize the file name as needed
            self.save_image(image_url, file_name)

        """###Similarity Score"""
        # Load the reference image
        reference_image_path = './static/images/' + self.gen_image_path  # Update with the path of your reference image
        reference_image = io.imread(reference_image_path)

        # Check if the image is already in RGB format (3 channels)
        if reference_image.shape[-1] == 3:
            # The image is already in RGB format
            rgb_reference_image = reference_image
        else:
            # Convert the grayscale image to RGB format
            rgb_reference_image = color.gray2rgb(reference_image)

        # Get the dimensions of the reference image
        reference_height, reference_width, _ = rgb_reference_image.shape
        # Assuming you have saved images from 'result_df' in your working directory
        Image_folder = "./static/images/"  # Update with the folder path where images are saved
        similarity_scores = []
        for index, row in result_df.iterrows():
            image_path = os.path.join(Image_folder, f"Image_{index}.jpg")  # Customize the file name pattern
            
            mse, ssim = self.calculate_similarity(image_path, rgb_reference_image, reference_height, reference_width, _)
            similarity_scores.append({'Image': image_path, 'MSE': mse, 'SSIM': ssim})

        # Convert similarity_scores to a DataFrame for easier analysis
        similarity_df = pd.DataFrame(similarity_scores)

        """###Image Match"""

        # Sort the similarity DataFrame by 'SSIM' score in descending order
        sorted_similarity_df = similarity_df.sort_values(by='SSIM', ascending=False)

        # Check if the DataFrame is not empty before proceeding
        if not sorted_similarity_df.empty:
            # Get the image path of the highest similarity image (top row)
            
            top_3=sorted_similarity_df.iloc[:total,:]['Image']

            # Extract the index number from the image name in the working directory
            top_3_dit={}
            for i in top_3:
                idx=int(os.path.basename(i).split('_')[-1].split('.')[0])
                top_3_dit[idx]=i
                
            #print('here')
            
            # Find the matching row in the original DataFrame using the index
            top_3_row = result_df.loc[result_df.index.isin(top_3_dit.keys())]
            for i,v in top_3_dit.items():
                top_3_row.at[i,'Image']=v

            # Check if the matched row exists before converting to a dictionary
            if not top_3_row.empty:
                # Convert the matched row to a dictionary
                result_dict = top_3_row.to_dict('records')
                return result_dict
            else:
                return "No matching row found in the result DataFrame."
                
        else:
            return "No similarity scores found in the similarity DataFrame."