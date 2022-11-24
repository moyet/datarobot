import pytest
from DataRobot.app import app

def test_create():
    assert True

def test_request_example(client):
    response = client.get("/posts")
    assert b"<h2>Hello, World!</h2>" in response.data