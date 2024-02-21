import os

import redis
from flask import Flask
from flask_session import Session

# Initialize the app
app = Flask(__name__, instance_relative_config=True)

from app.views import dashboard
from app.views import settings
from app.views import register
from app.views import budget 
from app.views import reports
from app.views import future_spends
from app.views import orders
from app.views import category
from app.views import notifications
PROFILE_PICTURES = '/webapp/app/views/pictures'
app.config['PROFILE_PICTURES'] = PROFILE_PICTURES


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
