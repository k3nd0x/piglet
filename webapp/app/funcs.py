from flask import Flask, render_template, url_for, flash, redirect, request, session, send_from_directory
from .api_func import get_data_api

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

def get_notis(pigapi):
    s, notis = pigapi.get(f"notifications/?show_all=false")
    noticount = notis[0]
    notilist = notis[1]
    notifications = notis[2]

    return noticount, notilist, notifications
