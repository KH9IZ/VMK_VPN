from app.proxyman.command import command_pb2_grpc
from app.proxyman.command import command_pb2
from common.protocol import user_pb2
from common.serial import typed_message_pb2
from proxy.vless import account_pb2
import grpc
from uuid import UUID


def _obj_to_typed_msg(obj) -> typed_message_pb2.TypedMessage:
    return typed_message_pb2.TypedMessage(
        type=obj.DESCRIPTOR.full_name, 
        value=obj.SerializeToString(),
    )


def _user_operation(op):
    with grpc.insecure_channel('xray:10084') as channel:
        stub = command_pb2_grpc.HandlerServiceStub(channel)
        resp = stub.AlterInbound(
            command_pb2.AlterInboundRequest(
                tag='vless_tls',
                operation=_obj_to_typed_msg(op),
            ), 
            wait_for_ready=True,
        )
    return resp


def add_user(id: UUID, email: str):
    a = account_pb2.Account(
        id=str(id),
        flow='xtls-rprx-vision',
        encryption='none',
    )
    op = command_pb2.AddUserOperation(
        user=user_pb2.User(
            email=email,
            account=_obj_to_typed_msg(a),
        ),
    )
    return _user_operation(op)


def delete_user(email: str):
    op = command_pb2.RemoveUserOperation(
        email=email,
    )
    return _user_operation(op)
