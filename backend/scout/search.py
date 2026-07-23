import httpx
import re
from urllib.parse import urlparse
from backend.core.config import settings

async def scrape_with_firecrawl(url: str, client: httpx.AsyncClient) -> str:
    if not settings.FIRECRAWL_API_KEY:
        return ""
    try:
        fc_url = "https://api.firecrawl.dev/v1/scrape"
        headers = {"Authorization": f"Bearer {settings.FIRECRAWL_API_KEY}"}
        payload = {"url": url, "formats": ["markdown"], "onlyMainContent": True}
        res = await client.post(fc_url, headers=headers, json=payload, timeout=20.0)
        if res.status_code == 200:
            data = res.json()
            return data.get("data", {}).get("markdown", "")
    except Exception as e:
        print(f"Firecrawl error for {url}: {e}")
    return ""

async def search_company_info(query: str) -> str:
    """
    Mencari informasi perusahaan menggunakan Tavily Search API,
    lalu melakukan deep-scrape pada 2 URL teratas menggunakan Firecrawl.
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
        tavily_results = data.get('results', [])
        
        # Ekstrak URL untuk di-scrape oleh Firecrawl (hindari situs berita umum jika bisa)
        news_domains = ["kompas.com", "detik.com", "tribunnews.com", "cnbcindonesia.com", "bisnis.com"]
        target_urls = []
        for res in tavily_results:
            url_str = res.get('url', '')
            domain = urlparse(url_str).netloc.lower()
            if domain and not any(news in domain for news in news_domains):
                target_urls.append(url_str)
                if len(target_urls) >= 2: # Ambil maksimal 2 URL untuk deep scrape agar tidak timeout
                    break
        
        firecrawl_context = ""
        if settings.FIRECRAWL_API_KEY and target_urls:
            firecrawl_context += "\n\nDEEP WEBSITE SCRAPE (FIRECRAWL):\n"
            for t_url in target_urls:
                scrape_res = await scrape_with_firecrawl(t_url, client)
                if scrape_res:
                    # Ambil 2000 karakter pertama saja per website agar token tidak meledak
                    firecrawl_context += f"--- Source: {t_url} ---\n{scrape_res[:2000]}\n\n"
                    
    results_text = [res.get('content', '') for res in tavily_results]
    tavily_context = f"ANALISIS AWAL (TAVILY): {answer}\n\nBERITA & PASAR:\n" + "\n".join(results_text)
    
    return tavily_context + firecrawl_context
