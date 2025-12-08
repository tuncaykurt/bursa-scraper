from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import os
import sys
from main import run_scraper

# LivaProxy Configuration - Türkiye Rotating Proxy
PROXY_CONFIG = {
    "server": "http://45.94.171.52:1080",
    "username": "EJCXumk9",
    "password": "iqRvjxOP"
}

app = FastAPI(title="Bursa Real Estate Scraper API")

# Request model for POST endpoint
class ScrapeRequest(BaseModel):
    limit: int = 20

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/webhook/scrape")
async def scrape_webhook_get(limit: int = 20):
    """
    Webhook endpoint (GET) to trigger scraping
    Query parameter: limit (default: 20, max: 50)
    """
    try:
        # Validate limit
        if limit < 1:
            raise HTTPException(status_code=400, detail="Limit must be at least 1")
        if limit > 50:
            raise HTTPException(status_code=400, detail="Limit cannot exceed 50")
        
        print(f"Webhook received - scraping {limit} listings from BURSA (all listings) with TR proxy")
        
        # Run scraper with proxy
        listings = await run_scraper(limit=limit, proxy=PROXY_CONFIG)
        
        return JSONResponse(content={
            "status": "success",
            "count": len(listings),
            "listings": listings
        })
    
    except Exception as e:
        error_message = str(e)
        print(f"Error in webhook: {error_message}")
        
        # Check if it's a proxy-related error
        if "Proxy" in error_message or "proxy" in error_message:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Proxy connection failed. Please check proxy configuration.",
                    "details": error_message
                }
            )
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": error_message
            }
        )

@app.post("/webhook/scrape")
async def scrape_webhook_post(request: ScrapeRequest):
    """
    Webhook endpoint (POST) to trigger scraping
    Request body: {"limit": 20}
    """
    try:
        # Validate limit
        if request.limit < 1:
            raise HTTPException(status_code=400, detail="Limit must be at least 1")
        if request.limit > 50:
            raise HTTPException(status_code=400, detail="Limit cannot exceed 50")
        
        print(f"Webhook received - scraping {request.limit} listings from BURSA (all listings) with TR proxy")
        
        # Run scraper with proxy
        listings = await run_scraper(limit=request.limit, proxy=PROXY_CONFIG)
        
        return JSONResponse(content={
            "status": "success",
            "count": len(listings),
            "listings": listings
        })
    
    except Exception as e:
        error_message = str(e)
        print(f"Error in webhook: {error_message}")
        
        # Check if it's a proxy-related error
        if "Proxy" in error_message or "proxy" in error_message:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Proxy connection failed. Please check proxy configuration.",
                    "details": error_message
                }
            )
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": error_message
            }
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 6090))
    uvicorn.run(app, host="0.0.0.0", port=port)
