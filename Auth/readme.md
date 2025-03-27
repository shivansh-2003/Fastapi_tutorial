# FastAPI JWT Authentication with Supabase

A demonstration of JWT authentication with FastAPI using Supabase as the database.

## Supabase Setup

1. Create a Supabase account and project at https://supabase.io
2. Create a table called `users` with the following columns:
   - `id`: UUID, primary key
   - `username`: VARCHAR, unique, not null
   - `full_name`: VARCHAR, not null
   - `email`: VARCHAR, unique, not null
   - `hashed_password`: VARCHAR, not null
   - `disabled`: BOOLEAN, default false
   - `created_at`: TIMESTAMP, default now()

3. Get your Supabase URL and API key from the project settings

## Environment Setup

1. Create a `.env` file with the following:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_api_key
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   uvicorn main:app --reload
   ```

4. Access the API documentation:
   Open your browser and go to http://127.0.0.1:8000/docs

## Testing the API

1. Create a new user:
   - Endpoint: POST /users/
   - Payload: {"username": "newuser", "full_name": "New User", "email": "new@example.com", "password": "password123"}

2. Get a JWT token:
   - Endpoint: POST /token
   - Form data: username=newuser&password=password123

3. Access protected resources:
   - Endpoint: GET /users/me or GET /protected-resource/
   - Authorization header: Bearer {your_jwt_token}