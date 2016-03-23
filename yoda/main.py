import re

from collections import defaultdict
from pprint import pprint

from mongoengine import *

from flask import Flask, render_template, redirect, url_for, flash
from flask.ext.mongoengine import MongoEngine
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension

from docdef import *
import settings

app = Flask(__name__)
app.config['MONGODB_DB'] = settings.MONGODB
app.config['SECRET_KEY'] = "b\xac\xea&\x9d\x86\x98Da?\xcaL\x146\x13\x83\x82.$\x91\xee\x03\xe3\x95"
app.debug = True

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

@app.route("/view_files/<files_id>")
def view_file(files_id):

    series = {}
    files_object = File.objects(id__in=re.split('&', files_id))

    for file in files_object:
        serie = defaultdict(list)
        for line in file.lines:
            for k,listv in line.data.items():
                for v in listv:
                    if type(v) is (int or float):
                        serie[k].append(v)
        series[file.id] = serie

    return render_template('view_files.html', files=files_object, series=series)

@app.route("/remove_file/<file_id>")
def remove_file(file_id):
    File.objects(id=file_id).delete()
    flash('The entry %s was successfully deleted' % file_id)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()