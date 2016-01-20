from mongoengine import *
from docdef import *
from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['MONGODB_DB'] = 'yoda'
db = MongoEngine(app)
Bootstrap(app)

@app.route("/")
def index():
    return render_template('index.html', files=File.objects)

@app.route("/view_file")
def view_file():
    return render_template('view_file.html', files=File.objects)

if __name__ == "__main__":
    app.run(debug=True)