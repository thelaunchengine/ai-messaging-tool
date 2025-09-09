from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def root():
    return jsonify({"message": "Flask Test App - Working!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "python": "3.11"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 