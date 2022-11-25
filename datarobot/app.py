import logging
import os

from flask import Flask, request, Response
from werkzeug import utils
from sklearn import svm
from joblib import dump, load
from pandas import read_csv

UPLOAD_DIR = '/tmp/models/'

if not os.path.exists(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='clojure-rules',
        )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    return app

app = create_app()


def create_model(dataframe, target):
    """ Created a model from a dataframe, with the specified target"""
    y = dataframe.pop(target).values
    X = dataframe.values

    C = 1.0  # SVM regularization parameter

    model = svm.SVC(kernel="linear", C=C)
#   model = svm.SVC(kernel="rbf", gamma=0.7, C=C)
#   model = svm.SVC(kernel="poly", degree=3, gamma="auto", C=C)

    fitted_model = model.fit(X, y)

    return fitted_model


def save_model(model):
    """
        Saves a model to the file system.
        This is unsafe, but since I have control over who can post to this API

    """
    filename = 'iris.model'
    dump(model, utils.safe_join(UPLOAD_DIR, filename))


def load_model():
    """Loads a previoous generated model from the upload dir"""
    filename = 'iris.model'
    model = load(utils.safe_join(UPLOAD_DIR, filename))
    return model


def make_prediction(input_values):
    model = load_model()

    v = model.predict([input_values])

    return v


@app.route('/create', methods=['POST', ])
def create():
    try:
        target = request.args.get('target', None)
        if not target:
            return Response(status=400)

        f = request.files['csv_file']
        dataframe = read_csv(f)

        model = create_model(dataframe, target)

        save_model(model)

    except Exception as e:
        logging.warning("We have an exception ", exc_info=e)
        return Response(status=500)

    return Response(status=202)


@app.route('/hello', methods=['GET'])
def hello():
    """Small test to see if, the API is up and running"""
    return 'Hello DataRobot!'


@app.route('/predict', methods=['POST', ])
def predict():
    try:
        input_line = request.args.get('input_line', None)

        if not input_line:
            return Response('No input-line', status=400)

        input_values = list(map(float, input_line.split(',')))
        prediction = make_prediction(input_values)

        return Response(str(prediction), status=200)

    except FileNotFoundError as e:
        logging.warning('File not found', exc_info=e)
        return Response(status=404)
    except Exception as e:
        logging.warning("We have an exception ", exc_info=e)
        return Response(status=500)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(debug=True)
