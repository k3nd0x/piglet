from flask import Flask, render_template, url_for, flash, redirect, request, session, send_from_directory
from hashlib import sha256
import os
import json

from app.views import app
from app.api_func import get_data_api, post_data_api, del_data_api
from app.funcs import get_notis, auth, allowed_exts

from app.piglet_api import api









