from flask import Flask

app = Flask(__name__)


@app.route('/')
def home():
    return 'User Management Microservice'


if __name__ == "__main__":
    app.run(port=5002, debug=True)
