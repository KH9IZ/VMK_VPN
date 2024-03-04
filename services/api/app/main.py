from fastapi import FastAPI


app = FastAPI()


@app.get('/user/{user_id}')
def get_user(user_id: int):
    ...

@app.post('/user')
def post_user(user):
    ...

@app.get('/subscription/{sub_id}')
def get_subscription():
    ...

@app.post('/subscription')
def post_subscription(sub):
    ...
