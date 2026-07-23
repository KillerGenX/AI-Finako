import httpx
from backend.core.config import settings

async def search_company_info(query: str) -> str:
    """
    Mencari informasi perusahaan berdasarkan query bebas menggunakan Tavily Search API.
    Contoh query: "Perusahaan kelapa sawit di Riau"
    """
    if not settings.TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is missing in environment variables")
        
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": settings.TAVILY_API_KEY,
        "query": f"Business overview, recent news, and exact company names for: {query}. Focus on enterprise prospects in Indonesia.",
        "search_depth": "advanced",
        "include_answer": True,
        "max_results": 7,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=30.0)
        response.raise_for_status()
        data = response.json()
        
    answer = data.get('answer', '')
    results = [res.get('content', '') for res in data.get('results', [])]
    return f"ANALISIS AWAL: {answer}\n\nSUMBER DATA:\n" + "\n".join(results)
