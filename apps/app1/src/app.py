from flask import Flask, jsonify
import socket
import os

app = Flask(__name__)

@app.route('/')
def home():
    response = {
        "app_name": "app1",
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "hostname": socket.gethostname(),
        "version": os.environ.get("APP_VERSION", "v1.0")
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
