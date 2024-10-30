from flask import Flask, request, render_template_string, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key="newsectret"
# Define target nutrient levels for optimal crop yield
TARGET_NUTRIENTS = {'N': 100, 'P': 60, 'K': 80, 'S': 50}  # Target levels in ppm or mg/kg
FERTILIZER_COSTS = {'N': 0.5, 'P': 0.7, 'K': 0.6, 'S': 0.4}  # Cost per kg of fertilizer
FERTILIZER_EFFICIENCIES = {'N': 0.8, 'P': 0.75, 'K': 0.7, 'S': 0.65}  # Efficiency of fertilizers
FERTILIZER_NAMES = {
    'N': ['Urea', 'Ammonium Nitrate', 'Ammonium Sulfate', 'Calcium Nitrate', 'Sulfate of Ammonia',
          'AN+Urea', 'UAN', 'N-P-K', 'NPK 10-10-10', 'NPK 20-20-20'],
    'P': ['Superphosphate', 'Triple Superphosphate', 'Monoammonium Phosphate', 'Diammonium Phosphate',
          'Rock Phosphate', 'Bone Meal', 'Poultry Manure', 'Fish Emulsion', 'Humic Acid', 'Bat Guano'],
    'K': ['Potassium Chloride', 'Potassium Sulfate', 'Potassium Nitrate', 'Sul-Po-Mag', 'Potash',
          'K-Mag', 'Muriate of Potash', 'Sulfate of Potash', 'KCl', 'K2SO4'],
    'S': ['Gypsum', 'Elemental Sulfur', 'Calcium Sulfate', 'Ammonium Sulfate', 'Sulfate of Potash',
          'Thiobacillus', 'Magnesium Sulfate', 'Potassium Sulfate', 'Sulfur-Coated Urea', 'Sulfur Dust']
}

