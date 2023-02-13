# app/__init__.py

import os

import redis
from flask import Flask
from flask_session import Session
PROFILE_PICTURES = '/webapp/source/app/static/'

# Initialize the app
app = Flask(__name__, instance_relative_config=True)


# Load the views
from source.app import views
from source.app import register
from source.app import budget_sharing 
from source.app import reports
app.config['UPLOAD_FOLDER'] = PROFILE_PICTURES


app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['SESSION_COOKIE_SECURE'] = "True"

# Load the config file
app.config.from_object('config')
app.secret_key = os.urandom(16).hex()

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')

server_session = Session(app)
