"""Module for WSGI connection to Nginx server. Additionally process hosting documentation."""
import flask
from main import bot, telebot


WEBHOOK_ENDPOINT = f"/{bot.token}/"
HOST = "45.142.215.232"  # TODO: Вынести в конфигурацию
PUBCERT = "/etc/ssl/certs/nginx-selfsigned.crt"

app = flask.Flask(__name__, static_url_path='/docs/', static_folder='docs/build/html')
#bot.delete_webhook()
#with open(PUBCERT, 'r') as pubcert:
#    bot.set_webhook(url=f"https://{HOST}:{WEBHOOK_ENDPOINT}",
#                    certificate=pubcert)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Index endpoint serves confused face."""
    return "O.o"

@app.route('/docs/')
@app.route('/docs/<path:path>')
def docs(path='index.html'):
    """Documentation endpoint."""
    return app.send_static_file(path)

@app.route(WEBHOOK_ENDPOINT, methods=['POST'])
def bot_webhook():
    """Process received telegram bot webhook events."""
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    flask.abort(403)
    return 'Unknown content-type', 403

if __name__ == "__main__":
    app.run(host="0.0.0.0")
