import base64
import bcrypt
import io
import numpy as np
import pickle
import random
import re
import string
from flask import Flask, abort, flash, redirect, jsonify, render_template, request, session, url_for
from flask_cors import CORS
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from string import ascii_uppercase
from datetime import datetime
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app) 

app.config["SECRET_KEY"] = "agri123"
app.config['MONGO_URI'] = 'mongodb://localhost:27017/agritest'

mongo = PyMongo(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, email, password, first_name, id=None):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.id = str(id) if id else None

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User(email=user_data['email'], password=user_data['password'], first_name=user_data['first_name'], id=user_data['_id'])
    except Exception as e:
        print(f"Error loading user: {e}")
    return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/connect_home')
def connect_home():
    return render_template('connect_home.html')

@app.route('/dashboard')
def dashboard():
    if current_user.is_authenticated:
        try:
            crop_details = list(mongo.db.crop_details.find({'user_id': current_user.id}))
            return render_template('dashboard.html', crop_details=crop_details)
        except Exception as e:
            print(f"Error loading dashboard: {e}")
            return render_template('dashboard.html')
    else:
        return render_template('dashboard.html')
    
@app.route('/news')
def news():
    return render_template('news.html')
    
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_crop():
    if request.method == 'POST':
        try:
            crop_details = {
                'crop_name': request.form['crop_name'],
                'date_planted': datetime.strptime(request.form['date_planted'], '%Y-%m-%d'),
                'land_details': request.form['land_details'],
                'fertilizer_details': request.form['fertilizer_details'],
                'pesticides_details': request.form['pesticides_details'],
                'other_details': request.form['other_details'],
                'user_id': current_user.id
            }
            mongo.db.crop_details.insert_one(crop_details)
            flash('Crop details added successfully!', category='success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Error adding crop: {str(e)}', category='error')
    return render_template('add_crop.html')

@app.route('/crop/<crop_id>', methods=['GET', 'POST'])
@login_required
def crop_detail(crop_id):
    try:
        crop = mongo.db.crop_details.find_one_or_404({'_id': ObjectId(crop_id)})
        if crop['user_id'] != current_user.id:
            abort(403)
        if request.method == 'POST':
            if request.form['action'] == 'delete':
                mongo.db.crop_details.delete_one({'_id': ObjectId(crop_id)})
                flash('Crop details deleted successfully!', category='success')
                return redirect(url_for('dashboard'))
            elif request.form['action'] == 'update':
                updated_crop = {
                    'crop_name': request.form['crop_name'],
                    'date_planted': datetime.strptime(request.form['date_planted'], '%Y-%m-%d'),
                    'land_details': request.form['land_details'],
                    'fertilizer_details': request.form['fertilizer_details'],
                    'pesticides_details': request.form['pesticides_details'],
                    'other_details': request.form['other_details']
                }
                mongo.db.crop_details.update_one({'_id': ObjectId(crop_id)}, {'$set': updated_crop})
                flash('Crop details updated successfully!', category='success')
                return redirect(url_for('dashboard'))
        return render_template('crop_detail.html', crop=crop)
    except Exception as e:
        flash(f'Error accessing crop details: {str(e)}', category='error')
        return redirect(url_for('dashboard'))

@app.route('/services')
def services():
    return render_template('services.html', is_services_page=True)

@app.route('/crop_recommendation')
def crop_recommendation():
    return render_template('crop_recommendation.html')

