# eSimNowAI — WhatsApp & Telegram eSIM Bot 🌍

This project is an AI-powered eSIM assistant that helps users browse and purchase global eSIM plans via **WhatsApp** or **Telegram**.

## 🚀 Features
- Real-time country and plan fetching from live API
- Smart caching (`data_cache.json`)
- Dynamic price and validity info
- Multi-platform support (WhatsApp & Telegram)
- Integrated PayU payment link

## ⚙️ Run Locally
```bash
pip install -r requirements.txt
python WhatsappBot.py
python TelegramBot.py 

Test via Postman:
	•	URL: http://127.0.0.1:5050/whatsapp
	•	Method: POST
	•	Body: From=whatsapp:+911234567890&Body=hi

APIs Used
	•	Country API → https://apiesim.connectingit.in/api/country/list
	•	Product API → https://apiesim.connectingit.in/api/product/get-all-product

⸻