# Expanded crop nutrient requirements
CROP_REQUIREMENTS = {
    'Wheat': {'N': 80, 'P': 40, 'K': 60, 'S': 40},
    'Corn': {'N': 120, 'P': 50, 'K': 100, 'S': 50},
    'Rice': {'N': 150, 'P': 60, 'K': 80, 'S': 30},
    'Soybean': {'N': 90, 'P': 40, 'K': 70, 'S': 40},
    'Cabbage': {'N': 35, 'P': 20, 'K': 30, 'S': 25},
    'Beetroot': {'N': 30, 'P': 25, 'K': 35, 'S': 20},
    'Radish': {'N': 25, 'P': 15, 'K': 30, 'S': 20},
    'Spinach': {'N': 40, 'P': 25, 'K': 30, 'S': 20},
    'Lettuce': {'N': 30, 'P': 20, 'K': 25, 'S': 15},
    'Turnip': {'N': 20, 'P': 15, 'K': 30, 'S': 20},
    'Arugula': {'N': 35, 'P': 20, 'K': 30, 'S': 25},
    'Kale': {'N': 35, 'P': 20, 'K': 30, 'S': 25},
    'Swiss Chard': {'N': 30, 'P': 20, 'K': 30, 'S': 20},
    'Mustard Greens': {'N': 30, 'P': 15, 'K': 25, 'S': 20},
    'Pak Choi': {'N': 30, 'P': 20, 'K': 25, 'S': 15},
    'Collard Greens': {'N': 35, 'P': 20, 'K': 30, 'S': 25},
    'Celery': {'N': 30, 'P': 15, 'K': 25, 'S': 20},
    'Chard': {'N': 30, 'P': 20, 'K': 30, 'S': 15},
    'Barley': {'N': 70, 'P': 30, 'K': 50, 'S': 30},
    'Oats': {'N': 80, 'P': 35, 'K': 60, 'S': 35},
    'Potato': {'N': 120, 'P': 50, 'K': 100, 'S': 40},
    'Tomato': {'N': 100, 'P': 45, 'K': 90, 'S': 50},
    'Barley': {'N': 90, 'P': 35, 'K': 65, 'S': 45},
    'Oats': {'N': 85, 'P': 45, 'K': 55, 'S': 40},
    'Rye': {'N': 70, 'P': 25, 'K': 50, 'S': 30},
    'Canola': {'N': 100, 'P': 50, 'K': 90, 'S': 50},
    'Sunflower': {'N': 110, 'P': 55, 'K': 70, 'S': 55},
    'Potato': {'N': 120, 'P': 70, 'K': 100, 'S': 60},
    'Tomato': {'N': 130, 'P': 60, 'K': 110, 'S': 65},
    'Lettuce': {'N': 70, 'P': 30, 'K': 40, 'S': 25},
    'Carrot': {'N': 80, 'P': 40, 'K': 50, 'S': 30},
    'Cucumber': {'N': 90, 'P': 45, 'K': 60, 'S': 35},
    'Pea': {'N': 60, 'P': 25, 'K': 45, 'S': 20},
    'Bean': {'N': 65, 'P': 35, 'K': 55, 'S': 25},
    'Squash': {'N': 100, 'P': 50, 'K': 75, 'S': 50},
    'Pumpkin': {'N': 110, 'P': 55, 'K': 80, 'S': 55},
    'Bell Pepper': {'N': 120, 'P': 60, 'K': 85, 'S': 60},
    'Broccoli': {'N': 90, 'P': 45, 'K': 70, 'S': 45},
    'Cauliflower': {'N': 95, 'P': 50, 'K': 75, 'S': 50},
    'Spinach': {'N': 80, 'P': 35, 'K': 55, 'S': 30},
    'Kale': {'N': 85, 'P': 40, 'K': 60, 'S': 35},
    'Onion': {'N': 70, 'P': 30, 'K': 50, 'S': 30},
    'Garlic': {'N': 75, 'P': 35, 'K': 55, 'S': 35},
    'Radish': {'N': 60, 'P': 25, 'K': 40, 'S': 25},
    'Beet': {'N': 80, 'P': 40, 'K': 50, 'S': 30},
    'Sweet Corn': {'N': 115, 'P': 55, 'K': 95, 'S': 50},
    'Grape': {'N': 110, 'P': 50, 'K': 85, 'S': 45},
    'Apple': {'N': 100, 'P': 45, 'K': 70, 'S': 40},
    'Pear': {'N': 95, 'P': 40, 'K': 65, 'S': 35},
    'Peach': {'N': 105, 'P': 50, 'K': 80, 'S': 45},
    'Cherry': {'N': 100, 'P': 45, 'K': 75, 'S': 40},
    'Plum': {'N': 90, 'P': 40, 'K': 70, 'S': 35},
    'Apricot': {'N': 85, 'P': 35, 'K': 65, 'S': 30},
    'Strawberry': {'N': 70, 'P': 30, 'K': 55, 'S': 25},
    'Blueberry': {'N': 80, 'P': 35, 'K': 60, 'S': 30},
    'Raspberry': {'N': 75, 'P': 30, 'K': 55, 'S': 25},
    'Blackberry': {'N': 80, 'P': 35, 'K': 60, 'S': 30},
    'Fig': {'N': 85, 'P': 40, 'K': 65, 'S': 35},
    'Olive': {'N': 90, 'P': 45, 'K': 70, 'S': 40},
    'Almond': {'N': 100, 'P': 50, 'K': 80, 'S': 45},
    'Walnut': {'N': 110, 'P': 55, 'K': 85, 'S': 50},
    'Pecan': {'N': 120, 'P': 60, 'K': 90, 'S': 55},
    'Chestnut': {'N': 110, 'P': 50, 'K': 85, 'S': 50},
    'Hazelnut': {'N': 100, 'P': 45, 'K': 80, 'S': 45},
    'Macadamia': {'N': 95, 'P': 40, 'K': 75, 'S': 40},
    'Cashew': {'N': 90, 'P': 35, 'K': 70, 'S': 35},
    'Pistachio': {'N': 105, 'P': 50, 'K': 85, 'S': 45},
    'Coconut': {'N': 120, 'P': 60, 'K': 95, 'S': 55},
    'Avocado': {'N': 110, 'P': 55, 'K': 90, 'S': 50},
    'Mango': {'N': 115, 'P': 60, 'K': 95, 'S': 55},
    'Papaya': {'N': 105, 'P': 55, 'K': 85, 'S': 50},
    'Banana': {'N': 120, 'P': 60, 'K': 100, 'S': 55},
    'Date': {'N': 115, 'P': 55, 'K': 90, 'S': 50},
    'Guava': {'N': 110, 'P': 55, 'K': 90, 'S': 50},
    'Passion Fruit': {'N': 105, 'P': 50, 'K': 85, 'S': 45},
    'Kiwi': {'N': 120, 'P': 60, 'K': 100, 'S': 55},
    'Dragon Fruit': {'N': 115, 'P': 55, 'K': 95, 'S': 50},
    'Ginger': {'N': 80, 'P': 40, 'K': 60, 'S': 30},
    'Turmeric': {'N': 85, 'P': 45, 'K': 65, 'S': 35},
    'Cabbage': {'N': 35, 'P': 20, 'K': 30, 'S': 25},
    'Beetroot': {'N': 30, 'P': 25, 'K': 35, 'S': 20},
    'Radish': {'N': 25, 'P': 15, 'K': 30, 'S': 20},
    'Spinach': {'N': 40, 'P': 25, 'K': 30, 'S': 20},
    'Lettuce': {'N': 30, 'P': 20, 'K': 25, 'S': 15},
    'Turnip': {'N': 20, 'P': 15, 'K': 30, 'S': 20},
    'Arugula': {'N': 35, 'P': 20, 'K': 30, 'S': 25},
    'Kale': {'N': 35, 'P': 20, 'K': 30, 'S': 25},
    'Swiss Chard': {'N': 30, 'P': 20, 'K': 30, 'S': 20},
    'Mustard Greens': {'N': 30, 'P': 15, 'K': 25, 'S': 20},
    'Pak Choi': {'N': 30, 'P': 20, 'K': 25, 'S': 15},
    'Collard Greens': {'N': 35, 'P': 20, 'K': 30, 'S': 25},
    'Celery': {'N': 30, 'P': 15, 'K': 25, 'S': 20},
    'Chard': {'N': 30, 'P': 20, 'K': 30, 'S': 15},
    'Endive': {'N': 25, 'P': 15, 'K': 20, 'S': 15}
    # Add more crops as needed
}


