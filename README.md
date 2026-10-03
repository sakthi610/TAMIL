# தமிழ் AI நண்பன் 🤖

Sarvam AI (sarvam-105b) பயன்படுத்தி உருவாக்கப்பட்ட இலவச தமிழ் Chatbot.

## அமைப்பு

1. Python நிறுவவும் (3.8+)
2. Terminal-ல்:
```
cd C:\Users\ADMIN\Desktop\Tamil
pip install -r requirements.txt
python app.py
```
3. Browser-ல் திறக்கவும்: http://127.0.0.1:5000

## அம்சங்கள்
- 💬 தமிழில் மட்டுமே பதில் (Tanglish கேட்டாலும் தமிழில் பதில்)
- 🎤 குரல் உள்ளீடு (Chrome-ல் ta-IN)
- 📜 திருக்குறள், கதை, சமையல் quick buttons
- 🧠 உரையாடல் நினைவகம் (கடைசி 10 messages)

## Files
- app.py → Flask backend + Sarvam API
- templates/index.html → Chat UI
- .env → உங்கள் SARVAM_API_KEY (யாருடனும் பகிர வேண்டாம்!)
- requirements.txt

## API Key
Sarvam dashboard: https://dashboard.sarvam.ai
Model: sarvam-105b | Endpoint: POST https://api.sarvam.ai/v1/chat/completions
