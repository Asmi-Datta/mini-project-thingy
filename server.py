import json
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, Response, jsonify
from flask_cors import CORS
from scripts import the_big_dipper
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

load_dotenv()
app = Flask(__name__)
CORS(app)

# Directory where your resource text files are stored
RESOURCES_DIR = "static/resources"
df = pd.read_csv("static/assets/facebook_dream_archetypes.csv")
dream_text = ""
selected_archetype = ""

# Custom JSON encoder to handle NumPy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

# Configure Flask to use the custom encoder
app.json_encoder = NumpyEncoder

def json_listify(data: dict) -> str:
    spam = []
    for key in data:
        d = {}
        d["_id_"] = key
        d["_text_"] = data[key]
        spam.append(d)
    return json.dumps(spam)

# Keep track of submitted dreams and their archetypes
dream_history = []


# Generate time series data for archetypes
def generate_time_series_data():
    archetypes = ['explorer', 'everyman', 'hero', 'outlaw', 'sage']
    end_date = datetime.now()
    
    # Generate dates for the past 6 months
    dates = [(end_date - timedelta(days=i*30)).strftime('%Y-%m') for i in range(6)]
    dates.reverse()  # Chronological order
    
    data = []
    for archetype in archetypes:
        # Generate somewhat smooth trend with some randomness
        base_value = np.random.randint(5, 15)
        trend = np.random.choice([-1, 0, 1])  # Trend direction
        values = []
        
        for i in range(len(dates)):
            # Value changes with some trend and randomness
            val = max(1, base_value + trend * i + np.random.randint(-3, 4))
            # Convert NumPy int64 to regular Python int
            val = int(val)
            values.append(val)
        
        data.append({
            'archetype': archetype,
            'values': values
        })
    
    return {
        'dates': dates,
        'data': data
    }

# Calculate rarity score based on archetype distribution
def calculate_rarity_score(archetype):
    # Rarity is inversely proportional to frequency
    # higher the number here, more common it is
    archetype_weights = {
        'explorer': 0.3,
        'everyman': 1,
        'hero': 0.15,
        'outlaw': 0.1,
        'sage': 0.1,
        'creator': 0.1,
        'caregiver': 0.5,
        'lover': 0.7
    }
    
    # Calculate base rarity (rare archetypes = high score)
    base_rarity = 100 - (archetype_weights.get(archetype, 0.5) * 100)
    
    # Add some randomness for variability
    randomness = np.random.normal(0, 10)
    
    # Ensure score is between 0 and 100
    score = max(0, min(100, base_rarity + randomness))
    
    # Convert to native Python float
    score = float(round(score, 1))
    
    return score

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# Process dream text and return interpretation
@app.route("/llm", methods=["POST"])
def llm_():
    global dream_text
    global selected_archetype
    
    if request.method == "POST":
        dream_text = request.form["dream"]

    data = the_big_dipper.main(dream_text=dream_text)
    # data = {
    #     "archetype": "everyman",
    #     "descriptive_content": {
    #         "title": "nope",
    #         "content": "please kys"
    #     }
    # }
    selected_archetype = data['archetype']
    # Store the dream and archetype for history
    if "archetype" in data:
        dream_history.append({
            "dream": dream_text,
            "archetype": data["archetype"],
            "timestamp": datetime.now().isoformat()
        })
    
    response = Response(json_listify(data), mimetype="application/json")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

# Visualization API endpoints
@app.route('/get_bar_data')
def get_bar_data():
    # Convert to the format expected by Chart.js
    counts = df['archetype'].value_counts()
    
    # Convert NumPy types to native Python types
    data = {
        'labels': counts.index.tolist(),
        'values': [int(val) for val in counts.values.tolist()]
    }
    
    return jsonify(data)

@app.route('/get_doughnut_data')
def get_doughnut_data():
    __v__ = the_big_dipper.vector_store_reader(
        load_dir_path="scripts/pickles",
        store_names=["facebook_dream_archetypes_store.dat"],
        use_cpu=int(os.getenv("USE_CPU", "1")),
    )
    
    results = __v__.vector_store["facebook_dream_archetypes_store"].similarity_search(dream_text)
    
    # Convert to the format expected by Chart.js
    counts = pd.Series([df.loc[_.metadata["row"]]["archetype"] for _ in results]).value_counts()
    
    # Convert NumPy types to native Python types
    data = {
        'labels': counts.index.tolist(),
        'values': [int(val) for val in counts.values.tolist()]
    }
    
    return jsonify(data)

@app.route('/get_time_series_data')
def get_time_series_data():
    time_data = generate_time_series_data()
    return jsonify(time_data)

@app.route('/get_rarity_score')
def get_rarity_score():
    score = calculate_rarity_score(selected_archetype)
    
    return jsonify({
        'score': score,
        'archetype': selected_archetype
    })

@app.route('/get_resources/<archetype>')
def get_resources(archetype):
    """
    Load resources for a specific archetype from text files.
    Each archetype should have a JSON file in the resources directory.
    Falls back to default resources if the file doesn't exist.
    """
    try:
        # Sanitize the archetype name to prevent directory traversal
        archetype = os.path.basename(archetype.lower())
        
        # Path to the archetype's resource file
        resource_file = os.path.join(RESOURCES_DIR, f"{archetype}.json")
        
        # Check if the file exists
        if os.path.exists(resource_file):
            with open(resource_file, 'r') as f:
                resources = json.load(f)
        else:
            # Load default resources if archetype-specific file doesn't exist
            default_file = os.path.join(RESOURCES_DIR, "default.json")
            with open(default_file, 'r') as f:
                resources = json.load(f)
        
        print("sent reading notes...")
        return jsonify(resources)
    
    except Exception as e:
        print(f"Error loading resources: {e}")
        # Return default resources as fallback
        default_resources = [
            {
                "title": "Understanding Jungian Archetypes",
                "description": "An introduction to Carl Jung's theory of archetypes and their significance in dream interpretation.",
                "links": [
                    {"type": "Article", "url": "https://conorneill.com/2018/04/21/understanding-personality-the-12-jungian-archetypes/"},
                ]
            },
            {
                "title": "Dream Symbolism Dictionary",
                "description": "Comprehensive guide to common dream symbols and their potential meanings across cultures.",
                "links": [
                    {"type": "Reference", "url": "https://www.dreamdictionary.org/"}
                ]
            }
        ]
        return jsonify(default_resources)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