def calculate_fertilizer_need(soil_data):
    """Calculate the amount of fertilizer needed to reach target nutrient levels."""
    for nutrient in TARGET_NUTRIENTS:
        if nutrient in soil_data.columns:
            soil_data[f'{nutrient}_deficit'] = TARGET_NUTRIENTS[nutrient] - soil_data[nutrient]
        else:
            soil_data[f'{nutrient}_deficit'] = TARGET_NUTRIENTS[nutrient]

        # Ensure deficit cannot be negative
        soil_data[f'{nutrient}_deficit'] = soil_data[f'{nutrient}_deficit'].clip(lower=0)

        # Adjust for fertilizer efficiency
        soil_data[f'{nutrient}_amount_needed'] = soil_data[f'{nutrient}_deficit'] / FERTILIZER_EFFICIENCIES[nutrient]

        # Calculate cost based on amount needed
        soil_data[f'{nutrient}_cost'] = soil_data[f'{nutrient}_amount_needed'] * FERTILIZER_COSTS[nutrient]

    # Total cost and maximum amount of fertilizer needed
    soil_data['Total_cost'] = soil_data[[f'{nutrient}_cost' for nutrient in TARGET_NUTRIENTS]].sum(axis=1)
    soil_data['Total_fertilizer_amount'] = soil_data[
        [f'{nutrient}_amount_needed' for nutrient in TARGET_NUTRIENTS]].sum(axis=1)

    return soil_data


def recommend_crops(soil_data):
    """Recommend crops based on soil nutrient levels."""

    def crop_recommendation(row):
        recommendations = []
        for crop, requirements in CROP_REQUIREMENTS.items():
            if all(row[nutrient] >= requirements[nutrient] for nutrient in requirements):
                recommendations.append(crop)
        return ', '.join(recommendations)

    soil_data['Recommended_crops'] = soil_data.apply(crop_recommendation, axis=1)
    return soil_data


