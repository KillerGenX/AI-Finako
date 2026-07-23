import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import get_service_supabase
from backend.api.deps import get_current_user_id
from fastapi import HTTPException
from dotenv import load_dotenv

# Ensure .env is loaded
load_dotenv()

async def run_tests():
    print("========================================")
    print("🧪 MENJALANKAN TEST FASE 1 & 2")
    print("========================================")
    
    print("\n1. Mengetes Koneksi Database Supabase (Service Role)...")
    try:
        supabase = get_service_supabase()
        # Lakukan query ringan untuk memastikan koneksi internet & token valid
        response = supabase.table("profiles").select("count", count="exact").limit(1).execute()
        print("✅ KONEKSI BERHASIL: FastAPI bisa membaca Supabase!")
        
        print("\n2. Mengetes Logika Otentikasi Telegram ID...")
        try:
            # Kita melempar ID Telegram palsu (999999)
            await get_current_user_id(999999)
            print("❌ GAGAL: Seharusnya ID palsu ditolak, tapi malah berhasil.")
        except HTTPException as e:
            if e.status_code == 401:
                print(f"✅ OTENTIKASI BERHASIL: Sistem dengan benar menolak pengguna tak terdaftar.")
                print(f"   [Pesan dari Sistem]: {e.detail}")
            else:
                print(f"❌ GAGAL: Terjadi error HTTP tak terduga: {e.status_code}")
    except Exception as e:
        print(f"❌ KONEKSI GAGAL: {str(e)}")
        print("Pastikan Anda sudah mengisi SUPABASE_SERVICE_ROLE_KEY dengan benar di file .env")

    print("\n========================================")
    print("Test Selesai.")
    print("========================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
