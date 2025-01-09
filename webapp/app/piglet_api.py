#!/usr/bin/env python3
import requests
import json

class api:
    def __init__(self,auth=None):
        self.apihost = "http://127.0.0.1:8080/"
        self.headers = { "accept": "application/json" }

        self.session = requests.Session()

        self.headers["Authorization"] = "Bearer {}".format(auth)
    
    def get_token(self,payload):
        self.user = payload["email"]
        self.password = payload["password"]
        headers = { "accept": "application/x-www-form-urlencoded" }
        url = self.apihost + "admin/token"
        data = { "username": self.user, "password": self.password}

        try:
            r = self.session.post(url, headers=headers, data=data)
            if r.status_code != 200:
                return r.status_code,r.json()
        except:
            return 502,{'detail': "request error"}

        try:
            response = r.json()
        except:
            return 502,{'detail': "request error"}

        self.session.close()
        return r.status_code,response


    def get(self, url, data=None):
        url = self.apihost + url

        try:
            if data:
                r = self.session.get(url,headers=self.headers, data=json.dumps(data)).json()
                state = True
            else:
                r = self.session.get(url,headers=self.headers).json()
                state = True
        except:
            r = None
            state = False

        return state, r
    def post(self, url,data=None):
        url = self.apihost + url

        try:
            if data:
                r = self.session.post(url,headers=self.headers,data=json.dumps(data)).json()
                state = True
            else:
                r = self.session.post(url,headers=self.headers).json()
                state = True
        except:
            r = None
            state = False

        return state, r
    def put(self, url,data=None):
        url = self.apihost + url

        try:
            if data:
                r = self.session.put(url,headers=self.headers,data=json.dumps(data)).json()
                state = True
            else:
                r = self.session.put(url,headers=self.headers).json()
                state = True
        except:
            r = None
            state = False

        return state, r

    def delete(self, url, data=None):
        url = self.apihost + url

        try:
            if data:
                r = self.session.delete(url,headers=self.headers,data=json.dumps(data)).json()
                state = True
            else:
                r = self.session.delete(url,headers=self.headers).json()
                state = True
        except:
            state = False
            r = None

        return state, r
    
    def file(self, url, files=None):
        url = self.apihost + url
        try:
            r = self.session.post(url, headers=self.headers, files=files).json()
            state = True
        except:
            state = False
            r = None
        
        return state, r
    
    def close(self):
        self.session.close()
