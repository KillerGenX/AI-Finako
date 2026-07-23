from backend.scout.search import search_company_info
from backend.scout.analyzer import analyze_company
from supabase import Client

async def discover_account(query: str, user_id: str, supabase: Client):
    """
    Menjalankan workflow lengkap Scout AI berdasarkan query bebas, memproses beberapa perusahaan sekaligus,
    dan menyimpannya ke database dengan konteks RLS pengguna.
    """
    # 1. Search (Tavily)
    raw_data = await search_company_info(query)
    
    # 2. Analyze (Gemini)
    list_analysis = analyze_company(query, raw_data)
    
    # 3. Database Persistence
    created_opportunities = []
    
    for analysis in list_analysis.results:
        # Cek apakah company sudah ada di database shared
        company_res = supabase.table("companies").select("id").eq("domain", analysis.domain).execute()
        if company_res.data:
            company_id = company_res.data[0]['id']
        else:
            new_company = supabase.table("companies").insert({
                "name": analysis.company_name,
                "domain": analysis.domain,
                "industry": analysis.industry,
                "description": analysis.description
            }).execute()
            company_id = new_company.data[0]['id']
        
        # Insert Sinyal Pembelian
        if analysis.signals:
            signal_payloads = []
            for sig in analysis.signals:
                signal_payloads.append({
                    "company_id": company_id,
                    "signal_type": sig.signal_type,
                    "description": sig.description,
                    "evidence_url": sig.evidence_url
                })
            supabase.table("buying_signals").insert(signal_payloads).execute()
            
        # Insert Opportunity (Terikat dengan user_id secara RLS)
        opp = supabase.table("opportunities").insert({
            "company_id": company_id,
            "account_manager_id": user_id,
            "score": analysis.evaluation.score,
            "status": analysis.evaluation.status,
            "reasoning": analysis.evaluation.reasoning,
            "next_action": analysis.evaluation.next_action
        }).execute()
        
        created_opportunities.append({
            "opportunity": opp.data[0],
            "analysis": analysis.model_dump()
        })
    
    return created_opportunities
