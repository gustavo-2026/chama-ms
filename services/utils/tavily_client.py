"""
Tavily Search API Client
AI-powered search for research and discovery
"""
import os
import requests
from typing import List, Dict, Any, Optional

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "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")

class TavilyClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or TAVILY_API_KEY
        self.base_url = "https://api.tavily.com"
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web using Tavily"""
        response = requests.post(
            f"{self.base_url}/search",
            json={
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            raise Exception(f"Tavily API error: {response.text}")
    
    def get_answer(self, query: str) -> Dict[str, Any]:
        """Get AI-generated answer from Tavily"""
        response = requests.post(
            f"{self.base_url}/qna",
            json={
                "api_key": self.api_key,
                "query": query
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Tavily API error: {response.text}")


# FastAPI endpoint for search
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Search Service")

@app.get("/search")
def search(q: str, max_results: int = 5):
    """Search endpoint"""
    client = TavilyClient()
    try:
        results = client.search(q, max_results)
        return {"query": q, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ask")
def ask(q: str):
    """AI Q&A endpoint"""
    client = TavilyClient()
    try:
        answer = client.get_answer(q)
        return {"question": q, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "healthy", "service": "search"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
