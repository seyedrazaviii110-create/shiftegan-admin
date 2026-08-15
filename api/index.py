import os
import json
import urllib.request
import urllib.error
from flask import Flask, request

app = Flask(__name__)

HTML_START = """
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ادمین هوشمند شیفتگان ۳۱۳</title>

<style>
body{
    font-family:Tahoma,Arial,sans-serif;
    background:#f4f5f7;
    margin:0;
    padding:20px;
    color:#222;
}
.container{
    max-width:850px;
    margin:auto;
}
.card{
    background:white;
    border-radius:16px;
    padding:20px;
    margin-bottom:18px;
    box-shadow:0 3px 12px rgba(0,0,0,.08);
}
h1{
    text-align:center;
    margin-bottom:5px;
}
.subtitle{
    text-align:center;
    color:#666;
}
textarea{
    width:100%;
    min-height:230px;
    box-sizing:border-box;
    border:1px solid #ddd;
    border-radius:12px;
    padding:15px;
    font-family:inherit;
    font-size:16px;
    resize:vertical;
}
button{
    width:100%;
    margin-top:12px;
    padding:14px;
    border:0;
    border-radius:10px;
    background:#1976d2;
    color:white;
    font-size:17px;
    font-family:inherit;
}
button:active{
    opacity:.8;
}
.info{
    background:#e8f5e9;
    border-radius:10px;
    padding:12px;
    margin-top:15px;
}
.warning{
    background:#fff3cd;
    border-radius:10px;
    padding:12px;
    margin-top:15px;
}
.result{
    white-space:pre-wrap;
    line-height:2;
}
.score{
    font-size:24px;
    font-weight:bold;
}
</style>
</head>

<body>
<div class="container">

<div class="card">
<h1>🤖 ادمین هوشمند شیفتگان ۳۱۳</h1>
<p class="subtitle">دستیار تحلیل و پیشنهاد برای مدیران کانال</p>

<div class="info">
✅ ربات فقط پیشنهاد می‌دهد.<br>
🔒 ربات بدون اجازه مدیر هیچ پستی را ویرایش یا منتشر نمی‌کند.
</div>
</div>

<div class="card">
<h2>📝 تحلیل پست</h2>

<form method="post">

<textarea
name="text"
placeholder="متن پست کانال را اینجا وارد کنید..."
required
>{{ text }}</textarea>

<button type="submit">
🔍 تحلیل و ارائه پیشنهاد
</button>

</form>
</div>
"""

HTML_END = """
</div>
</body>
</html>
"""


def analyze_post(text):
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        return "❌ کلید OPENAI_API_KEY در Environment Variables تنظیم نشده است."

    prompt = f"""
تو دستیار حرفه‌ای مدیر یک کانال مذهبی و فرهنگی هستی.

متن زیر را فقط تحلیل کن و پیشنهاد اصلاح بده.

قوانین بسیار مهم:
1. خودت متن را تغییر نده.
2. متن نهایی بازنویسی‌شده تولید نکن.
3. فقط ایرادها و پیشنهادهای ویرایشی را به مدیر اعلام کن.
4. تصمیم نهایی همیشه با مدیر کانال است.
5. اگر متن مناسب است، صریحاً بگو نیازی به تغییر اساسی ندارد.

این موارد را بررسی کن:
- جذابیت عنوان
- وضوح و خوانایی
- غلط‌های نگارشی احتمالی
- طول و ساختار متن
- لحن مناسب کانال
- وجود ابهام یا ادعای نیازمند بررسی
- پیشنهاد هشتگ در صورت نیاز
- پیشنهاد تصویر یا رسانه در صورت نیاز
- دعوت به تعامل با مخاطب در صورت مناسب بودن

در پایان:
امتیاز کلی از 10 بده.

متن پست:
{text}
"""

    payload = {
        "model": "gpt-4.1-mini",
        "input": prompt
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))

        # استخراج متن پاسخ
        if "output_text" in result:
            return result["output_text"]

        # حالت جایگزین
        output = result.get("output", [])

        parts = []

        for item in output:
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    parts.append(content.get("text", ""))

        if parts:
            return "\n".join(parts)

        return "❌ پاسخی از سرویس هوش مصنوعی دریافت نشد."

    except urllib.error.HTTPError as e:
        try:
            error_text = e.read().decode("utf-8")
        except:
            error_text = str(e)

        return f"❌ خطای OpenAI:\n{error_text}"

    except Exception as e:
        return f"❌ خطا در ارتباط با سرویس تحلیل:\n{str(e)}"


@app.route("/", methods=["GET", "POST"])
def home():

    text = ""
    result = ""

    if request.method == "POST":

        text = request.form.get("text", "").strip()

        if not text:
            result = "❌ لطفاً متن پست را وارد کنید."

        else:
            result = analyze_post(text)

    page = HTML_START

    if result:
        page += f"""
        <div class="card">
            <h2>📊 نتیجه بررسی</h2>

            <div class="warning">
                ⚠️ این موارد فقط «پیشنهاد» هستند.
                متن اصلی پست تغییر نکرده است.
            </div>

            <div class="result">
                {result}
            </div>
        </div>
        """

    page += HTML_END

    return page


@app.route("/health")
def health():
    return {
        "status": "ok",
        "message": "ادمین هوشمند شیفتگان ۳۱۳ فعال است"
    }
