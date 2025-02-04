import os
import psycopg2
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Get PostgreSQL credentials from environment variables
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_NAME = os.getenv('POSTGRES_DB', 'messages_db')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'faiza_pwd')

def get_db_connection():
    """Establish a connection to PostgreSQL with error handling."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        print("✅ Connected to PostgreSQL successfully!")  # Log success
        return conn
    except psycopg2.Error as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")  # Log error
        return None  # Return None if the connection fails

# Initialize DB
def init_db():
    conn = get_db_connection()
    if conn is None:
        print("❌ Database initialization failed due to connection issues.")
        return
    try:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                message TEXT
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database initialized successfully!")
    except psycopg2.Error as e:
        print(f"❌ Error initializing database: {e}")

@app.route('/')
def home():
    """Fetch messages from the database and display them in index.html."""
    conn = get_db_connection()
    if conn is None:
        return "❌ Database connection failed. Check logs."
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT message FROM messages;")
        messages = cur.fetchall()  # Fetch all messages from DB
        cur.close()
        conn.close()
        return render_template('index.html', messages=messages)  # Pass messages to HTML
    except psycopg2.Error as e:
        print(f"❌ Error fetching messages: {e}")
        return "❌ Error fetching messages from the database."

@app.route('/submit', methods=['POST'])
def submit():
    """Insert new message into the database and return success response."""
    new_message = request.form.get('new_message')  # Get data from form
    if not new_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO messages (message) VALUES (%s)", (new_message,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Added successfully!"})  # Send success response
    except psycopg2.Error as e:
        print(f"❌ Error inserting message: {e}")
        return jsonify({"error": "Failed to insert message"}), 500

if __name__ == '__main__':
    init_db()  # Initialize database
    app.run(debug=True)
