from fastapi import FastAPI, HTTPException, Body,Depends
from pydantic import BaseModel, HttpUrl, conint
from helpers import store_url_in_redis,validate_slug,validate_url,validate_expiration_time,get_key_by_url
from datetime import datetime, timedelta
import random
import string
import uvicorn
from fastapi.responses import RedirectResponse  # Import RedirectResponse
from fastapi_limiter import FastAPILimiter
import redis.asyncio as aioredis   # Ensure you have aioredis for async Redis support
from fastapi_limiter.depends import RateLimiter

app = FastAPI()


class URLRequest(BaseModel):
    url: HttpUrl
    custom_slug: str | None = None
    expiration: conint(gt=0) | None = None


@app.on_event("startup")
async def startup():
    # Initialize Redis connection for the rate limiter
    redis_client  = aioredis.from_url("redis://redis")
    await FastAPILimiter.init(redis_client)

@app.post("/url/shorten", dependencies=[
        Depends(RateLimiter(times=15, seconds=60)),
       
    ],)
async def create_short_url(request: URLRequest):

    # Validate URL
    print(request.url)
    is_valid_url, url_error = validate_url(request.url)
    if not is_valid_url:
        raise HTTPException(status_code=400, detail=url_error)
    print(is_valid_url)
    # Validate custom slug
    if request.custom_slug:
        is_valid_slug, slug_error = validate_slug(request.custom_slug)
        if not is_valid_slug:
            raise HTTPException(status_code=400, detail=slug_error)
        
    # Validate expiration time
    is_valid_expiration_time, expiration_error = validate_expiration_time(request.expiration)

    if not is_valid_expiration_time:
        raise HTTPException(status_code=400, detail=expiration_error)
    # Store the URL in Redis
    short_code = store_url_in_redis(request.url, request.custom_slug, request.expiration)

    if short_code == "Slug not available":
        raise HTTPException(status_code=400, detail=short_code)

    return {"short_url": f"http://localhost:80/r/{short_code}"}

@app.get("/r/{short_code}", dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
    ])
async def redirect_to_url(short_code: str):
    # Retrieve the original URL from Redis
    original_url = get_key_by_url(short_code)
    if original_url is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    
    return RedirectResponse(url=original_url)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
