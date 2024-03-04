# TODO different build stage for make's
FROM python

WORKDIR /tmp
COPY requirements*.txt .
# временное решение пока не изобретем сборку отдельно от прода
RUN pip install -r requirements-dev.txt

COPY bot/* /bot
COPY bot/middlewares/ /bot/middlewares/
COPY bot/i18n/ /bot/i18n/
COPY Makefile /

WORKDIR /
RUN make i18n-compile

WORKDIR /bot
COPY --chmod=660 <<EOF script.sh
if [ -z "\${BOT_HOST}" -o "\${BOT_HOST}" == "localhost" ]; then
    python main.py
else
    gunicron --bind=${BOT_HOST}:${BOT_PORT} --certfile=/etc/ssl/cert.pub --keyfile=/etc/ssl/cert.key app:app
fi
EOF

CMD bash script.sh
