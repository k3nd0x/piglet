# app/__init__.py

import os

import redis
from flask import Flask
from flask_session import Session
import logging
PROFILE_PICTURES = '/webapp/source/app/pictures'

# Initialize the app
app = Flask(__name__, instance_relative_config=True)

hdlr = logging.FileHandler('access.log')
formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s')
hdlr.setLevel(logging.INFO)
hdlr.setFormatter(formatter)

app.logger.addHandler(hdlr)

# Load the views
from source.app import views
from source.app import register
from source.app import budget_sharing 
from source.app import reports
from source.app import future_spends
app.config['UPLOAD_FOLDER'] = PROFILE_PICTURES


app.config['SESSION_COOKIE_SAMESITE'] = "None"
if os.environ.get('SECURE_COOKIE') == "True":
    app.config['SESSION_COOKIE_SECURE'] = True
else:
    app.config['SESSION_COOKIE_SECURE'] = False


# Load the config file
app.config.from_object('config')
app.secret_key = os.urandom(16).hex()

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')

server_session = Session(app)
