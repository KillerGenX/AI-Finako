-- ==========================================
-- 0. EKSTENSI (EXTENSIONS)
-- ==========================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Wajib untuk Enterprise Knowledge Platform
CREATE EXTENSION IF NOT EXISTS vector; 

-- ==========================================
-- 1. OTENTIKASI & PROFIL (RBAC)
-- ==========================================
-- Profil terkait dengan tabel bawaan auth.users
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    telegram_id BIGINT UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    company_email VARCHAR(255) UNIQUE NOT NULL,
    pin_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    role VARCHAR(50) DEFAULT 'account_manager', -- 'admin' atau 'account_manager'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- 2. SCOUT AI (Enterprise Account Discovery)
-- ==========================================
-- Menyimpan entitas perusahaan/akun
CREATE TABLE public.companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255) UNIQUE,
    industry VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Menyimpan sinyal pembelian dari hasil pencarian (Tavily)
CREATE TABLE public.buying_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    signal_type VARCHAR(100), -- 'news', 'funding', 'expansion', dll
    description TEXT NOT NULL,
    evidence_url TEXT,
    date_detected TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Menyimpan daftar produk IOH
CREATE TABLE public.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Menyimpan peluang spesifik milik Account Manager
CREATE TABLE public.opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES public.companies(id) ON DELETE CASCADE,
    account_manager_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    status VARCHAR(50) DEFAULT 'discovered', -- 'discovered', 'evaluating', 'qualified'
    reasoning TEXT,
    next_action TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Relasi N-ke-N: Rekomendasi produk IOH untuk peluang tertentu beserta alasan AI
CREATE TABLE public.opportunity_products (
    opportunity_id UUID NOT NULL REFERENCES public.opportunities(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    reasoning TEXT,
    PRIMARY KEY (opportunity_id, product_id)
);

-- ==========================================
-- 3. ENTERPRISE KNOWLEDGE PLATFORM
-- ==========================================
-- Menyimpan metadata dokumen enterprise (PDF, Wiki, dll)
CREATE TABLE public.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    source_url TEXT,
    content_type VARCHAR(50),
    uploaded_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Menyimpan chunk dan vektor untuk Retrieval (RAG)
CREATE TABLE public.document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(768), -- Menggunakan 768 dimensi (Gemini)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index khusus HNSW untuk mempercepat pencarian semantic vector
CREATE INDEX ON public.document_chunks USING hnsw (embedding vector_cosine_ops);


-- ==========================================
-- 4. FUNCTIONS & TRIGGERS (Otomatisasi)
-- ==========================================

-- Fungsi untuk update otomatis kolom updated_at
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Menerapkan trigger updated_at
CREATE TRIGGER on_profiles_updated
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER on_companies_updated
  BEFORE UPDATE ON public.companies
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

CREATE TRIGGER on_opportunities_updated
  BEFORE UPDATE ON public.opportunities
  FOR EACH ROW EXECUTE PROCEDURE public.handle_updated_at();

-- Fungsi: Otomatis buat profil saat user baru terdaftar di auth.users (Admin mendaftarkan user)
-- SECURITY DEFINER membuat fungsi ini dijalankan dengan hak akses pembuat (postgres) agar bisa membaca auth.users
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, company_email)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', 'Account Manager Baru'),
    NEW.email
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger: saat user berhasil dibuat di Supabase Auth
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();


-- ==========================================
-- 5. ROW LEVEL SECURITY (RLS) POLICIES
-- ==========================================
-- Aktifkan RLS pada semua tabel
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.buying_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.opportunity_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_chunks ENABLE ROW LEVEL SECURITY;

-- 5a. RLS: Profiles (AM hanya bisa lihat profilnya sendiri)
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Admins can manage all profiles" ON public.profiles FOR ALL USING (
    (SELECT role FROM public.profiles WHERE id = auth.uid()) = 'admin'
);

-- 5b. RLS: Companies, Buying Signals, Products (Shared Knowledge)
CREATE POLICY "Authenticated users can read shared data" ON public.companies FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can read signals" ON public.buying_signals FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can read products" ON public.products FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated can insert shared data" ON public.companies FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Authenticated can insert signals" ON public.buying_signals FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- 5c. RLS: Opportunities & Opportunity Products (STRICT ISOLATION)
CREATE POLICY "AM manage own opportunities" ON public.opportunities
    FOR ALL USING (account_manager_id = auth.uid());
CREATE POLICY "AM manage own opportunity products" ON public.opportunity_products
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.opportunities 
            WHERE id = opportunity_products.opportunity_id 
            AND account_manager_id = auth.uid()
        )
    );

-- 5d. RLS: Knowledge Base (Shared Knowledge)
CREATE POLICY "Authenticated users can view documents" ON public.documents FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can view chunks" ON public.document_chunks FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can insert documents" ON public.documents FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can insert chunks" ON public.document_chunks FOR INSERT WITH CHECK (auth.role() = 'authenticated');