HTML_LOGIN = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container">
        <h1 class="mt-4">Login</h1>
        <form action="/login" method="post">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" class="form-control" placeholder="Username" required>
            </div>
            <div class="form-group">
                <label for="mobile">Mobile Number:</label>
                <input type="text" id="mobile" name="mobile" class="form-control" placeholder="Mobile Number" required>
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
        </form>
        {% if error %}
        <div class="alert alert-danger mt-3">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

HTML_INDEX = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fertilizer Optimizer</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container">
        <h1 class="mt-4">Enter Soil Data</h1>
        <form action="/" method="post">
            <div class="form-group">
                <label for="location">Location:</label>
                <input type="text" id="location" name="location" class="form-control" placeholder="Field Location" required>
            </div>
            <div class="form-group">
                <label for="n">Nitrogen (N):</label>
                <input type="number" step="any" id="n" name="n" class="form-control" placeholder="Nitrogen level in ppm" required>
            </div>
            <div class="form-group">
                <label for="p">Phosphorus (P):</label>
                <input type="number" step="any" id="p" name="p" class="form-control" placeholder="Phosphorus level in ppm" required>
            </div>
            <div class="form-group">
                <label for="k">Potassium (K):</label>
                <input type="number" step="any" id="k" name="k" class="form-control" placeholder="Potassium level in ppm" required>
            </div>
            <div class="form-group">
                <label for="s">Sulfur (S):</label>
                <input type="number" step="any" id="s" name="s" class="form-control" placeholder="Sulfur level in ppm" required>
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
        {% if error %}
        <div class="alert alert-danger mt-3">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

HTML_RESULTS = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fertilizer Recommendations</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container">
        <h1 class="mt-4">Fertilizer Recommendations</h1>
        {{ table_html | safe }}
        <br>
        <a href="/" class="btn btn-secondary">Back</a>
        <a href="/fertilizers" class="btn btn-info">View Fertilizers</a>
    </div>
</body>
</html>
"""


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        mobile = request.form.get('mobile')

        # Simple validation
        if username and mobile:
            # Store user data in session
            session['username'] = username
            session['mobile'] = mobile
            return redirect(url_for('index'))
        else:
            return render_template_string(HTML_LOGIN, error="Please provide both username and mobile number.")

    return render_template_string(HTML_LOGIN)


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve form data
        location = request.form.get('location', '')
        n = request.form.get('n', '')
        p = request.form.get('p', '')
        k = request.form.get('k', '')
        s = request.form.get('s', '')

        if not all([location, n, p, k, s]):
            return render_template_string(HTML_INDEX, error="Please provide all input data.")

        try:
            # Create DataFrame
            data = {
                'Location': [location],
                'N': [float(n)],
                'P': [float(p)],
                'K': [float(k)],
                'S': [float(s)],
            }
            df = pd.DataFrame(data)

            # Calculate fertilizer needs
            recommendations = calculate_fertilizer_need(df)

            # Recommend crops based on nutrient levels
            recommendations = recommend_crops(recommendations)

            # Convert DataFrame to HTML table
            table_html = recommendations.to_html(classes='table table-bordered', index=False)

            return render_template_string(HTML_RESULTS, table_html=table_html)
        except ValueError:
            return render_template_string(HTML_INDEX,
                                          error="Invalid input data. Please enter numeric values for nutrients.")

    return render_template_string(HTML_INDEX)


@app.route('/fertilizers', methods=['GET'])
def fertilizers():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Display fertilizer details including names, costs, and efficiencies
    data = {
        'Nutrient': list(FERTILIZER_COSTS.keys()),
        'Fertilizer Names': [', '.join(FERTILIZER_NAMES[nutrient]) for nutrient in FERTILIZER_NAMES],
        'Cost (per kg)': list(FERTILIZER_COSTS.values()),
        'Efficiency': list(FERTILIZER_EFFICIENCIES.values())
    }
    df = pd.DataFrame(data)
    table_html = df.to_html(classes='table table-bordered', index=False)

    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fertilizers</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container">
            <h1 class="mt-4">Fertilizer Details</h1>
            {table_html}
            <br>
            <a href="/" class="btn btn-secondary">Back</a>
        </div>
    </body>
    </html>
    """)


if __name__ == '__main__':
    app.run("localhost", 3000, True)