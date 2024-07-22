# File Sharing System

This repository contains a secure file-sharing system implemented in Flask.

## Endpoints

- `/ops/login` : Login for operation users
- `/ops/upload` : Upload files for operation users
- `/client/signup` : Signup for client users
- `/client/verify/<token>` : Email verification for client users
- `/client/login` : Login for client users
- `/client/download/<file_id>` : Download files for client users
- `/client/files` : List all uploaded files

## How to Run

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`

## Docker

1. Build the image: `docker build -t file-sharing-system .`
2. Run the container: `docker run -p 5000:5000 file-sharing-system`
 
