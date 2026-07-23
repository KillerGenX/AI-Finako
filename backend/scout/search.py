import httpx
from backend.core.config import settings

async def search_company_info(domain: str) -> str:
    """
    Mencari informasi profil dan berita terbaru perusahaan menggunakan Tavily Search API.
    """
    if not settings.TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is missing in environment variables")
        
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": settings.TAVILY_API_KEY,
        "query": f"company profile, business model, and recent news for {domain}",
        "search_depth": "advanced",
        "include_answer": True,
        "max_results": 5,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        
    answer = data.get('answer', '')
    results = [res.get('content', '') for res in data.get('results', [])]
    return f"{answer}\n\n" + "\n".join(results)
