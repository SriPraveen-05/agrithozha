import base64
import bcrypt
import io
import numpy as np
import pickle
import random
import re
import string
import pandas as pd
from flask import Flask, abort, flash, redirect, jsonify, render_template, request, session, url_for
from flask_cors import CORS
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from string import ascii_uppercase
from datetime import datetime
from bson.objectid import ObjectId
import os
from sklearn.preprocessing import LabelEncoder

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

# Global variables to store loaded models and data
ml_models = {}
crop_data = None
fertilizer_data = None

def load_ml_models():
    """Load all ML models and data"""
    global ml_models, crop_data, fertilizer_data
    
    try:
        # Load crop recommendation models
        minmax_path = 'models/minmax_scaler.pkl'
        if os.path.exists(minmax_path):
            with open(minmax_path, 'rb') as file:
                ml_models['crop_scaler'] = pickle.load(file)
                print("✅ Crop scaler loaded successfully")
        
        crop_model_path = 'models/crop_recommendation.pkl'
        if os.path.exists(crop_model_path):
            with open(crop_model_path, 'rb') as file:
                ml_models['crop_model'] = pickle.load(file)
                print("✅ Crop model loaded successfully")
        
        # Load fertilizer recommendation models
        standard_scaler_path = 'models/standard_scaler.pkl'
        if os.path.exists(standard_scaler_path):
            with open(standard_scaler_path, 'rb') as file:
                ml_models['fertilizer_scaler'] = pickle.load(file)
                print("✅ Fertilizer scaler loaded successfully")
        
        fertilizer_model_path = 'models/fertilizer_recommendation.pkl'
        if os.path.exists(fertilizer_model_path):
            with open(fertilizer_model_path, 'rb') as file:
                ml_models['fertilizer_model'] = pickle.load(file)
                print("✅ Fertilizer model loaded successfully")
        
        # Load CSV data for analysis and display
        crop_csv_path = 'data/raw/crop_recommendation.csv'
        if os.path.exists(crop_csv_path):
            crop_data = pd.read_csv(crop_csv_path)
            print(f"✅ Crop data loaded: {len(crop_data)} records")
        
        fertilizer_csv_path = 'data/raw/fertilizer_recommendation.csv'
        if os.path.exists(fertilizer_csv_path):
            fertilizer_data = pd.read_csv(fertilizer_csv_path)
            print(f"✅ Fertilizer data loaded: {len(fertilizer_data)} records")
            
    except Exception as e:
        print(f"❌ Error loading models: {e}")

def get_crop_statistics():
    """Get statistics about crops from the dataset"""
    if crop_data is not None:
        crop_counts = crop_data['label'].value_counts()
        return {
            'total_crops': len(crop_data),
            'unique_crops': len(crop_counts),
            'top_crops': crop_counts.head(10).to_dict(),
            'avg_temperature': crop_data['temperature'].mean(),
            'avg_humidity': crop_data['humidity'].mean(),
            'avg_ph': crop_data['ph'].mean(),
            'avg_rainfall': crop_data['rainfall'].mean()
        }
    return None

def get_fertilizer_statistics():
    """Get statistics about fertilizers from the dataset"""
    if fertilizer_data is not None:
        fertilizer_counts = fertilizer_data['Fertilizer Name'].value_counts()
        soil_type_counts = fertilizer_data['Soil Type'].value_counts()
        crop_type_counts = fertilizer_data['Crop Type'].value_counts()
        return {
            'total_fertilizers': len(fertilizer_data),
            'unique_fertilizers': len(fertilizer_counts),
            'fertilizer_distribution': fertilizer_counts.to_dict(),
            'soil_type_distribution': soil_type_counts.to_dict(),
            'crop_type_distribution': crop_type_counts.to_dict(),
            'avg_temperature': fertilizer_data['Temparature'].mean(),
            'avg_humidity': fertilizer_data['Humidity '].mean(),
            'avg_moisture': fertilizer_data['Moisture'].mean()
        }
    return None

@app.route('/')
def home():
    return render_template('home_modern.html')

@app.route('/classic')
def home_classic():
    return render_template('home.html')

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

@app.route('/data_analysis')
def data_analysis():
    """New route to display data analysis and statistics"""
    crop_stats = get_crop_statistics()
    fertilizer_stats = get_fertilizer_statistics()
    
    return render_template('data_analysis.html', 
                         crop_stats=crop_stats, 
                         fertilizer_stats=fertilizer_stats)

@app.route('/crop_recommendation')
def crop_recommendation():
    return render_template('crop_recommendation_modern.html')

@app.route('/crop_recommendation_classic')
def crop_recommendation_classic():
    return render_template('crop_recommendation.html')

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
        if 'crop_scaler' in ml_models and 'crop_model' in ml_models:
            try:
                input_data = [nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]
                normalized_input_data = ml_models['crop_scaler'].transform([input_data])
                prediction = ml_models['crop_model'].predict(normalized_input_data)
                myprediction = prediction[0]
                confidence = "High (ML Model)"
            except Exception as e:
                print(f"ML model error: {e}")
                myprediction = get_simple_crop_recommendation(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall)
                confidence = "Medium (Rule-based)"
        else:
            myprediction = get_simple_crop_recommendation(nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall)
            confidence = "Medium (Rule-based)"

        # Get additional crop information
        crop_info = get_crop_information(myprediction)
        
        return render_template('crop_recommendation_result.html', 
                             myprediction=myprediction, 
                             confidence=confidence,
                             crop_info=crop_info)
    except Exception as e:
        flash(f'Error in crop recommendation: {str(e)}', category='error')
        return redirect(url_for('crop_recommendation'))

