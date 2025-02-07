from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import subprocess
import os
from typing import Optional
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Crawler API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À remplacer par vos domaines en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    url: HttpUrl
    max_depth: Optional[int] = 10

@app.post("/crawl")
async def start_crawl(request: CrawlRequest):
    try:
        # Vérifier si le dossier crawler existe
        if not os.path.exists("crawler"):
            raise HTTPException(status_code=500, detail="Crawler directory not found")

        # Lancer le crawler avec l'URL fournie
        process = subprocess.Popen(
            ["scrapy", "crawl", "domain_crawler", "-a", f"start_url={request.url}"],
            cwd="crawler",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return {
            "status": "success",
            "message": "Crawl started",
            "url": str(request.url)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs")
async def get_logs():
    try:
        log_path = "crawler/logs/crawler.log"
        if not os.path.exists(log_path):
            return {"logs": []}
        
        with open(log_path, "r") as f:
            logs = f.readlines()
        return {"logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)