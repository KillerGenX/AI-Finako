#!/bin/bash

echo "🚀 Memulai Deployment Finako AI..."

echo "1. Menarik kode terbaru dari Github..."
git pull origin main

echo "2. Membangun ulang (rebuild) backend jika ada perubahan..."
docker compose up -d --build

echo "3. Menyuntikkan (Injecting) Workflow ke n8n..."
# Pastikan folder n8n/workflows tersedia
if [ -d "n8n/workflows" ]; then
    docker exec finako_n8n n8n import:workflow --input=/data/workflows --separate
    echo "✅ Workflow berhasil diperbarui!"
else
    echo "⚠️ Folder n8n/workflows tidak ditemukan!"
fi

echo "🎉 Deployment selesai!"