def get_crop_information(crop_name):
    """Get detailed information about a crop from the dataset"""
    if crop_data is not None:
        crop_data_filtered = crop_data[crop_data['label'] == crop_name.lower()]
        if not crop_data_filtered.empty:
            return {
                'avg_nitrogen': crop_data_filtered['N'].mean(),
                'avg_phosphorus': crop_data_filtered['P'].mean(),
                'avg_potassium': crop_data_filtered['K'].mean(),
                'avg_temperature': crop_data_filtered['temperature'].mean(),
                'avg_humidity': crop_data_filtered['humidity'].mean(),
                'avg_ph': crop_data_filtered['ph'].mean(),
                'avg_rainfall': crop_data_filtered['rainfall'].mean(),
                'sample_count': len(crop_data_filtered)
            }
    return None

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

@app.route('/fertilizer_recommendation')
def fertilizer_recommendation():
    return render_template('fertilizer_recommendation.html')

@app.route('/fertilizer_name', methods=['POST'])
def fertilizer_name():
    try:
        nitrogen = float(request.form['nitrogen'])
        phosphorus = float(request.form['phosphorous'])
        potassium = float(request.form['potassium'])
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        moisture = float(request.form['moisture'])
        soil_type = request.form['soilType']
        crop_type = request.form['cropType']

        # Try to use ML model if available
        if 'fertilizer_scaler' in ml_models and 'fertilizer_model' in ml_models:
            try:
                # Encode categorical variables
                soil_type_encoded = LabelEncoder().fit_transform([soil_type])[0]
                crop_type_encoded = LabelEncoder().fit_transform([crop_type])[0]
                
                input_data = [nitrogen, phosphorus, potassium, temperature, humidity, moisture, soil_type_encoded, crop_type_encoded]
                normalized_input_data = ml_models['fertilizer_scaler'].transform([input_data])
                prediction = ml_models['fertilizer_model'].predict(normalized_input_data)
                
                reverse_fertilizer = {0: '10-26-26', 1: '14-35-14', 2: '17-17-17', 3: '20-20', 4: '28-28', 5: 'DAP', 6: 'Urea'}
                recommended_fertilizer = reverse_fertilizer[prediction[0]]
                confidence = "High (ML Model)"
            except Exception as e:
                print(f"ML model error: {e}")
                recommended_fertilizer = get_simple_fertilizer_recommendation(nitrogen, phosphorus, potassium, soil_type, crop_type)
                confidence = "Medium (Rule-based)"
        else:
            recommended_fertilizer = get_simple_fertilizer_recommendation(nitrogen, phosphorus, potassium, soil_type, crop_type)
            confidence = "Medium (Rule-based)"

        # Get additional fertilizer information
        fertilizer_info = get_fertilizer_information(recommended_fertilizer)
        
        return render_template('fertilizer_recommendation_result.html', 
                             recommended=recommended_fertilizer,
                             confidence=confidence,
                             fertilizer_info=fertilizer_info)
    except Exception as e:
        flash(f'Error in fertilizer recommendation: {str(e)}', category='error')
        return redirect(url_for('fertilizer_recommendation'))

def get_fertilizer_information(fertilizer_name):
    """Get detailed information about a fertilizer from the dataset"""
    if fertilizer_data is not None:
        fertilizer_data_filtered = fertilizer_data[fertilizer_data['Fertilizer Name'] == fertilizer_name]
        if not fertilizer_data_filtered.empty:
            return {
                'avg_temperature': fertilizer_data_filtered['Temparature'].mean(),
                'avg_humidity': fertilizer_data_filtered['Humidity '].mean(),
                'avg_moisture': fertilizer_data_filtered['Moisture'].mean(),
                'common_soil_types': fertilizer_data_filtered['Soil Type'].value_counts().head(3).to_dict(),
                'common_crop_types': fertilizer_data_filtered['Crop Type'].value_counts().head(3).to_dict(),
                'sample_count': len(fertilizer_data_filtered)
            }
    return None

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

@app.route('/api/crop_data')
def api_crop_data():
    """API endpoint to get crop data as JSON"""
    if crop_data is not None:
        return jsonify({
            'data': crop_data.head(100).to_dict('records'),
            'columns': list(crop_data.columns),
            'total_records': len(crop_data)
        })
    return jsonify({'error': 'No crop data available'})

@app.route('/api/fertilizer_data')
def api_fertilizer_data():
    """API endpoint to get fertilizer data as JSON"""
    if fertilizer_data is not None:
        return jsonify({
            'data': fertilizer_data.head(100).to_dict('records'),
            'columns': list(fertilizer_data.columns),
            'total_records': len(fertilizer_data)
        })
    return jsonify({'error': 'No fertilizer data available'})

# ... (rest of the routes remain the same)
@app.route('/connect_home')
def connect_home():
    return render_template('connect_home.html')

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
        
        # Simple response for now
        return render_template('disease_identification_result.html', 
                             predicted_class_label="Disease Detection", 
                             disease_name="Sample Plant Disease", 
                             disease_cause=["Environmental stress", "Pathogen infection"], 
                             chemical_methods=["Apply fungicide", "Use copper-based treatment"], 
                             natural_methods=["Improve air circulation", "Remove affected leaves", "Ensure proper drainage"])
    
    except Exception as e:
        flash(f'Error in disease identification: {str(e)}', category='error')
        return redirect(url_for('disease_identification'))

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
    print("🚀 Starting Agricultural Innovation Website...")
    print("📊 Loading ML models and data...")
    
    # Load models and data
    load_ml_models()
    
    print("🔗 MongoDB connection:", mongo.db.name)
    print("🤖 Available models:", list(ml_models.keys()))
    print("📈 Data loaded successfully!")
    print("🌐 Website running at: http://127.0.0.1:5000")
    
    app.run(host="127.0.0.1", port=5000, debug=True)
