from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

# ========================================
# تنظیمات
# ========================================
CONFIG = {
    "SECRET_KEY": "my_super_secret_key_2024",
    "TELEGRAM_BOT_TOKEN": "8327175400:AAEMDFJXVjBXEpbSj-RCCIlJv3_uPNBs_e8",
    "NOTIFY_CHAT_ID": None  # Chat ID خودت اگه میخوای نوتیف بگیری
}

# ذخیره سیگنال‌ها
signals_history = []

# ========================================
# دریافت سیگنال
# ========================================
@app.route('/trade', methods=['POST'])
def receive_signal():
    # چک امنیتی
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {CONFIG['SECRET_KEY']}":
        return jsonify({"error": "Unauthorized"}), 401
    
    signal = request.json
    
    print("=" * 60)
    print(f"📊 سیگنال جدید دریافت شد - {datetime.now()}")
    print(json.dumps(signal, indent=2, ensure_ascii=False))
    print("=" * 60)
    
    # ذخیره
    signal['received_at'] = datetime.now().isoformat()
    signals_history.append(signal)
    
    # ارسال نوتیف به خودت
    if CONFIG['NOTIFY_CHAT_ID']:
        send_notification(signal)
    
    return jsonify({
        "status": "success",
        "message": "Signal received and saved",
        "signal": signal
    })

# ========================================
# ارسال نوتیف تلگرام
# ========================================
def send_notification(signal):
    message = f"""
🔔 <b>سیگنال جدید دریافت شد</b>

📊 سمبل: <b>{signal['symbol']}</b>
{"🟢 خرید" if signal['type'] == 'BUY' else "🔴 فروش"}: <code>{signal['type']}</code>

💰 ورود: <code>{signal['entry']}</code>
🛑 حد ضرر: <code>{signal['sl']}</code>
🎯 هدف 1: <code>{signal['tp1']}</code> (50%)
🎯 هدف 2: <code>{signal['tp2']}</code> (50%)

⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    try:
        requests.post(
            f"https://api.telegram.org/bot{CONFIG['TELEGRAM_BOT_TOKEN']}/sendMessage",
            json={
                "chat_id": CONFIG['NOTIFY_CHAT_ID'],
                "text": message,
                "parse_mode": "HTML"
            },
            timeout=5
        )
    except Exception as e:
        print(f"خطا در ارسال نوتیف: {e}")

# ========================================
# صفحه اصلی
# ========================================
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "✅ فعال",
        "service": "MT5 Signal Receiver",
        "total_signals": len(signals_history),
        "last_signal": signals_history[-1] if signals_history else None
    })

# ========================================
# تاریخچه سیگنال‌ها
# ========================================
@app.route('/history', methods=['GET'])
def history():
    return jsonify({
        "total": len(signals_history),
        "signals": signals_history[-50:]  # آخرین 50 تا
    })

# ========================================
# تست
# ========================================
@app.route('/test', methods=['POST'])
def test():
    return jsonify({
        "status": "OK",
        "message": "سرور در حال اجراست!",
        "timestamp": datetime.now().isoformat()
    })

# ========================================
# اجرا
# ========================================
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
