
from models import generate_gifts, generate_images
from products import GetProducts
from flask import Flask, request, jsonify, render_template


# app.py

app = Flask(__name__,template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def get_gifts():
    data = request.json
    occasion = data['occasion']
    attributes = data['attributes']
    
    gifts= generate_gifts(prompt=attributes, context=occasion, max_tokens=1000, temp=0.2)
    
    return jsonify([gift.strip('"')[3:] for gift in gifts.split('\n')])


@app.route('/image', methods=['POST'])
def get_image():
    data = request.json
    gift = data['gift']
    xla = data['xla']
    
    #image_names=generate_images(gift,xla)
    image_names=['gift_1.png','gift_2.png','gift_3.png']
    return jsonify(image_names)


@app.route('/products', methods=['POST'])
def get_products():
    
    data = request.json
    Products=GetProducts(data['budget'],data['gift_name'], data['image_path'])
    products=Products.getResult()
    
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True)