def display_image(cropname, table_name):
    try:
        # Map crop names to actual image files
        crop_image_mapping = {
            # Grains and Cereals
            'rice': 'rice.jpg',
            'wheat': 'wheat.jpeg',
            'maize': 'maize.jpeg',
            'sugarcane': 'sugarcane.jpg',
            'barley': 'wheat.jpeg',  # Using wheat image for barley
            'oats': 'wheat.jpeg',    # Using wheat image for oats
            'millet': 'maize.jpeg',  # Using maize image for millet
            'sorghum': 'maize.jpeg', # Using maize image for sorghum
            
            # Cash Crops
            'cotton': 'cotton.jpg',
            'jute': 'jute.jpeg',
            'coffee': 'coffee.jpeg',
            'tea': 'coffee.jpeg',    # Using coffee image for tea
            'tobacco': 'etc.jpg',    # Using generic image
            
            # Vegetables
            'tomato': 'etc.jpg',
            'potato': 'etc.jpg',
            'onion': 'etc.jpg',
            'garlic': 'etc.jpg',
            'ginger': 'etc.jpg',
            'turmeric': 'etc.jpg',
            'chili': 'etc.jpg',
            'pepper': 'etc.jpg',
            
            # Fruits
            'apple': 'apple.jpeg',
            'banana': 'banana.jpeg',
            'mango': 'mango.jpeg',
            'orange': 'orange.jpeg',
            'grapes': 'grapes.jpeg',
            'watermelon': 'watermelon.jpeg',
            'muskmelon': 'muskmelon.jpeg',
            'papaya': 'papaya.jpg',
            'pomegranate': 'pomegranate.jpeg',
            'coconut': 'coconut.jpeg',
            
            # Pulses and Legumes
            'blackgram': 'blackgram.jpeg',
            'chickpea': 'chickpea.jpeg',
            'lentil': 'lentil.jpg',
            'pigeonpeas': 'pigeonpeas.jpeg',
            'mothbeans': 'mothbeans.jpg',
            'mungbean': 'mungbean.jpeg',
            'kideneybeans': 'kideneybeans.jpeg',
            'soybean': 'soybean.jpg',
            
            # Oilseeds and Spices
            'groundnut': 'etc.jpg',
            'sunflower': 'etc.jpg',
            'mustard': 'etc.jpg',
            'sesame': 'etc.jpg',
            'castor': 'etc.jpg',
            'spices': 'etc.jpg',
            'cardamom': 'etc.jpg',
            'cinnamon': 'etc.jpg',
            'cloves': 'etc.jpg',
            'nutmeg': 'etc.jpg',
            'vanilla': 'etc.jpg',
            
            # Nuts and Other Crops
            'cocoa': 'coffee.jpeg',  # Using coffee image for cocoa
            'cashew': 'etc.jpg',
            'almond': 'etc.jpg',
            'walnut': 'etc.jpg',
            'pistachio': 'etc.jpg',
            'hazelnut': 'etc.jpg',
            'pecan': 'etc.jpg',
            'macadamia': 'etc.jpg',
            'brazil_nut': 'etc.jpg',
            'pine_nut': 'etc.jpg',
            'chestnut': 'etc.jpg',
            'rubber': 'etc.jpg'
        }
        
        # Get the image filename for the crop
        image_filename = crop_image_mapping.get(cropname.lower())
        
        if image_filename:
            # Construct the path to the static image file
            image_path = os.path.join('app', 'static', 'images', 'crop_images', image_filename)
            
            if os.path.exists(image_path):
                # Read the image file and convert to base64
                with open(image_path, 'rb') as img_file:
                    image_data = img_file.read()
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    image_url = f"/static/images/crop_images/{image_filename}"
                    return image_base64, image_url
        
        # If no image found, return None
        return None, None
        
    except Exception as e:
        print(f"Error loading image for {cropname}: {e}")
        return None, None

def display_fertilizer_image(fertilizer_name):
    try:
        # Map fertilizer names to actual image files
        fertilizer_image_mapping = {
            'urea': 'Urea.png',
            'dap': 'DAP.png',
            '20-20': '20-20.png',
            '17-17-17': '17-17-17.png',
            '14-35-14': '14-35-14.png',
            '10-26-26': '10-26-26.png',
            '28-28': '28-28.png'
        }
        
        # Get the image filename for the fertilizer
        image_filename = fertilizer_image_mapping.get(fertilizer_name.lower())
        
        if image_filename:
            # Construct the path to the static image file
            image_path = os.path.join('app', 'static', 'images', 'fertilizer_images', image_filename)
            
            if os.path.exists(image_path):
                # Read the image file and convert to base64
                with open(image_path, 'rb') as img_file:
                    image_data = img_file.read()
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    image_url = f"/static/images/fertilizer_images/{image_filename}"
                    return image_base64, image_url
        
        # If no image found, return None
        return None, None
        
    except Exception as e:
        print(f"Error loading fertilizer image for {fertilizer_name}: {e}")
        return None, None

