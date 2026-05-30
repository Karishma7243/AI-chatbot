from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------

def init_db():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # demo user
    cursor.execute("""
    INSERT INTO users (username, password)
    VALUES ('admin', '1234')
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN PAGE ----------------

@app.route('/')
def home():
    return render_template('index.html')

# ---------------- LOGIN CHECK ----------------

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM users
    WHERE username=? AND password=?
    """, (username, password))

    user = cursor.fetchone()

    conn.close()

    if user:
        return redirect(url_for('rag_page'))
    else:
        return "Invalid Username or Password"

# ---------------- RAG PAGE ----------------

@app.route('/rag')
def rag_page():
    return render_template('rag.html')

# ---------------- ASK QUESTION ----------------

@app.route('/ask', methods=['POST'])
def ask():

    question = request.form['question']

    # Your RAG code here
    # Example:
    answer = f"You asked: {question}"

    return f"""
    <h2>Question:</h2>
    <p>{question}</p>

    <h2>Answer:</h2>
    <p>{answer}</p>

    <br><br>

    <a href='/rag'>Back</a>
    """

# ---------------- RUN ----------------

if __name__ == '__main__':
    app.run(debug=True)