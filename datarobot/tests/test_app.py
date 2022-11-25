import io
import os
from io import BytesIO
from os.path import exists
from werkzeug import utils
import json

from flask import url_for
from datarobot.app import app, upload_dir


def test_hello_route():
    response = app.test_client().get('/hello')

    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'Hello DataRobot!'


def test_create_is_a_post():
    response = app.test_client().get('/create')
    assert response.status_code == 405


def test_create_bad_response():
    response = app.test_client().post('/create')
    assert response.status_code == 400

    response = app.test_client().post('/create?target=testing')
    assert response.status_code == 500


def test_create_with_a_csv_file():
    data = dict(
        csv_file=(BytesIO(
            b'Sepal.Length,Sepal.Width,Petal.Length,Petal.Width,Species\n'
            b'5.1,3.5,1.4,0.2,setosa\n'
            b'5.2,3.5,1.4,0.2,virginia',
        ), "iris.csv"),
    )

    response = app.test_client().post(
        '/create?target=Species',
        content_type='multipart/form-data',
        data=data,
    )

    assert response.status_code == 202

    filename = 'iris.model'
    assert exists(utils.safe_join(upload_dir, filename))


def test_predict():
    response = app.test_client().post(
        '/predict'
    )
    assert response.status_code == 400

    response = app.test_client().post(
        '/predict?input_line=1,2,3,4',
    )
    assert response.status_code == 200
    assert response.data.decode('utf-8') in ["['setosa']", "['virginica']"]
