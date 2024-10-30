import base64
import secrets
import redis
import re
from urllib.parse import urlparse
from pydantic import HttpUrl
# Connect to Redis
client = redis.StrictRedis(host='redis', port=6379, db=0)

# Generate a unique, base64 key for session_data
def generate_unique_key():
    random_bytes = secrets.token_bytes(12)
    base64_key = base64.urlsafe_b64encode(random_bytes).rstrip(b'=').decode('utf-8')
    return base64_key

def validate_slug(slug):
    """
    Validates a given slug.
    
    Parameters:
    - slug (str): The slug to validate.
    
    Returns:
    - bool: True if the slug is valid, False otherwise.
    - str: An error message if invalid, None if valid.
    """
    if not slug:
        return False, "Slug cannot be empty."
    
    # Check length
    if len(slug) < 1 or len(slug) > 100:
        return False, "Slug must be between 1 and 100 characters."

    # Check for invalid characters
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', slug):
        return False, "Slug can only contain lowercase letters, numbers, and hyphens, and cannot start or end with a hyphen."
    
    return True, None

def validate_url(url:HttpUrl):
    url_str = str(url)  
    parsed = urlparse(url_str)
    
    # Your validation logic goes here
    is_valid_url = parsed.scheme in ("http", "https")
    url_error = None if is_valid_url else "Invalid URL scheme"

    return is_valid_url, url_error

def validate_expiration_time(expiration_time):
    """
    Validates an expiration time.
    
    Parameters:
    - expiration_time (int): The expiration time in minutes.
    
    Returns:
    - bool: True if the expiration time is valid, False otherwise.
    - str: An error message if invalid, None if valid.
    """
    if expiration_time is None:
        return True, None  # No expiration time provided is valid (defaults to 60 minutes)
    
    if not isinstance(expiration_time, int) or expiration_time <= 0:
        return False, "Expiration time must be a positive integer."
    
    return True, None

# Store URL in Redis with a base64 key and a TTL of 300 seconds
def store_url_in_redis(url, slug=None, expiration_time=None):
    # Set expiration time in seconds, defaulting to 1 hour (3600 seconds)
    ttl = expiration_time * 60 if expiration_time else 3600
    
    # Check if custom slug is provided and available
    if slug:
        if client.exists(slug):
            return "Slug not available"
        session_key = slug
    else:
        session_key = generate_unique_key()
    
    # Store the URL with the session key and expiration time
    urlstr=str(url)
    client.setex(session_key, ttl, urlstr)
    client.set(urlstr, session_key)
    return session_key

def get_key_by_url(url):
    return client.get(url).decode('utf-8') if client.exists(url) else None


