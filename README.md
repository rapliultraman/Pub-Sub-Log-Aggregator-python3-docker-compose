# 🧩 Pub-Sub Log Aggregator (UTS Sistem Terdistribusi)

Implementasi sistem *Publish-Subscribe Log Aggregator* dengan **Idempotent Consumer** dan **Deduplication**, sebagai bagian dari UTS mata kuliah **Sistem Terdistribusi**.

---

## 📚 Deskripsi Singkat

Proyek ini merepresentasikan sistem terdistribusi yang menerima event dari satu atau lebih *publisher*, kemudian memprosesnya melalui *subscriber/consumer* yang bersifat **idempotent** — artinya, event yang sama tidak akan diproses dua kali.

Sistem dibangun menggunakan:
- **Python 3.11 + FastAPI**
- **asyncio.Queue** sebagai *in-memory event pipeline*
- **SQLite** sebagai *deduplication store* yang persisten
- **Docker** & **Docker Compose** untuk simulasi lingkungan terdistribusi lokal

Arsitektur ini menerapkan konsep dari Bab 1–7 buku *Distributed Systems: Principles and Paradigms* (Tanenbaum & Van Steen, 2023), seperti:
- Concurrency dan fault tolerance  
- Asynchronous communication  
- Idempotent consumer  
- Deduplication dan eventual consistency  
- Naming dan ordering antar event  

---

## ⚙️ Langkah-Langkah Build dan Menjalankan Proyek

Berikut panduan singkat untuk membangun dan menjalankan sistem **Pub-Sub Log Aggregator** menggunakan **Docker Compose**.

---

### 1. Persiapkan Izin Akses Folder Data

Pastikan folder `data/` memiliki izin tulis agar container dapat menyimpan file database SQLite dan log event.

```bash
sudo chmod -R 777 /Path/to/your/dir/data


```
### 2. Build dan Jalankan Sistem dengan Skema Publisher dan Aggregator


```bash
# Build ulang image tanpa cache lama
sudo docker compose build --no-cache

# Jalankan seluruh service di jaringan internal Docker
sudo docker compose up
```

### 3. Build dan Jalankan Sistem dengan Skema Unit Test dan Aggregator

```bash
#menjalankan unit test pada docker container aggregator
sudo docker compose run -e MODE=TEST aggregator
```




