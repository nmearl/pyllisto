import click
from pynpm import YarnPackage
from flask import Flask, send_from_directory
import os
import shutil
import json

import click
from flask import Flask, send_from_directory
from pynpm import YarnPackage

PKG = YarnPackage(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "js", "package.json")),
    commands=['install', 'run'])

BUILT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "js", "built"))

LIB_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "js", "lib"))

NODE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "js"))

TMP_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), "..", "js", "tmp"))

app = Flask(__name__)


@app.route('/built/<path:path>')
def static_built(path):
    return send_from_directory(BUILT_DIR, path)


@app.route('/')
def index():
    return send_from_directory(LIB_DIR, 'index.html')
    # return render_template('index.html')


@app.route('/fetch-data')
def fetch_notebook_data():
    data_path = app.config.get('data_path')

    if data_path.endswith('.ipynb'):
        data_path.replace('.ipynb', '.json')

    with open(data_path) as f:
        return json.dumps(json.load(f))


@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('-r', '--recompile', is_flag=True,
              help="Rebuild javascript files.")
@click.option('-e', '--electron', is_flag=True,
              help="Run the application in an electron shell.")
def start(path, recompile, electron):
    # Start the jupyter kernel
    # manager = KernelManager(shell_port=8888)
    # manager.start_kernel()
    #
    # client = manager.client()
    # client.start_channels()
    # client.wait_for_ready()
    #
    # msg = client.execute("import baldr; baldr.__version__")
    # print(msg)

    if recompile:
        # Run NPM install
        PKG.install()

        # Run the build command
        PKG.run('build')

    if electron:
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)

        os.mkdir(TMP_DIR)

        shutil.copy2(path, os.path.join(TMP_DIR, 'widget_code.json'))

        PKG.run('start')
    else:
        # Store the data path in the global config so it can be retrieved
        # via the front-end get request
        app.config['data_path'] = path

        # Start the flask http server
        app.run()
