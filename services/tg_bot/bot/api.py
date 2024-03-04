import requests


class API:
    def add_user(self, email):
        return requests.post('http://api/user', data={'email': email}).json()