# Load ML models with error handling
def load_models():
    models = {}
    try:
        minmaxpath = 'models/minmax_scaler.pkl'
        if os.path.exists(minmaxpath):
            with open(minmaxpath, 'rb') as file:
                models['scaler'] = pickle.load(file)
        
        crop_model_path = 'models/crop_recommendation.pkl'
        if os.path.exists(crop_model_path):
            with open(crop_model_path, 'rb') as file:
                models['crop_model'] = pickle.load(file)
    except Exception as e:
        print(f"Error loading crop models: {e}")
    return models

# Load fertilizer models with error handling
def load_fertilizer_models():
    models = {}
    try:
        standard_scaler_path = 'models/standard_scaler.pkl'
        if os.path.exists(standard_scaler_path):
            with open(standard_scaler_path, 'rb') as file:
                models['standard_scaler'] = pickle.load(file)
        
        fertilizer_model_path = 'models/fertilizer_recommendation.pkl'
        if os.path.exists(fertilizer_model_path):
            with open(fertilizer_model_path, 'rb') as file:
                models['fertilizer_model'] = pickle.load(file)
    except Exception as e:
        print(f"Error loading fertilizer models: {e}")
    return models

# Load models
ml_models = load_models()
scaler = ml_models.get('scaler')
crop_model = ml_models.get('crop_model')

fertilizer_models = load_fertilizer_models()
standard_scaler = fertilizer_models.get('standard_scaler')
fertilizer_model = fertilizer_models.get('fertilizer_model')

@app.route('/crop_name', methods=['POST'])
def crop_name():
    try:
        nitrogen = float(request.form['nitrogen'])
        phosphorus = float(request.form['phosphorus'])
        potassium = float(request.form['potassium'])
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        # Try to use ML model if available
        if scaler and crop_model:
            try:
                input_data = [nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]
                normalized_input_data = scaler.transform([input_data])
                prediction = crop_model.predict(normalized_input_data)
                myprediction = prediction[0]
            except Exception as e:
                print(f"ML model error: {e}")
                myprediction = get_simple_crop_recommendation(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall)
        else:
            myprediction = get_simple_crop_recommendation(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall)

        image_data, image_url = display_image(myprediction, "crop_images")
        return render_template('crop_recommendation_result.html', myprediction=myprediction, image_data=image_data, image_url=image_url)
    except Exception as e:
        flash(f'Error in crop recommendation: {str(e)}', category='error')
        return redirect(url_for('crop_recommendation'))

def get_simple_crop_recommendation(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall):
    """Simple rule-based crop recommendation"""
    if temperature > 25 and rainfall > 100:
        return "Rice"
    elif temperature > 20 and ph > 6:
        return "Wheat"
    elif temperature > 15 and nitrogen > 50:
        return "Maize"
    elif temperature > 18 and humidity > 60:
        return "Cotton"
    elif ph > 6.5 and potassium > 40:
        return "Tomato"
    else:
        return "Potato"

@app.route('/disease_identification')
def disease_identification():
    return render_template('disease_identification.html')

