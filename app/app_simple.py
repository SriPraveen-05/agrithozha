import base64
import bcrypt
import io
import numpy as np
import pickle
import random
import re
import string
from flask import Flask, abort, flash, redirect,jsonify, render_template, request, session, url_for
from flask_cors import CORS
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from string import ascii_uppercase
from datetime import datetime
from bson.objectid import ObjectId

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
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(email=user_data['email'], password=user_data['password'], first_name=user_data['first_name'], id=user_data['_id'])
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
        crop_details = list(mongo.db.crop_details.find({'user_id': current_user.id}))
        return render_template('dashboard.html', crop_details=crop_details)
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
    return render_template('add_crop.html')

@app.route('/crop/<crop_id>', methods=['GET', 'POST'])
@login_required
def crop_detail(crop_id):
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

@app.route('/services')
def services():
    return render_template('services.html', is_services_page=True)

@app.route('/crop_recommendation')
def crop_recommendation():
    return render_template('crop_recommendation.html')

def display_image(cropname, table_name):
    image_data = None
    image_url = None
    image_record = mongo.db[table_name].find_one({'image_name': cropname})
    if image_record:
        image_data = image_record['image_data']
        image_url = image_record['image_url']
    image_base64 = base64.b64encode(image_data).decode('utf-8') if image_data else None
    return image_base64, image_url

# Simple crop recommendation without ML models
@app.route('/crop_name', methods=['POST'])
def crop_name():
    nitrogen = float(request.form['nitrogen'])
    phosphorus = float(request.form['phosphorus'])
    potassium = float(request.form['potassium'])
    temperature = float(request.form['temperature'])
    humidity = float(request.form['humidity'])
    ph = float(request.form['ph'])
    rainfall = float(request.form['rainfall'])

    # Simple rule-based recommendation
    if temperature > 25 and rainfall > 100:
        myprediction = "Rice"
    elif temperature > 20 and ph > 6:
        myprediction = "Wheat"
    elif temperature > 15 and nitrogen > 50:
        myprediction = "Maize"
    else:
        myprediction = "Tomato"

    image_data, image_url = display_image(myprediction, "crop_images")
    return render_template('crop_recommendation_result.html', myprediction=myprediction, image_data=image_data, image_url=image_url)

@app.route('/disease_identification')
def disease_identification():
    return render_template('disease_identification.html')

@app.route('/disease_name', methods=['POST'])
def disease_name():
    # Simple placeholder response
    return render_template('disease_identification_result.html', 
                         predicted_class_label="Disease Detection", 
                         disease_name="Sample Disease", 
                         disease_cause=["Environmental factors"], 
                         chemical_methods=["Use appropriate fungicide"], 
                         natural_methods=["Improve air circulation"])

@app.route('/fertilizer_recommendation')
def fertilizer_recommendation():
    return render_template('fertilizer_recommendation.html')

@app.route('/fertilizer_name', methods=['POST'])
def fertilizer_name():
    nitrogen = float(request.form['nitrogen'])
    phosphorus = float(request.form['phosphorous'])
    potassium = float(request.form['potassium'])
    temperature = float(request.form['temperature'])
    humidity = float(request.form['humidity'])
    moisture = float(request.form['moisture'])
    soil_type = request.form['soilType']
    crop_type = request.form['cropType']

    # Simple rule-based fertilizer recommendation
    if nitrogen < 30:
        recommended_fertilizer = "Urea"
    elif phosphorus < 20:
        recommended_fertilizer = "DAP"
    elif potassium < 25:
        recommended_fertilizer = "20-20"
    else:
        recommended_fertilizer = "17-17-17"

    image_data, image_url = display_image(recommended_fertilizer, "fertilizer_images")
    return render_template(
        'fertilizer_recommendation_result.html', 
        recommended=recommended_fertilizer,
        image_data=image_data, 
        image_url=image_url
    )

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
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
    
    return render_template("sign_up.html", user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = mongo.db.users.find_one({"email": email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            flash('Logged in successfully!', category='success')
            login_user(User(email=user['email'], password=user['password'], first_name=user['first_name'], id=user['_id']), remember=True)
            return redirect(url_for('home'))
        else:
            flash('Incorrect email or password, try again.', category='error')

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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
