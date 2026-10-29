from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>🚛 HaulPool is Running!</h1><p>Flask is working. Next step: add MongoDB.</p>'

if __name__ == '__main__':
    app.run(debug=True, port=5000)