from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import sqlite3
from flask import session

views = Blueprint(__name__, "views")

def format_results(results):
    formatted_results = []
    for result in results:
        formatted_result = {
            'question': result[0],
            'answer': result[1]
        }
        formatted_results.append(formatted_result)
    return formatted_results

conn = sqlite3.connect('DiplomaWork.db', check_same_thread=False)
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
    return render_template("home.html")

@views.route('/search', methods=['POST'])
def search():
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
    
    print(formatted_results)
    return jsonify(results=formatted_results)






