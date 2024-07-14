
```markdown
# Messaging System with RabbitMQ, Celery, and Flask behind Nginx

This project demonstrates how to set up a messaging system with RabbitMQ/Celery and a Python Flask application behind Nginx on an EC2 instance. The system can send emails and log messages to a file and is accessible via a public URL using Ngrok.

## Prerequisites

- An AWS account and an EC2 instance running Ubuntu
- Basic knowledge of Python, Flask, and Nginx
- A Yahoo email account for sending emails

## Setup Guide

### 1. Set Up the EC2 Instance

1. **Launch an EC2 Instance:**
   - Use the AWS Management Console to launch an Ubuntu instance.
   - Configure security groups to allow HTTP (port 80), HTTPS (port 443), and SSH (port 22) access.

2. **Connect to the EC2 Instance:**
   - Use SSH to connect to your EC2 instance.
   - Example command:
     ```bash
     ssh -i your-key.pem ubuntu@your-ec2-public-ip
     ```

### 2. Install Dependencies

3. **Update the System:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Install Required Packages:**
   ```bash
   sudo apt install python3 python3-venv python3-pip nginx rabbitmq-server -y
   ```

5. **Start RabbitMQ Server:**
   ```bash
   sudo systemctl start rabbitmq-server
   sudo systemctl enable rabbitmq-server
   ```

### 3. Set Up the Project Directory

6. **Create a Project Directory:**
   ```bash
   mkdir ~/messaging_system
   cd ~/messaging_system
   ```

7. **Set Up a Python Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

8. **Install Python Packages:**
   ```bash
   pip install flask celery smtplib
   ```

### 4. Create the Flask Application

9. **Create `app.py`:**
   ```python
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
   ```

### 5. Create the Celery Tasks

10. **Create `tasks.py`:**
    ```python
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
    ```

### 6. Configure Nginx

11. **Create Nginx Configuration File:**
    ```bash
    sudo nano /etc/nginx/sites-available/flask_app
    ```

12. **Add the Following Configuration:**
    ```nginx
    server {
        listen 80;

        server_name your-ec2-public-ip;

        location / {
            proxy_pass http://127.0.0.1:8080;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

13. **Enable the Configuration:**
    ```bash
    sudo ln -s /etc/nginx/sites-available/flask_app /etc/nginx/sites-enabled/
    sudo rm /etc/nginx/sites-enabled/default
    sudo nginx -t
    sudo systemctl reload nginx
    ```

### 7. Start the Flask Application and Celery Worker

14. **Run the Flask Application:**
    ```bash
    cd ~/messaging_system
    source venv/bin/activate
    python3 app.py
    ```

15. **Run the Celery Worker:**
    Open another terminal or use a new tab:
    ```bash
    cd ~/messaging_system
    source venv/bin/activate
    celery -A tasks worker --loglevel=info
    ```

### 8. Expose Your Local Server to the Internet Using Ngrok

16. **Install Ngrok:**
    ```bash
    wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
    unzip ngrok-stable-linux-amd64.zip
    sudo mv ngrok /usr/local/bin/
    ```

17. **Authenticate Ngrok:**
    ```bash
    ngrok authtoken your-ngrok-auth-token
    ```

18. **Start Ngrok to Forward Port 80:**
    ```bash
    ngrok http 80
    ```

    Note the URL provided by Ngrok.

### 9. Test the Application

#### Using `curl`

19. **Test the Send Mail Endpoint:**
    ```bash
    curl -H "ngrok-skip-browser-warning: true" https://your-ngrok-url.ngrok-free.app/sendmail?sendmail=your_recipient_email@gmail.com
    ```

20. **Test the Talk to Me Endpoint:**
    ```bash
    curl -H "ngrok-skip-browser-warning: true" https://your-ngrok-url.ngrok-free.app/talktome
    ```

#### Using Postman

21. **Test with Postman:**
   - Open Postman.
   - Create a new GET request for the send mail endpoint:
     ```
     GET https://your-ngrok-url.ngrok-free.app/sendmail?sendmail=your_recipient_email@gmail.com
     ```
   - Send the request and check the response.

   - Create a new GET request for the talk to me endpoint:
     ```
     GET https://your-ngrok-url.ngrok-free.app/talktome
     ```
   - Send the request and check the response.

#### Using a Web Browser

22. **Test with a Web Browser:**
   - Open a web browser.
   - Enter the following URL to test the send mail endpoint:
     ```
     https://your-ngrok-url.ngrok-free.app/sendmail?sendmail=your_recipient_email@gmail.com
     ```
   - Enter the following URL to test the talk to me endpoint:
     ```
     https://your-ngrok-url.ngrok-free.app/talktome
     ```

### Summary

By following these steps, you have successfully set up a messaging system with RabbitMQ/Celery and a Python Flask application behind Nginx on an EC2 instance. The system can send emails and log messages to a file, and it is accessible via a public URL using Ngrok. Ensure to monitor the logs and debug any issues that may arise during the process.

