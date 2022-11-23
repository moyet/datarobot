import logging
import os

from flask import Flask, request, Response
from werkzeug import utils


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

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Ohhhh fuck!'


    @app.route('/create', methods=['POST', ])
    def create():
        try:
            upload_dir = 'uploads/'

            target = request.args.get('target', None)
            if not target :
                print('No target')
                return Response(status=404)

            f = request.files['csv_file']
            filename = utils.secure_filename(f.filename)
            f.save(utils.safe_join(upload_dir, filename))
        except Exception as e:
            logging.warning("We have an exception ", exc_info=e)
            return Response(status=500)

        return Response(status=202)

    @app.route('/predict', methods=['POST', ])
    def predict():
        try:
            return Response('Hello, World!', status=200)

        except Exception as e:
            logging.warning("We have an exception ", exc_info=e)
            return Response(status=500)

    return app


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
