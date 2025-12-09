# 🏠 Bursa Sahibinden Scraper

**N8N'de test edilmiş ve çalışan versiyon!**

Bu proje Bursa bölgesindeki Sahibinden.com'daki satılık daire ilanlarını scrape eder.

## ✨ Özellikler

- ✅ **N8N'de çalışıyor** - Production'da test edilmiş
- 🤖 **Cloudflare Bypass** - Otomatik captcha çözümü
- 🌐 **Proxy Desteği** - Opsiyonel proxy kullanımı
- 🚀 **FastAPI Webhook** - REST API entegrasyonu
- 📊 **Detaylı Bilgi** - Fiyat, konum, ilan sahibi, telefon numarası
- 🐳 **Docker Ready** - Coolify/Docker deployment

## 📦 Kurulum

### Lokal Geliştirme

```bash
# Python 3.13+ gerekli
pip install uv
uv sync
```

### Docker ile Çalıştırma

```bash
docker-compose up --build
```

## 🚀 Kullanım

### 1. Webhook Server Başlatma

```bash
# uv ile
uv run python webhook_server.py

# veya direkt
python webhook_server.py
```

Server `http://localhost:6090` adresinde çalışacak.

### 2. API Kullanımı

#### GET Request (Basit)
```bash
curl "http://localhost:6090/webhook/scrape?limit=5"
```

#### POST Request (Proxy ile)
```bash
curl -X POST "http://localhost:6090/webhook/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 5,
    "proxy": {
      "server": "http://proxy-server:port",
      "username": "user",
      "password": "pass"
    }
  }'
```

#### Health Check
```bash
curl "http://localhost:6090/health"
```

## 🐳 Coolify Deployment

### 1. GitHub'a Yükle

```bash
git add .
git commit -m "Add working scraper from n8n"
git push origin main
```

### 2. Coolify'da Ayarla

1. **Service** → **bursa-scraper** → **Settings**
2. **Build Pack**: `Dockerfile`
3. **Port**: `6090`
4. **Environment Variables**:
   ```
   DEFAULT_LIMIT=5
   MAX_LIMIT=20
   ```

### 3. Test Edin

```
https://your-domain.yapayzekaotomasyon.cloud/webhook/scrape?limit=2
```

## ⚙️ Environment Variables

| Variable | Default | Açıklama |
|----------|---------|----------|
| `PORT` | `6090` | Server portu |
| `DEFAULT_LIMIT` | `5` | Varsayılan ilan sayısı |
| `MAX_LIMIT` | `20` | Maksimum ilan sayısı |

## 📝 Notlar

- **N8N'de çalışıyor**: Production'da test edilmiş kod
- **Proxy opsiyonel**: Genelde gerekmiyor, ama yüksek hacimde kullanım için önerilir
- **Cloudflare bypass**: Otomatik çalışır

## 📞 Destek

Sorular için GitHub Issues kullanın.

## ⚖️ Yasal Uyarı

Sadece eğitim ve kişisel kullanım içindir.
