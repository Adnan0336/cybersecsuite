from flask import Flask, render_template, request
import joblib, numpy as np, hashlib, requests, sqlite3, os

app = Flask(__name__)

# Create folders if missing
os.makedirs("models", exist_ok=True)
os.makedirs("database", exist_ok=True)

# Initialize dummy model
model_path = "models/phishing_model.pkl"
if not os.path.exists(model_path):
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    dummy_model = RandomForestClassifier()
    dummy_model.fit([[0,1,0,1,0,1,0,1,0,1]], [0])
    joblib.dump(dummy_model, model_path)

model = joblib.load(model_path)

# Initialize database
db_path = "database/logs.db"
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("CREATE TABLE logs (id INTEGER PRIMARY KEY, event TEXT, severity TEXT)")
    c.execute("INSERT INTO logs (event, severity) VALUES ('Login Failure Detected','Medium')")
    c.execute("INSERT INTO logs (event, severity) VALUES ('Phishing URL Attempt','High')")
    c.execute("INSERT INTO logs (event, severity) VALUES ('Password Breach Found','Critical')")
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/phishing', methods=['GET', 'POST'])
def phishing():
    result = None
    if request.method == 'POST':
        url = request.form['url']
        features = np.random.randint(0, 2, 10).reshape(1, -1)
        prediction = model.predict(features)[0]
        result = "🚨 Phishing Detected!" if prediction == 1 else "✅ Safe URL"
    return render_template('phishing.html', result=result)

@app.route('/password', methods=['GET', 'POST'])
def password():
    result = None
    if request.method == 'POST':
        pwd = request.form['password']
        strength = "Strong"
        if len(pwd) < 8 or pwd.isalpha() or pwd.isdigit():
            strength = "Weak"

        sha1pwd = hashlib.sha1(pwd.encode()).hexdigest().upper()
        prefix, suffix = sha1pwd[:5], sha1pwd[5:]
        res = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
        found = any(suffix in line for line in res.text.splitlines())
        result = f"{strength} | {'⚠️ Breached!' if found else '✅ Safe Password'}"
    return render_template('password.html', result=result)

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database/logs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM logs")
    data = c.fetchall()
    conn.close()
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)


