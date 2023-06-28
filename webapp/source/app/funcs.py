from flask import Flask, render_template, url_for, flash, redirect, request, session, send_from_directory
from source.app import app

from .api_func import get_data_api, post_data_api, del_data_api
def allowed_exts(ext):
    allowed = [ 'jpeg', 'jpg', 'png']
    ext = ext.lower()
    if ext in allowed:
        return True
    else:
        return False
def auth():
    auth = session["authorization"]

    return auth

def get_notis():
    userid = session["userid"]
    noticount, notilist, notifications = get_data_api("notis", data={ "uid": userid, "show_all": False},auth=auth())

    return noticount, notilist, notifications
