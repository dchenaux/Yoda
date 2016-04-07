#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web_exec is a visualisation module for the results generated by the analyser. It is provided inside a Flask instance
which can be either run directly by executing this script or also deployed on a webserver like Apache with mod_wsgi.
See Flask documentation for detailed informations about how to deploy an app.
"""

from collections import defaultdict
import re

from mongoengine import *

from flask import Flask, render_template, redirect, url_for, flash
from flask.ext.mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from yoda.docdef import *
import yoda.settings as settings


# Configuration of Flask App
app = Flask(__name__)
app.config['MONGODB_DB'] = settings.MONGODB
app.config['SECRET_KEY'] = "b\xac\xea&\x9d\x86\x98Da?\xcaL\x146\x13\x83\x82.$\x91\xee\x03\xe3\x95"
app.debug = True

# Debug toolbar configuration
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
    'yoda.flask_debugtoolbar_mongo.panel.MongoDebugPanel',
]

toolbar = DebugToolbarExtension(app)
# End of Debug toolbar configuration

db = MongoEngine(app)

# End of Flask configuration

@app.route("/")
def index():
    """
    Index page of the application which lists all the runs made by the analyser
    :return: render the index.html template
    """
    return render_template('index.html', files=File.objects.exclude("frames", "content").order_by('-timestamp'))

@app.route("/view_file/<file_id>")
def view_file(file_id):
    """
    view_file page which gives detailed information about a single run
    :param file_id: passed in the url, unique identifier of a run
    :return: render the view_file.html template
    """

    series = {}
    file_object = File.objects(id=file_id)

    for file in file_object:
        serie = defaultdict(list)
        for frame in file.frames:
            for line in frame.lines:
                for k,listv in line.data.items():
                    for v in listv:
                        if type(v) is (int or float):
                            serie[k].append(v)
        series[file.id] = serie

    for file in file_object:
        executed_lines = []
        for frame in file.frames:
            for line in frame.lines:
                executed_lines.append(line.lineno)
        file.content = highlight(file.content, PythonLexer(), HtmlFormatter(linenos=True, hl_lines=executed_lines, anchorlinenos=True))

    return render_template('view_file.html', file=file_object, series=series)

@app.route("/remove_files/<files_id>")
def remove_files(files_id):
    """
    Delete a run
    :param files_id: passed in the url, unique identifier of a run
    :return: redirects to index page
    """
    files_id = re.split('&', files_id)

    File.objects(id__in=files_id).delete()
    if len(files_id) == 1:
        flash('The entry %s was successfully deleted' % str(files_id).strip('[]'))
    else:
        flash('The entries %s were successfully deleted' % ', '.join(files_id))
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run()