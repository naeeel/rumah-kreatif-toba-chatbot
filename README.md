# Rumah Kreatif Toba - Chatbot RAG

Chatbot berbasis Retrieval-Augmented Generation (RAG) untuk Rumah Kreatif Toba.

## Fitur Utama

- Menjawab FAQ seputar produk & layanan Rumah Kreatif Toba
- Mengecek stok produk secara real-time
- Melacak pesanan berdasarkan ID pelanggan
- Memberikan rekomendasi produk berdasarkan riwayat transaksi

## Arsitektur

Chatbot ini menggunakan arsitektur Retrieval-Augmented Generation (RAG) dengan komponen utama:

1. **UI**: Antarmuka berbasis web menggunakan Streamlit
2. **API**: Backend API menggunakan FastAPI
3. **Model NLP**: Ollama untuk pemrosesan bahasa alami
4. **Pipeline RAG**: LangChain untuk mengorganisir alur kerja RAG
5. **Vector Store**: ChromaDB untuk penyimpanan vector embeddings
6. **Database**: PostgreSQL untuk penyimpanan data transaksional

## Setup Lokal

### Prasyarat

- Docker dan Docker Compose
- Python 3.9+
- Ollama (untuk menjalankan model LLM secara lokal)

### Langkah-langkah Instalasi

1. Clone repositori:
   ```
   git clone https://github.com/yourusername/rumah-kreatif-toba-chatbot.git
   cd rumah-kreatif-toba-chatbot
   ```

2. Buat file `.env` dan konfigurasi (gunakan `.env.example` sebagai contoh)

3. Jalankan dengan Docker Compose:
   ```
   docker-compose up -d
   ```

4. Akses aplikasi:
   - UI Chatbot: http://localhost:8501
   - API Dokumentasi: http://localhost:8000/docs

### Setup Manual (Tanpa Docker)

1. Buat dan aktifkan virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Jalankan API:
   ```
   uvicorn main:app --reload
   ```

4. Jalankan UI (di terminal terpisah):
   ```
   streamlit run streamlit_app.py
   ```

## Menggunakan Chatbot

Chatbot dapat digunakan untuk:

1. **Tanya Jawab Umum**:
   - "Apa saja produk yang dijual Rumah Kreatif Toba?"
   - "Bagaimana cara memesan produk dari Rumah Kreatif Toba?"

2. **Cek Stok Produk**:
   - "Berapa stok kain tenun motif batak yang tersedia?"
   - "Apakah ulos batak masih tersedia?"

3. **Lacak Pesanan**:
   - "Bagaimana status pesanan dengan ID 12345?"
   - "Kapan pesanan saya akan dikirim?"

4. **Rekomendasi Produk**:
   - "Produk apa yang paling laris?"
   - "Rekomendasi souvenir untuk oleh-oleh khas Toba"

## Deployment

Chatbot dapat di-deploy menggunakan:

1. **Deployment Lengkap (Docker)**:
   ```
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Deployment Terpisah**:
   - Deploy API ke server dengan FastAPI/Uvicorn
   - Deploy UI ke platform seperti Streamlit Cloud

## Evaluasi Kinerja

Evaluasi chatbot menggunakan RAGAS untuk metrik:

- Context Precision
- Faithfulness
- Answer Relevancy
- Harmfulness

Jalankan evaluasi:
```
python -m tests.test_rag
```

## Pemeliharaan

- **Update Database Vektor**: Jalankan script pembaruan database vektor saat dokumen baru ditambahkan.
- **Pemantauan**: Gunakan logging untuk memantau interaksi pengguna dan kinerja respons.

## Kontribusi

Silakan berkontribusi dengan membuat Pull Request atau melaporkan issue di repositori ini.

## Lisensi

[MIT License](LICENSE)
