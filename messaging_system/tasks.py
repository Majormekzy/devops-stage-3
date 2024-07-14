# tasks.py
from celery import Celery
import smtplib
from email.mime.text import MIMEText
import time

celery = Celery('tasks', backend='rpc://', broker='pyamqp://guest@localhost//')

@celery.task
def send_email(recipient):
    start_time = time.time()
    msg = MIMEText('This is a test email sent using Yahoo SMTP.')
    msg['Subject'] = 'Test Email'
    msg['From'] = 'ennyjones4u@yahoo.com'
    msg['To'] = recipient

    with smtplib.SMTP('smtp.mail.yahoo.com', 587) as server:
        server.starttls()
        server.login('ennyjones4u@yahoo.com', 'vsjfzscwkwsjtpvi')
        server.sendmail('ennyjones4u@yahoo.com', recipient, msg.as_string())

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Email sent to {recipient} in {execution_time} seconds")

