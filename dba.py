import os

# Ensure the data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Set the database URI
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/site.db'
 
