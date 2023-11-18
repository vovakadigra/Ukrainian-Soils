from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import sqlite3
from flask import session
import logging
import json
import numpy as np

views = Blueprint(__name__, "views")

logging.basicConfig(level=logging.DEBUG)

@views.route('/get_username', methods=['GET'])
def get_username():
    if 'user_id' in session:
        username = session['user_id']
        return jsonify({'username': username})
    else:
        return jsonify({'username': None})

def get_logged_in_user():
    if 'user_id' in session:
        return session['user_id']
    else:
        return None
    
def proceed_web_page(page):
    username = get_logged_in_user()

    if username:
    # The user is logged in
        return render_template(page, username=username)
    else:
        # The user is not logged in, so redirect them to the login page
        return redirect(url_for('views.login'))


def format_results(results):
    formatted_results = []
    for result in results:
        formatted_result = {
            'question': result[0],
            'answer': result[1]
        }
        formatted_results.append(formatted_result)
    return formatted_results

conn = sqlite3.connect('DiplomaWork.db', check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,  isolation_level=None)
cursor = conn.cursor()


@views.route("/logout", methods=['GET'])
def logout():
    # Clear the user session to log the user out
    session.clear()
    return redirect(url_for('views.login'))

@views.route("/", methods=['GET', 'POST'])
def login():
    error_message = None

    if request.method == 'POST':
        if 'username' in request.form:
            # Handle login logic
            username = request.form['username']
            password = request.form['password']

            # Query the database to check if the username and password match
            cursor.execute("SELECT * FROM user WHERE login=? AND password=?", (username, password))
            user = cursor.fetchone()

            if user:
                # Successful login, redirect to a protected page
                session['user_id'] = username
                return render_template("home.html")
            else:
                error_message = 'Invalid username or password. Please try again.'

        elif 'new-username' in request.form:
            # Handle signup logic
            username = request.form['new-username']
            password = request.form['new-password']
            confirm_password = request.form['confirm-password']

            if password != confirm_password:
                error_message = 'Passwords do not match.'
            else:
                cursor.execute("SELECT * FROM user WHERE login=?", (username,))
                user = cursor.fetchone()

                if user:
                    error_message = 'Username already exists.'
                else:
                    cursor.execute("INSERT INTO user (login, password) VALUES (?, ?)", (username, password))
                    conn.commit()  # Commit the changes to the database
                    return render_template("home.html")  # Redirect to the protected page after successful signup

    return render_template('login.html', error_message=error_message)

@views.route("/home", methods=['GET'])
def home():
    # Clear the user session to log the user out
    username = get_logged_in_user()

    if username:
        # The user is logged in
        return render_template('home.html', username=username)
    else:
        # The user is not logged in, so redirect them to the login page
        return redirect(url_for('views.login'))

@views.route('/search', methods=['POST'])
def search():
    try:
        # Get the user's search query from the AJAX request
        query = request.json['query']
        cursor_search = conn.cursor()

        # Connect to the database
        # Execute a database query to search for answers based on the query
        # Sample query:
        cursor_search.execute("SELECT question,answer FROM tips WHERE question LIKE ? limit 5", ('%' + query + '%',))
        results = cursor_search.fetchall()

        # Format the results as needed and return as JSON
        formatted_results = format_results(results)

        if not formatted_results:
            return jsonify(results=[]) 
        
        return jsonify(results=formatted_results)
    except Exception as e:
        logging.error(f"Error in /search route: {e}")

@views.route('/map')
def index():
    username = get_logged_in_user()
    if username:
        # The user is logged in
        return render_template('map.html')
    else:
        # The user is not logged in, so redirect them to the login page
        return redirect(url_for('views.login'))

@views.route('/research')
def research():
    username = get_logged_in_user()
    if username:
        # The user is logged in
        return render_template('research.html')
    else:
        # The user is not logged in, so redirect them to the login page
        return redirect(url_for('views.login'))
    


@views.route('/soil-types')
def soiltypes():
    username = get_logged_in_user()
    if username:
        # The user is logged in
        return render_template('soil_types.html')
    else:
        # The user is not logged in, so redirect them to the login page
        return redirect(url_for('views.login'))

    

@views.route('/conversation')
def conversation():
    username = get_logged_in_user()
    if username:
        # The user is logged in
        return render_template('conversation.html')
    else:
        # The user is not logged in, so redirect them to the login page
        return redirect(url_for('views.login'))



@views.route('/test')
def test():
    return render_template('test.html')

@views.route('/static/Ukraine.geojson')
def serve_geojson():
    try:
        # Open the file in binary mode and decode it using 'latin1' while ignoring errors
        with open('static/Ukraine.geojson', 'rb') as file:
            geojson_data = json.loads(file.read().decode('latin1', errors='ignore'))
        return geojson_data
    except Exception as e:
        return str(e)

def organic_carbon(oc_value):
    if 0.5 <= oc_value <= 2.0:
        return 0.2 * oc_value, "Medium"
    elif oc_value > 2.0:
        return 0.3 * oc_value, "High"
    elif oc_value < 2.0:
        return 10 * oc_value, "Low"

def ph_level(ph_value):
    if 5.5 <= ph_value <= 7.5:
        return 0.4 * ph_value, "Hign"
    elif 5 < ph_value < 5.5 or 5.5 < ph_value < 6:
        return 0.2 * ph_value, "Medium"
    elif ph_value < 7.5:
        return 0.3 * ph_value, "Low"
    else:
        return 0.7 * ph_value, "Low"

def texture(texture_value):
    if 3.0 <= texture_value <= 7.0:
        return 0.3 * texture_value, "Medium"
    elif texture_value < 3.0:
        return 0.2 * texture_value, "Low"
    else:
        return 0.2 * texture_value, "High"

