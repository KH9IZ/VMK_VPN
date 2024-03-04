import json
from flask import (
    abort,
    Flask,
    request,
)
from telebot.types import Update

from main import bot
from models import create_tables


app = Flask(__name__)
create_tables()


@app.route('/bot<token>', methods=['POST'])
def bot_route(token):
    if token != bot.token:
        abort(404)
    if not request.is_json:
        abort(403)

    try:
        update = Update.de_json(request.json)
    except (ValueError, KeyError, json.decoder.JSONDecodeError):
        abort(403)

    bot.process_new_updates([update])
    return ''
