from mongoengine import *
from docdef import *
from flask import Flask, render_template, redirect, url_for
from flask.ext.mongoengine import MongoEngine
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['MONGODB_DB'] = 'yoda'
db = MongoEngine(app)
Bootstrap(app)

@app.route("/")
def index():
    return render_template('index.html', files=File.objects.order_by('-timestamp'))

@app.route("/view_file/<file_id>")
def view_file(file_id):
    return render_template('view_file.html', files=File.objects(id=file_id))

@app.route("/remove_file/<file_id>")
def remove_file(file_id):
    File.objects(id=file_id).delete()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)