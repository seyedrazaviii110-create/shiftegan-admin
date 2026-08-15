import os
import json
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
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: #f3f5f7;
            font-family: Tahoma, Arial, sans-serif;
            color: #222;
        }

        .container {
            max-width: 850px;
            margin: auto;
            padding: 25px 15px;
        }

        .card {
            background: white;
            border-radius: 24px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,.08);
        }

        h1, h2, h3 {
            text-align: center;
        }

        .header {
            text-align: center;
        }

        .header h1 {
            font-size: 30px;
        }

        .header p {
            color: #666;
            font-size: 18px;
        }

        .notice {
            background: #e8f7ea;
            border-radius: 18px;
            padding: 18px;
            text-align: center;
            line-height: 2;
            font-size: 17px;
        }

        textarea {
            width: 100%;
            min-height: 250px;
            resize: vertical;
            border: 1px solid #ddd;
            border-radius: 18px;
            padding: 18px;
            font-size: 17px;
            font-family: Tahoma, Arial, sans-serif;
            direction: rtl;
        }

        button {
            width: 100%;
            margin-top: 15px;
            padding: 17px;
            border: 0;
            border-radius: 15px;
            background: #1976d2;
            color: white;
            font-size: 18px;
            cursor: pointer;
        }

        button:hover {
            background: #125ca3;
        }

        .result {
            background: #f8f9fa;
            border-radius: 18px;
            padding: 20px;
            line-height: 2;
            white-space: pre-wrap;
        }

        .score {
            text-align: center;
            font-size: 22px;
            font-weight: bold;
        }

        .warning {
            background: #fff4e5;
            padding: 15px;
            border-radius: 15px;
            margin-top: 15px;
            line-height: 2;
        }
    </style>
</head>

<body>

<div class="container">

    <div class="card header">
        <h1>🤖 ادمین هوشمند شیفتگان ۳۱۳</h1>
        <p>دستیار تحلیل و پیشنهاد برای مدیران کانال</p>

        <div class="notice">
            ✅ ربات فقط پیشنهاد می‌دهد.<br>
            🔒 ربات بدون اجازه مدیر هیچ پستی را ویرایش یا منتشر نمی‌کند.
        </div>
    </div>

    <div class="card">

        <h2>📝 تحلیل پست</h2>

        <form method="POST">

            <textarea
                name="text"
                placeholder="متن پست کانال را اینجا وارد کنید..."
            >{{ text }}</textarea>

            <button type="submit">
                🔍 تحلیل و ارائه پیشنهاد
            </button>

        </form>

    </div>

    {% if result %}

    <div class="card">

        <h2>📊 نتیجه بررسی</h2>

        <div class="score">
            امتیاز اولیه: {{ score }}/10
        </div>

        <div class="result">
            {{ result }}
        </div>

        <div class="warning">
            🔒 <b>توجه مدیر:</b><br>
            این فقط یک پیشنهاد است.
            هیچ تغییری به‌صورت خودکار روی پست انجام نمی‌شود.
            ویرایش یا انتشار فقط پس از تصمیم مدیر انجام خواهد شد.
        </div>

    </div>

    {% endif %}

</div>

</body>
</html>
"""


def analyze_text(text):
    """
    فعلاً یک تحلیل ساده انجام می‌دهد.
    بعداً می‌توانیم هوش مصنوعی واقعی را به این قسمت وصل کنیم.
    """

    if not text.strip():
        return 0, "متنی برای بررسی وارد نشده است."

    score = 7

    suggestions = []

    if len(text) < 30:
        score -= 1
        suggestions.append("🔸 متن پست کوتاه است؛ بهتر است توضیح بیشتری اضافه شود.")

    if len(text) > 1500:
        score -= 1
        suggestions.append("🔸 متن نسبتاً طولانی است؛ امکان خلاصه‌تر کردن آن وجود دارد.")

    if not any(x in text for x in ["!", "؟", "؟"]):
        suggestions.append("🔸 می‌توان برای جذاب‌تر شدن متن از تیتر یا جمله پایانی استفاده کرد.")

    if not suggestions:
        suggestions.append("✅ ساختار کلی پست مناسب به نظر می‌رسد.")

    suggestions.append("")
    suggestions.append("💡 پیشنهاد ویرایش:")
    suggestions.append("نسخه پیشنهادی فقط برای بررسی مدیر نمایش داده می‌شود و خودکار منتشر نخواهد شد.")

    return max(0, min(10, score)), "\n".join(suggestions)


@app.route("/", methods=["GET", "POST"])
def home():

    text = ""
    result = ""
    score = 0

    if request.method == "POST":

        text = request.form.get("text", "").strip()

        score, result = analyze_text(text)

    return render_template_string(
        HTML,
        text=text,
        result=result,
        score=score
    )


@app.route("/health")
def health():
    return {
        "status": "ok",
        "message": "ادمین هوشمند شیفتگان ۳۱۳ فعال است",
        "auto_edit": False,
        "auto_publish": False
    }


if __name__ == "__main__":
    app.run()
