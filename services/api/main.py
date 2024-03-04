from flask import (
    abort,
    Flask,
    jsonify,
    request,
)
from grpc_manager import (
    add_user as grpc_add,
    delete_user as grpc_delete,
)
from uuid import uuid4


app = Flask(__name__)


@app.route('/user', methods=['POST'])
def add_user():
    if not (email := request.values.get('email')):
        abort(400)
    uuid = uuid4()
    grpc_add(
        id=uuid,
        email=email,
    )
    return jsonify(uuid=uuid, email=email)


@app.route('/user', methods=['DELETE'])
def delete_user():
    ...


@app.route('/users', methods=['GET'])
def get_users():
    raise NotImplementedError()
