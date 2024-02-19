# TODO different build stage for make's
FROM python

WORKDIR /tmp
COPY requirements*.txt .
# временное решение пока не изобретем сборку отдельно от прода
RUN pip install -r requirements-dev.txt

WORKDIR tg_bot
COPY main.py app.py handle_timeouts.py models.py Makefile .
COPY middlewares/ middlewares/
COPY i18n/ i18n/
COPY --chmod=666 script.sh .

RUN make i18n-compile

COPY --chmod=660 <<EOF script.sh
if [ -z "\${BOT_HOST}" -o "\${BOT_HOST}" == "localhost" ]; then
    python main.py
else
    gunicron --bind=${BOT_HOST}:${BOT_PORT} --certfile=/etc/ssl/cert.pub --keyfile=/etc/ssl/cert.key app:app
fi
EOF

CMD bash script.sh

# CMD ["gunicorn", \
#      "--bind", "0.0.0.0:8443", \
#      "--certfile", "/etc/ssl/cert.pub", \
#      "--keyfile", "/etc/ssl/cert.key", \
#      "app:app"]
