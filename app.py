from flask import Flask
from flask import jsonify

flaskApp = Flask(__name__)


@flaskApp.route("/")
def home():
    return jsonify({"message": "hello world"})


if __name__ == "__main__":
    flaskApp.run()
