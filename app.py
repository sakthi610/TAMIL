"""
தமிழ் Chatbot - Flask backend using Sarvam AI (sarvam-105b)
Run:  pip install -r requirements.txt
      python app.py
Open: http://127.0.0.1:5000
"""
import os
import traceback
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "sk_gf2byh03_T10h1azKZvePwJbuviRy1M8A")
SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"
MODEL = "sarvam-105b"

SYSTEM_PROMPT = """நீ ஒரு உதவிகரமான தமிழ் AI நண்பன்.

முக்கிய விதிகள்:
1. எப்போதும் தமிழ் எழுத்துக்களில் (தமிழ் ஸ்கிரிப்ட்: அ-ஔ, க-ன்) மட்டுமே பதில் சொல். Tanglish / Roman எழுத்துக்களில் ஒருபோதும் பதில் சொல்லாதே.
2. பயனர் English-ல் அல்லது Tanglish-ல் கேட்டாலும், நீ தூய தமிழில் பதில் சொல்.
3. எளிய, இனிமையான, நட்பான தமிழில் பேசு. கடினமான சொற்களைத் தவிர்.
4. பதில்கள் சுருக்கமாகவும் தெளிவாகவும் இருக்கட்டும் (மிக நீளமாக வேண்டாம்).
5. வணக்கம் சொல்லி உரையாடலைத் தொடங்கு.
6. நீ Sarvam AI-ஆல் உருவாக்கப்பட்டவன் என்பதைத் தேவைப்பட்டால் கூறு.
"""

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_msg = (data.get("message") or "").strip()
        history = data.get("history") or []  # [{role, content}]

        if not user_msg:
            return jsonify({"error": "வெற்று செய்தி அனுப்ப வேண்டாம்."}), 400

        # Build messages: system + last 10 turns + current
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in history[-10:]:
            if isinstance(m, dict) and m.get("role") in ("user", "assistant") and m.get("content"):
                messages.append({"role": m["role"], "content": str(m["content"])[:2000]})
        messages.append({"role": "user", "content": user_msg})

        try:
            resp = requests.post(
                SARVAM_URL,
                headers={
                    "api-subscription-key": SARVAM_API_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "model": MODEL,
                    "messages": messages,
                    "temperature": 0.6,
                    "max_tokens": 1024,
                    # Disable thinking mode: otherwise a small max_tokens budget can be
                    # consumed by reasoning and the API returns content=null
                    "reasoning_effort": None,
                },
                timeout=60,
            )
        except requests.exceptions.ConnectionError as e:
            print("Sarvam connection error:", e)
            return jsonify({"error": "இணைய இணைப்பு பிழை. Internet இணைப்பை சரிபார்த்து மீண்டும் முயற்சிக்கவும்."}), 503
        except requests.exceptions.Timeout:
            return jsonify({"error": "நேரம் முடிந்தது. மீண்டும் முயற்சிக்கவும்."}), 504

        if resp.status_code != 200:
            print("Sarvam error:", resp.status_code, resp.text[:1000])
            return jsonify({"error": f"Sarvam API பிழை ({resp.status_code}). மீண்டும் முயற்சிக்கவும்."}), 500

        try:
            out = resp.json()
        except Exception:
            print("Sarvam bad JSON:", resp.text[:1000])
            return jsonify({"error": "Sarvam-லிருந்து தவறான பதில். மீண்டும் முயற்சிக்கவும்."}), 500

        choices = out.get("choices") or []
        if not choices:
            print("Sarvam empty choices:", str(out)[:1000])
            return jsonify({"error": "Sarvam-லிருந்து பதில் இல்லை. மீண்டும் முயற்சிக்கவும்."}), 500

        msg = choices[0].get("message") or {}
        finish = choices[0].get("finish_reason")
        reply = msg.get("content") or msg.get("reasoning_content") or ""
        reply = reply.strip() if isinstance(reply, str) else ""

        if not reply:
            # content=null happens on length-cutoff / tool-call / filtered replies
            print(f"Sarvam empty content (finish={finish}):", str(out)[:1500])
            if finish == "length":
                return jsonify({"error": "பதில் மிக நீளமாக இருந்ததால் தடைப்பட்டது. கேள்வியை சுருக்கமாக கேளுங்கள்."}), 500
            if finish == "content_filter":
                return jsonify({"error": "இந்த கேள்விக்கு பதில் சொல்ல முடியவில்லை. வேறு கேள்வி கேளுங்கள்."}), 500
            return jsonify({"error": "Sarvam-லிருந்து வெற்று பதில் வந்தது. மீண்டும் முயற்சிக்கவும்."}), 500

        return jsonify({"reply": reply})

    except requests.exceptions.Timeout:
        return jsonify({"error": "நேரம் முடிந்தது. மீண்டும் முயற்சிக்கவும்."}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "இணைய இணைப்பு பிழை. Internet இணைப்பை சரிபார்த்து மீண்டும் முயற்சிக்கவும்."}), 503
    except Exception as e:
        print("Server error:", e)
        traceback.print_exc()
        return jsonify({"error": "சர்வர் பிழை. மீண்டும் முயற்சிக்கவும்."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