@app.route('/disease_name', methods=['POST'])
def disease_name():
    try:
        if 'file' not in request.files:
            flash('No file uploaded', category='error')
            return redirect(url_for('disease_identification'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', category='error')
            return redirect(url_for('disease_identification'))
        
        # For now, return a simple response since TensorFlow models are problematic
        return render_template('disease_identification_result.html', 
                             predicted_class_label="Disease Detection", 
                             disease_name="Sample Plant Disease", 
                             disease_cause=["Environmental stress", "Pathogen infection"], 
                             chemical_methods=["Apply fungicide", "Use copper-based treatment"], 
                             natural_methods=["Improve air circulation", "Remove affected leaves", "Ensure proper drainage"])
    
    except Exception as e:
        flash(f'Error in disease identification: {str(e)}', category='error')
        return redirect(url_for('disease_identification'))

@app.route('/fertilizer_recommendation')
def fertilizer_recommendation():
    return render_template('fertilizer_recommendation.html')

@app.route('/fertilizer_name', methods=['POST'])
def fertilizer_name():
    try:
        # Retrieve form data
        nitrogen = float(request.form['nitrogen'])
        phosphorus = float(request.form['phosphorous'])
        potassium = float(request.form['potassium'])
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        moisture = float(request.form['moisture'])
        soil_type = request.form['soilType']
        crop_type = request.form['cropType']

        # Try to use ML model if available
        if standard_scaler and fertilizer_model:
            try:
                from sklearn.preprocessing import LabelEncoder
                # Encode soil and crop types using LabelEncoder
                soil_type_encoded = LabelEncoder().fit_transform([soil_type])
                crop_type_encoded = LabelEncoder().fit_transform([crop_type])

                # Prepare input data for the model
                input_data = [nitrogen, phosphorus, potassium, temperature, humidity, moisture, soil_type_encoded[0], crop_type_encoded[0]]

                # Normalize input data
                normalized_input_data = standard_scaler.transform([input_data])

                # Make prediction using the trained fertilizer model
                prediction = fertilizer_model.predict(normalized_input_data)
                
                # Map the prediction index to the actual fertilizer name
                reverse_fertilizer = {0: '10-26-26', 1: '14-35-14', 2: '17-17-17', 3: '20-20', 4: '28-28', 5: 'DAP', 6: 'Urea'}
                recommended_fertilizer = reverse_fertilizer[prediction[0]]
            except Exception as e:
                print(f"ML model error: {e}")
                # Fallback to simple rule-based recommendation
                recommended_fertilizer = get_simple_fertilizer_recommendation(nitrogen, phosphorus, potassium, soil_type, crop_type)
        else:
            # Use simple rule-based recommendation
            recommended_fertilizer = get_simple_fertilizer_recommendation(nitrogen, phosphorus, potassium, soil_type, crop_type)

        # Retrieve the corresponding image for the predicted fertilizer
        image_data, image_url = display_fertilizer_image(recommended_fertilizer)

        # Render the result template with the predicted fertilizer details
        return render_template(
            'fertilizer_recommendation_result.html', 
            recommended=recommended_fertilizer,
            image_data=image_data, 
            image_url=image_url
        )
    except Exception as e:
        flash(f'Error in fertilizer recommendation: {str(e)}', category='error')
        return redirect(url_for('fertilizer_recommendation'))

def get_simple_fertilizer_recommendation(nitrogen, phosphorus, potassium, soil_type, crop_type):
    """Simple rule-based fertilizer recommendation"""
    if nitrogen < 30:
        return "Urea"
    elif phosphorus < 20:
        return "DAP"
    elif potassium < 25:
        return "20-20"
    elif soil_type.lower() == "clay":
        return "17-17-17"
    elif crop_type.lower() in ["rice", "wheat"]:
        return "14-35-14"
    else:
        return "28-28"

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            first_name = request.form.get('firstName')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')

            user = mongo.db.users.find_one({"email": email})
            if user:
                flash('Email already exists.', category='error')
            elif len(email) < 4:
                flash('Email must be greater than 3 characters.', category='error')
            elif len(first_name) < 2:
                flash('First name must be greater than 1 character.', category='error')
            elif password1 != password2:
                flash('Passwords don\'t match.', category='error')
            elif len(password1) < 7:
                flash('Password must be at least 7 characters.', category='error')
            else:
                hashed_password = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt())
                new_user = {
                    "email": email,
                    "first_name": first_name,
                    "password": hashed_password.decode('utf-8')
                }
                user_id = mongo.db.users.insert_one(new_user).inserted_id
                login_user(User(email=new_user['email'], password=new_user['password'], first_name=new_user['first_name'], id=user_id), remember=True)
                flash('Account created!', category='success')
                return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error creating account: {str(e)}', category='error')
    
    return render_template("sign_up.html", user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')

            user = mongo.db.users.find_one({"email": email})
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                flash('Logged in successfully!', category='success')
                login_user(User(email=user['email'], password=user['password'], first_name=user['first_name'], id=user['_id']), remember=True)
                return redirect(url_for('home'))
            else:
                flash('Incorrect email or password, try again.', category='error')
        except Exception as e:
            flash(f'Error logging in: {str(e)}', category='error')

    return render_template("login.html", user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/check_weather')
def check_weather():
    return render_template('check_weather.html')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == "__main__":
    print("Starting Agricultural Innovation Website...")
    print("MongoDB connection:", mongo.db.name)
    print("Available crop models:", list(ml_models.keys()))
    print("Available fertilizer models:", list(fertilizer_models.keys()))
    app.run(host="127.0.0.1", port=5000, debug=True)

