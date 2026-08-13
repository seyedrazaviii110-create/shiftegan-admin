import os
import urllib.parse
import urllib.request
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ادمین هوشمند شیفتگان ۳۱۳</title>
<style>
body{font-family:sans-serif;max-width:800px;margin:auto;padding:15px;background:#f4f4f4}
.card{background:white;padding:18px;margin:12px 0;border-radius:15px}
textarea{width:100%;height:220px;padding:10px;box-sizing:border-box}
button{padding:12px 20px;border:0;border-radius:10px;margin-top:10px}
</style>
</head>
<body>
<div class="card">
<h2>🤖 ادمین هوشمند شیفتگان ۳۱۳</h2>
<p>نسخه آزمایشی مدیریت محتوا</p>
</div>

<div class="card">
<form method="post">
<textarea name="text" placeholder="متن پست را اینجا وارد کنید..."></textarea>
<br>
<button type="submit">🔍 تحلیل پست</button>
</form>
</div>

{% if text %}
<div class="card">
<h3>نتیجه بررسی</h3>
<p><b>امتیاز اولیه:</b> {{ score }}/10</p>
<p><b>وضعیت:</b> {{ status }}</p>
<h4>متن پیشنهادی</h4>
<textarea>{{ text }}</textarea>

<form method="post" action="/publish">
<input type="hidden" name="text" value="{{ text|e }}">
<button type="submit">✅ تأیید و ارسال به ایتا</button>
</form>
</div>
{% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    text = ""
    score = 8
    status = "آماده بررسی"

    if request.method == "POST":
        text = request.form.get("text", "").strip()

        if not text:
            score = 0
            status = "متن وارد نشده است"
        elif len(text) > 1500:
            score = 6
            status = "نیازمند کوتاه‌سازی"
        else:
            score = 8
            status = "مناسب برای بررسی نهایی"

    return render_template_string(
        HTML,
        text=text,
        score=score,
        status=status
    )

@app.route("/publish", methods=["POST"])
def publish():
    text = request.form.get("text", "").strip()

    token = os.environ.get("EITAAYAR_TOKEN")
    chat_id = os.environ.get("EITAAYAR_CHANNEL_ID")

    if not token or not chat_id:
        return """
        <html lang="fa" dir="rtl">
        <h2>⚠️ اتصال ایتایار هنوز تنظیم نشده است.</h2>
        <p>ابتدا Secretهای پروژه را در Vercel تنظیم می‌کنیم.</p>
        <a href="/">بازگشت</a>
        </html>
        """

    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text
    }).encode()

    url = "https://eitaayar.ir/api/" + token + "/sendMessage"

    try:
        req = urllib.request.Request(url, data=data, method="POST")

        with urllib.request.urlopen(req, timeout=20) as response:
            result = response.read().decode("utf-8", "replace")

        return """
        <html lang="fa" dir="rtl">
        <h2>✅ درخواست ارسال شد</h2>
        <pre>%s</pre>
        <a href="/">بازگشت</a>
        </html>
        """ % result

    except Exception as e:
        return """
        <html lang="fa" dir="rtl">
        <h2>❌ ارسال انجام نشد</h2>
        <pre>%s</pre>
        <a href="/">بازگشت</a>
        </html>
        """ % str(e), 500