def soil_structure(structure_value):
    if structure_value == 5:
        return 0.2 * structure_value, "Medium"
    elif structure_value == 2.5:
        return 0.2 * structure_value, "Low"
    else:
        return 0.3 * structure_value, "Hign"

def salinity(salinity_value):
    if salinity_value < 2.0:
        return 0.4 * salinity_value, "High"
    else:
        return 0.3 * salinity_value, "Low"

def potassium(potassium_value):
    if 100 <= potassium_value < 200:
        return 0.004 * potassium_value, "Medium"
    elif potassium_value >= 200:
        return 0.006 * potassium_value, "High"
    else:
        return 0.002 * potassium_value, "Low"

def nitrogen(nitrogen_value):
    if 100 <= nitrogen_value < 200:
        return 0.004 * nitrogen_value, "Medium"
    elif nitrogen_value >= 200:
        return 0.006 * nitrogen_value, "High"
    else:
        return 0.002 * nitrogen_value, "Low"

def calculate_fertility_score(organic_carbon_value, ph_level_value, texture_value, soil_structure_value, salinity_value, potassium_value,nitrogen_value):
    fertility_points = {
    'Low': 0.0,
    'Medium': 0.0,
    'High': 0.0
}

    # Calculate the contribution from each parameter and categorize them
    organic_carbon_score, organic_carbon_category = organic_carbon(organic_carbon_value)
    ph_level_score, ph_level_category = ph_level(ph_level_value)
    potassium_score, potassium_category = potassium(potassium_value)
    texture_score, texture_category = texture(texture_value)
    soil_structure_score, soil_structure_category = soil_structure(soil_structure_value)
    salinity_score, salinity_category = salinity(salinity_value)
    nitrogen_score, nitrogen_category = nitrogen(nitrogen_value)

    # Update fertility_points based on categories for each parameter
    fertility_points[organic_carbon_category] += organic_carbon_score
    fertility_points[ph_level_category] += ph_level_score
    fertility_points[potassium_category] += potassium_score
    fertility_points[texture_category] += texture_score
    fertility_points[soil_structure_category] += soil_structure_score
    fertility_points[salinity_category] += salinity_score
    fertility_points[nitrogen_category] += nitrogen_score
    # Find the maximum category as the overall fertility score
    max_fertility = max(fertility_points, key=fertility_points.get)
    result = {
        'OverallCategory': max_fertility,
        'Categories': {
            'OrganicCarbon': {
                'Value': organic_carbon_value,
                'Category': organic_carbon_category,
                'Score': organic_carbon_score
            },
            'pHLevel': {
                'Value': ph_level_value,
                'Category': ph_level_category,
                'Score': ph_level_score
            },
            'Potassium': {
                'Value': potassium_value,
                'Category': potassium_category,
                'Score': potassium_score
            },
            'Texture': {
                'Value': texture_value,
                'Category': texture_category,
                'Score': texture_score
            },
            'SoilStructure': {
                'Value': soil_structure_value,
                'Category': soil_structure_category,
                'Score': soil_structure_score
            },
            'Salinity': {
                'Value': salinity_value,
                'Category': salinity_category,
                'Score': salinity_score
            },
            'Nitrogen': {
                'Value': nitrogen_value,
                'Category': nitrogen_category,
                'Score': nitrogen_score
            }
        }
    }
    return result

@views.route('/calculate_fertility', methods=['POST'])
def calculate_fertility():
    try:
        # Get the JSON data from the request
        data = request.get_json()

        # Extract parameters from the JSON data
        organic_carbon_value = data['organicCarbon']
        ph_level_value = data['phLevel']
        texture_value = data['texture']
        soil_structure_value = data['soilStructure']
        salinity_value = data['salinity']
        potassium_value = data['potassium']
        nitrogen_value = data['nitrogen']

        # Calculate the fertility score
        fertility_scoreJSON = calculate_fertility_score(organic_carbon_value, ph_level_value, texture_value, soil_structure_value, salinity_value, potassium_value,nitrogen_value)
        # Return the fertility score as JSON
        return fertility_scoreJSON
        

    except Exception as e:
        return jsonify(error=str(e)), 400
    
@views.route('/feedback_form', methods=['GET', 'POST'])
def feedback_form():
    try:
        if request.method == 'POST':
            username = request.form['username']
            message = request.form['message']

            # Insert data into the database
            cursor.execute('INSERT INTO user_feedbacks (user_id, user_comment) VALUES ( ?, ?)', (username, message))
            conn.commit()

    except Exception as e:
        return jsonify(error=str(e)), 400
    
    return render_template('conversation.html', username=get_logged_in_user())

@views.route('/feedbacks')
def feedbacks():
    # Connect to the SQLite database
    username = get_logged_in_user()

    # Get the filter status from the query parameters
    filter_status = request.args.get('status', 'all')

    # Prepare the SQL query based on the filter status
    if filter_status == 'all':
        query = 'SELECT id, comment_status, user_comment, comment_date FROM user_feedbacks WHERE user_id = ? order by comment_date desc  LIMIT 3'
        params = (username,)
    else:
        query = 'SELECT id, comment_status, user_comment, comment_date FROM user_feedbacks WHERE user_id = ? AND comment_status = ? LIMIT 3'
        params = (username, filter_status)

    # Fetch data from the database
    cursor.execute(query, params)
    feedbacks = [{'id': row[0], 'comment_status': row[1], 'user_comment': row[2], 'comment_date': row[3]} for row in cursor.fetchall()]

    # Close the database connection

    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(feedbacks)

    # Render the template with the feedbacks data
    return render_template('conversation.html', feedbacks=feedbacks)





