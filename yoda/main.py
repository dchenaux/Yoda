#!/usr/bin/env python

from collections import defaultdict

from flask import Flask, render_template, redirect, url_for
from flask.ext.mongoengine import MongoEngine
from flask_bootstrap import Bootstrap

from docdef import *

app = Flask(__name__)
app.config['MONGODB_DB'] = 'yoda'
db = MongoEngine(app)
Bootstrap(app)

@app.route("/")
def index():
    return render_template('index.html', files=File.objects.order_by('-timestamp'))

@app.route("/view_file/<file_id>")
def view_file(file_id):

    list_var_value = []
    series = defaultdict(list)

    for file in File.objects(id=file_id):
        for line in file.lines:
            for data in line.data:
                for var_and_value in data:
                    list_var_value.append(var_and_value)

    for k,v in list_var_value: series[k].append(v)

    return render_template('view_file.html', files=File.objects(id=file_id), series=series.items())

@app.route("/remove_file/<file_id>")
def remove_file(file_id):
    File.objects(id=file_id).delete()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)