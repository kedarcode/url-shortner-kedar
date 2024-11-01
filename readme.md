URL Shortener Service
This project is a URL shortening service using FastAPI, Redis, and NGINX. The service provides RESTful APIs to create and manage shortened URLs, with request rate-limiting and URL expiration features, deployed through Docker Compose.

Project Structure

app: Contains the main application code.

nginx: NGINX configuration to act as a reverse proxy for the application.

venv: Python virtual environment for dependencies (optional for local setup).

Dockerfile: Defines the application environment.

docker-compose.yml: Contains configuration for service deployment.

nginx.conf: Configures NGINX to forward requests.

helpers.py: Contains helper functions for validation and storage.

main.py: The main application file with FastAPI routes.
Setup and Installation

Prerequisites

Docker and Docker Compose should be installed on your system.
Running the Application with Docker Compose
Clone the repository.

Ensure your terminal is in the project root directory.

Run the following command to start all services:

```bash
docker-compose up --build
```

After the services start, access the URL shortener at http://localhost:80.

Local Development
To run the service locally without Docker:

Install the required dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start Redis on your local machine (e.g., using Docker):

```bash
docker run -d --name redis -p 6379:6379 redis
```

Run the FastAPI application:

```bash
uvicorn main:app --reload
```

The application will be available at http://localhost:80.

API Documentation

Endpoints

1. Create Short URL
   URL: /url/shorten

Method: POST

Payload:

```json
{
  "url": "https://example.com",
  "custom_slug": "example",
  "expiration": 60
}
```

Response:

200 OK - Returns the shortened URL:

```json
{
  "short_url": "http://localhost:80/r/example"
}
```

400 Bad Request - Validation error if URL, slug, or expiration time is invalid.

Rate Limit: 15 requests per minute.

2. Redirect to Original URL
   URL: /r/{short_code}

Method: GET

Path Parameter: short_code - The short code generated for the URL.

Response:

Redirects to the original URL.
404 Not Found if the short code does not exist.
Rate Limit: 30 requests per minute.

Limitations
Rate Limiting: Prevents abuse by limiting the number of requests. You can adjust the rate limits in the main.py file.
URL Expiration: URLs can have an optional expiration time in seconds.
Data Persistence: Redis stores data temporarily; once the container stops, data may be lost unless persistent volumes are configured.
