import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'f8c418118f71a6388a718c0ba32c23d4')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'YDjvlsED8jN2L2oLl7xDSJvmYgsZf7OcOr9Y1ZLOGU0')  # Add this line for JWT
    # Email configuration for Gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'er.sumit.ranjan@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'Anything@123')  # Use App Password if 2-Step Verification is enabled
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False