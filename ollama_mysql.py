import mysql.connector
from flask import Flask, render_template, request, jsonify
import ollama

app = Flask(__name__)

# Database connection
def create_db_connection():
    return mysql.connector.connect(
        host='localhost',  # e.g., 'localhost'
        user='root',
        password='I@mironman5',
    )

@app.route('/')
def index():
    return render_template('chatbot_interface.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    
    # Connect to the database
    try:
        db_connection = create_db_connection()
        cursor = db_connection.cursor()
    except mysql.connector.Error as err:
        return jsonify({'error': f"Database connection error: {err}"})

    # Check for database-related queries
    if "databases" in user_input.lower():
        try:
            cursor.execute("SHOW DATABASES;")
            results = cursor.fetchall()
            response = f"Here are your databases: {', '.join([r[0] for r in results])}"
        except mysql.connector.Error as err:
            response = f"Error querying database: {err}"
    else:
        # Use Ollama to process the input
        try:
            response = ollama.chat(model='llama3.1', messages=[{'role': 'user', 'content': user_input}])
        except Exception as e:
            response = f"Error processing request: {e}"
    
    cursor.close()
    db_connection.close()

    return jsonify({'response': response})

if __name__ == "__main__":
    app.run(debug=True)
