# Agricultural Innovation Website

A comprehensive Flask-based web application for agricultural services including crop recommendation, disease identification, fertilizer recommendation, and weather checking.

## Features

- **Crop Recommendation**: ML-based crop recommendation based on soil and weather conditions
- **Disease Identification**: AI-powered plant disease detection from images
- **Fertilizer Recommendation**: Smart fertilizer suggestions based on soil analysis
- **Weather Checking**: Weather information for agricultural planning
- **User Management**: User registration, login, and dashboard
- **Crop Management**: Add, update, and track crop details
- **Real-time Chat**: SocketIO-based chat functionality
- **Responsive Design**: Modern UI with CSS styling

## Prerequisites

Before running the application, ensure you have the following installed:

1. **Python 3.8+**
2. **MongoDB** (Community Server)
3. **Git** (optional, for cloning)

## Installation & Setup

### 1. Clone or Download the Project
```bash
# If using git
git clone <repository-url>
cd agri-innovative

# Or extract the downloaded zip file
```

### 2. Install Python Dependencies
```bash
# Navigate to the project directory
cd agri-innovative

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. MongoDB Setup

#### Option A: Install MongoDB Locally
1. Download MongoDB Community Server from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Install and start MongoDB service
3. Default connection: `mongodb://localhost:27017`

#### Option B: Use MongoDB Atlas (Cloud)
1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a cluster and get connection string
3. Update the connection string in `app.py` (line 29)

### 4. Database Setup
The application will automatically create the required database (`agritest`) and collections when you first run it.

## Running the Application

### 1. Start MongoDB (if using local installation)
```bash
# On Windows (if MongoDB is installed as a service, it should start automatically)
# Or manually start:
mongod

# On macOS (using Homebrew):
brew services start mongodb-community

# On Linux:
sudo systemctl start mongod
```

### 2. Run the Flask Application
```bash
# Make sure you're in the agri-innovative directory
cd agri-innovative

# Activate virtual environment (if not already activated)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Run the application
python app/app.py
```

### 3. Access the Website
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

## Application Structure

```
agri-innovative/
├── app/
│   ├── app.py                 # Main Flask application
│   ├── models/               # ML model files (.pkl, .h5)
│   ├── static/              # CSS, JS, and image files
│   ├── templates/           # HTML templates
│   └── utils/               # Utility functions
├── data/                    # Raw data files
├── models/                  # Additional model files
├── notebooks/               # Jupyter notebooks for model training
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Key Features Explained

### 1. Crop Recommendation
- Input: Nitrogen, Phosphorus, Potassium, Temperature, Humidity, pH, Rainfall
- Output: Recommended crop with image and details
- Uses trained ML model for predictions

### 2. Disease Identification
- Upload plant leaf images
- AI model identifies diseases and provides treatment recommendations
- Supports multiple plant types and diseases

### 3. Fertilizer Recommendation
- Input: Soil nutrients, weather conditions, soil type, crop type
- Output: Recommended fertilizer with dosage information
- Uses machine learning for accurate recommendations

### 4. User Dashboard
- Register/Login functionality
- Add and manage crop details
- Track planting dates and agricultural activities

## Troubleshooting

### Common Issues:

1. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check connection string in `app.py`
   - Verify MongoDB service is started

2. **Module Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility (3.8+)

3. **Model Loading Errors**
   - Ensure model files exist in `app/models/` directory
   - Check file permissions

4. **Port Already in Use**
   - Change port in `app.py` (line 352): `app.run(host="127.0.0.1", port=5001)`
   - Or kill the process using port 5000

### Performance Tips:
- Use a virtual environment to avoid dependency conflicts
- Ensure sufficient RAM for TensorFlow models
- Use SSD storage for better model loading performance

## Development

### Adding New Features:
1. Add new routes in `app.py`
2. Create corresponding HTML templates in `templates/`
3. Add CSS styling in `static/css/`
4. Update navigation in layout templates

### Model Updates:
1. Train new models using Jupyter notebooks in `notebooks/`
2. Save models in `app/models/` directory
3. Update model loading code in `app.py`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure MongoDB is running and accessible
4. Check console output for specific error messages

## License

This project is for educational and agricultural innovation purposes.
