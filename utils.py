import jwt
import datetime
from flask_mail import Mail, Message
from flask import current_app

mail = Mail()  # Define the Mail instance

def generate_token(user_id):
    """Generate a JWT token for the user."""
    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def send_verification_email(user_email, token):
    """Send an email with a verification link to the user."""
    verification_link = f"http://localhost:5000/api/verify-email?token={token}"
    msg = Message(
        'Verify Your Email',
        sender='er.sumit.ranjan@gmail.com',  # Replace with your email address
        recipients=[user_email]
    )
    msg.body = f'Please verify your email by clicking the following link: {verification_link}'
    mail.send(msg)
