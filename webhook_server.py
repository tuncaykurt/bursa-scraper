from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import os
from main import run_scraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sahibinden Scraper Webhook", version="1.0.0")


class ProxyConfig(BaseModel):
    server: str
    username: Optional[str] = None
    password: Optional[str] = None


class ScrapeRequest(BaseModel):
    limit: Optional[int] = None
    proxy: Optional[ProxyConfig] = None


@app.get("/webhook/scrape")
async def trigger_scrape_get(limit: int = None):
    """
    GET endpoint to trigger scraping (backwards compatibility)
    """
    return await trigger_scrape_logic(limit=limit, proxy=None)


@app.post("/webhook/scrape")
async def trigger_scrape_post(request: ScrapeRequest):
    """
    POST endpoint to trigger scraping with proxy support
    """
    proxy_dict = None
    if request.proxy:
        proxy_dict = request.proxy.model_dump()

    return await trigger_scrape_logic(limit=request.limit, proxy=proxy_dict)


async def trigger_scrape_logic(limit: int = None, proxy: dict = None):
    """
    Common logic for both GET and POST endpoints
    """
    try:
        # Get default values from environment or use hardcoded defaults
        default_limit = int(os.getenv("DEFAULT_LIMIT", 5))
        max_limit = int(os.getenv("MAX_LIMIT", 20))

        # Use default if limit not provided
        if limit is None:
            limit = default_limit

        # Ensure limit is between 1 and max_limit
        limit = min(max(limit, 1), max_limit)

        proxy_info = ""
        if proxy and proxy.get('server'):
            proxy_info = f" with proxy {proxy['server']}"

        logger.info(f"Webhook received - starting scraper with limit {limit}{proxy_info}")
        listings = await run_scraper(limit, proxy)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "count": len(listings),
                "listings": listings
            }
        )
    except Exception as e:
        error_msg = str(e)

        # Provide more specific error messages for common proxy issues
        if "Proxy validation failed" in error_msg:
            logger.error(f"Proxy validation error: {error_msg}")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "error_type": "proxy_validation_failed",
                    "message": error_msg,
                    "suggestion": "Check if your proxy server is running and accessible. Verify the proxy URL format and credentials."
                }
            )
        elif "NS_ERROR_PROXY_BAD_GATEWAY" in error_msg:
            logger.error(f"Proxy gateway error: {error_msg}")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "error_type": "proxy_bad_gateway",
                    "message": "The proxy server returned a bad gateway error",
                    "suggestion": "The proxy server may be down, overloaded, or misconfigured. Try a different proxy server."
                }
            )
        elif "proxy" in error_msg.lower():
            logger.error(f"Proxy-related error: {error_msg}")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "error_type": "proxy_error",
                    "message": error_msg,
                    "suggestion": "Check your proxy configuration. Ensure the proxy server supports the required protocol (HTTP/SOCKS5)."
                }
            )
        else:
            logger.error(f"General scraping error: {error_msg}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "error_type": "scraping_error",
                    "message": f"Failed to run scraper: {error_msg}"
                }
            )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 6090))
    uvicorn.run(app, host="0.0.0.0", port=port)
