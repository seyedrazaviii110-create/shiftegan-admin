import os
from flask import Flask, request, render_template_string
from openai import OpenAI

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ادمین هوشمند شیفتگان ۳۱۳</title>
<style>
body{font-family:sans-serif;max-width:850px;margin:auto;padding:15px;background:#f3f3f3}
.card{background:white;padding:20px;margin:15px 0;border-radius:15px}
textarea{width:100%;height:220px;padding:12px;box-sizing:border-box}
button{padding:12px 22px;border:0;border-radius:10px;margin-top:10px;cursor:pointer}
.result{white-space:pre-wrap;line-height:1.9}
</style>
</head>
<body>

<div class="card">
<h2>🤖 ادمین هوشمند شیفتگان ۳۱۳</h2>
<p>تحلیل و آماده‌سازی پست برای انتشار</p>
</div>

<div class="card">
<form method="post">
<textarea name="text" placeholder="متن پست را اینجا وارد کنید...">{{ text }}</textarea>
<br>
<button type="submit">🤖 تحلیل با هوش مصنوعی</button>
</form>
</div>

{% if result %}
<div class="card">
<h3>نتیجه تحلیل</h3>
<div class="result">{{ result }}</div>
</div>
{% endif %}

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    text = ""
    result = ""

    if request.method == "POST":
        text = request.form.get("text", "").strip()

        if not text:
            result = "⚠️ ابتدا متن پست را وارد کنید."
        else:
            api_key = os.environ.get("OPENAI_API_KEY")

            if not api_key:
                result = "❌ کلید OPENAI_API_KEY در Vercel تنظیم نشده است."
            else:
                try:
                    client = OpenAI(api_key=api_key)

                    response = client.responses.create(
                        model="gpt-4.1-mini",
                        input=f"""
متن زیر یک پست برای کانال مذهبی است.

آن را از نظر:
1. نگارشی
2. وضوح
3. جذابیت
4. مناسب بودن برای انتشار
5. وجود ادعاهای نیازمند بررسی

بررسی کن.

سپس:
- امتیاز از 10 بده.
- مشکلات را کوتاه توضیح بده.
- یک نسخه پیشنهادی برای انتشار ارائه کن.

متن:
{text}
"""
                    )

                    result = response.output_text

                except Exception as e:
                    result = "❌ خطا در اتصال به هوش مصنوعی:\\n" + str(e)

    return render_template_string(
        HTML,
        text=text,
        result=result
    )
