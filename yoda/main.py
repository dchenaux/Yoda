from mongoengine import *
from docdef import *
from flask import Flask, render_template, redirect, url_for
from flask.ext.mongoengine import MongoEngine
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension

from collections import defaultdict
import time

app = Flask(__name__)
app.config['MONGODB_DB'] = 'yoda'
app.debug = True
app.config['SECRET_KEY'] = "b\xac\xea&\x9d\x86\x98Da?\xcaL\x146\x13\x83\x82.$\x91\xee\x03\xe3\x95"

app.config['DEBUG_TB_PANELS'] = [
    'flask_debugtoolbar.panels.versions.VersionDebugPanel',
    'flask_debugtoolbar.panels.timer.TimerDebugPanel',
    'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
    'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
    'flask_debugtoolbar.panels.template.TemplateDebugPanel',
    #'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
    'flask_debugtoolbar.panels.logger.LoggingPanel',
    'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
    # Add the MongoDB panel
    'flask_debugtoolbar_mongo.panel.MongoDebugPanel',
]

toolbar = DebugToolbarExtension(app)

db = MongoEngine(app)
Bootstrap(app)

@app.route("/")
def index():
    return render_template('index.html', files=File.objects.exclude("lines", "content").order_by('-timestamp'))

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

@app.route("/compare_files/<files_id>")
def compare_files(files_id):

    return render_template('compare_files.html')

@app.route("/remove_file/<file_id>")
def remove_file(file_id):
    File.objects(id=file_id).delete()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)