import json
import os
from litellm import completion
from backend.models.scout_models import ScoutListResult
from backend.core.config import settings

def analyze_company(query: str, raw_data: str) -> ScoutListResult:
    """
    Menganalisis data mentah dan mendeteksi beberapa perusahaan dari query pencarian.
    Serta memberikan skor (Scoring) menggunakan Google Gemini via LiteLLM (Vertex AI).
    Mendukung Application Default Credentials (ADC) dari Google Cloud VM secara otomatis.
    """
    
    prompt = f"""
    You are an expert Enterprise Account Manager AI.
    The user searched for: '{query}'.
    Analyze the following search results to identify up to 3 distinct enterprise companies that match the query.
    For each company, extract buying signals and evaluate the business opportunity.
    
    Return ONLY a valid JSON object adhering EXACTLY to this schema (no markdown, no extra text):
    {{
      "results": [
        {{
          "company_name": "string",
          "domain": "string (website domain if available, else generic name)",
          "industry": "string",
          "description": "string",
          "signals": [
            {{"signal_type": "string", "description": "string", "evidence_url": "string"}}
          ],
          "evaluation": {{
            "score": integer (0-100),
            "reasoning": "string",
            "next_action": "string",
            "status": "discovered"
          }}
        }}
      ]
    }}
    
    Data:
    {raw_data}
    """
    
    # Memanggil Vertex AI via LiteLLM
    response = completion(
        model="vertex_ai/gemini-2.5-pro",
        messages=[{"role": "user", "content": prompt}],
    )
    
    result_str = response.choices[0].message.content
    
    # Bersihkan markdown json jika ada
    if result_str.startswith("```json"):
        result_str = result_str.replace("```json\n", "").replace("```", "").strip()
    elif result_str.startswith("```"):
        result_str = result_str.replace("```\n", "").replace("```", "").strip()
        
    result_dict = json.loads(result_str)
    return ScoutListResult(**result_dict)
