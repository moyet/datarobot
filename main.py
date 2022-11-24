import array
import logging
import os

from flask import Flask, request, Response
from werkzeug import utils

from sklearn import svm, datasets

from joblib import dump, load

upload_dir = 'models/'


def create_model(target):
    iris = datasets.load_iris()
    X = iris.data[:, :4]
    y = iris.target

    C = 1.0  # SVM regularization parameter

    model = svm.SVC(kernel="linear", C=C)
#   model = svm.SVC(kernel="rbf", gamma=0.7, C=C)
#   model = svm.SVC(kernel="poly", degree=3, gamma="auto", C=C)

    fitted_model = model.fit(X, y)

    return fitted_model


def save_model(model):
    # This is unsafe, but since I have control over who can post to this API
    filename = 'iris.model'
    dump(model, utils.safe_join(upload_dir, filename))


def load_model():
    # I know that this could be unsafe
    filename = 'iris.model'
    model = load(utils.safe_join(upload_dir, filename))
    return model


def make_prediction(input_values):
    model = load_model()
    iris = datasets.load_iris()

    v = model.predict([input_values])

    return iris.target_names[v]


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

    @app.route('/hello')
    def hello():
        return 'Ohhhh fuck!'

    @app.route('/create', methods=['POST', ])
    def create():
        try:
            target = request.args.get('target', None)
            if not target:
                print('No target')
                return Response(status=400)

            f = request.files['csv_file']
            filename = utils.secure_filename(f.filename)
            f.save(filename)

            model = create_model(target)
            save_model(model)

        except Exception as e:
            logging.warning("We have an exception ", exc_info=e)
            return Response(status=500)

        return Response(status=202)

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

    return app


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
