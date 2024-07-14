# app.py
from flask import Flask, request
from tasks import celery, send_email
from datetime import datetime

app = Flask(__name__)

@app.route('/sendmail')
def send_mail():
    recipient = request.args.get('sendmail')
    if recipient:
        send_email.delay(recipient)
        return 'Email queued for sending.'
    return 'Recipient email not provided.', 400

@app.route('/talktome')
def talk_to_me():
    log_path = '/var/log/messaging_system.log'
    try:
        with open(log_path, 'a') as log_file:
            log_file.write(f'Current time: {datetime.now()}\n')
        return 'Logged the current time.'
    except PermissionError:
        return f'Permission denied: Unable to write to {log_path}.', 500

@app.route('/')
def index():
    return 'Welcome to the Messaging System!'

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.errorhandler(404)
def page_not_found(e):
    return 'Page not found', 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

