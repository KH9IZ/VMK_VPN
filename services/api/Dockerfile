FROM python:3.12 AS build_stage

COPY requirements.build.txt .
RUN pip install -r requirements.build.txt

RUN git clone https://github.com/XTLS/Xray-core.git
WORKDIR xray_grpc

RUN python -m grpc.tools.protoc \
    -I../Xray-core \
    --python_out=. \
    --grpc_python_out=. \
    ../Xray-core/app/proxyman/command/command.proto \
    ../Xray-core/common/protocol/user.proto \
    ../Xray-core/common/serial/typed_message.proto \
    ../Xray-core/core/config.proto \
    ../Xray-core/proxy/vless/account.proto \
    ../Xray-core/transport/global/config.proto \
    ../Xray-core/transport/internet/config.proto

FROM python:3.12

COPY --from=build_stage xray_grpc .
COPY requirements.txt /tmp
RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt

COPY app app
COPY main.py main.py
COPY grpc_manager.py grpc_manager.py

CMD ["gunicorn", "main:app", "-b", "0.0.0.0:80"]
