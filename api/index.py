from flask import Flask, request, jsonify, render_template_string
import os
import json
import urllib.request
import urllib.error

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
EITAAYAR_TOKEN = os.environ.get("EITAAYAR_TOKEN", "")

OPENAI_MODEL = "gpt-4o-mini"


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
            padding: 25px 16px 50px;
        }

        .header {
            background: white;
            border-radius: 25px;
            padding: 30px 20px;
            text-align: center;
            box-shadow: 0 5px 25px rgba(0,0,0,.08);
            margin-bottom: 20px;
        }

        .header h1 {
            font-size: 30px;
            margin: 5px 0 15px;
        }

        .header p {
            color: #777;
            font-size: 18px;
        }

        .safe-box {
            background: #e9f8ed;
            border-radius: 20px;
            padding: 20px;
            margin-top: 20px;
            line-height: 2;
            font-size: 17px;
        }

        .card {
            background: white;
            border-radius: 25px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 5px 25px rgba(0,0,0,.07);
        }

        .card h2 {
            text-align: center;
            font-size: 25px;
            margin-top: 5px;
        }

        textarea {
            width: 100%;
            min-height: 280px;
            border: 1px solid #ddd;
            border-radius: 18px;
            padding: 20px;
            font-family: Tahoma, Arial, sans-serif;
            font-size: 17px;
            line-height: 2;
            resize: vertical;
            outline: none;
        }

        textarea:focus {
            border-color: #1976d2;
            box-shadow: 0 0 0 3px rgba(25,118,210,.1);
        }

        button {
            width: 100%;
            border: none;
            border-radius: 16px;
            padding: 17px;
            margin-top: 18px;
            background: #1976d2;
            color: white;
            font-size: 18px;
            font-family: Tahoma, Arial, sans-serif;
            cursor: pointer;
        }

        button:disabled {
            background: #aaa;
            cursor: not-allowed;
        }

        .result {
            display: none;
        }

        .score {
            text-align: center;
            font-size: 30px;
            font-weight: bold;
            margin: 15px;
        }

        .box {
            background: #f7f8fa;
            border-radius: 18px;
            padding: 20px;
            line-height: 2;
            margin-top: 15px;
            white-space: pre-wrap;
        }

        .suggestion {
            background: #fff6e6;
            border-right: 5px solid #ff9800;
        }

        .edited {
            background: #edf7ee;
            border-right: 5px solid #4caf50;
        }

        .warning {
            background: #fff3cd;
            border-radius: 15px;
            padding: 15px;
            line-height: 2;
            margin-top: 15px;
        }

        .error-box {
            background: #fdeaea;
            border-right: 5px solid #d32f2f;
            border-radius: 18px;
            padding: 20px;
            line-height: 2;
            margin-top: 15px;
            display: none;
            white-space: pre-wrap;
        }

        .loading {
            text-align: center;
            padding: 25px;
            display: none;
        }

        .small {
            color: #777;
            font-size: 14px;
            line-height: 2;
        }

        .status {
            text-align: center;
            padding: 10px;
            color: #555;
        }
    </style>
</head>

<body>

<div class="container">

    <div class="header">

        <h1>🤖 ادمین هوشمند شیفتگان ۳۱۳</h1>

        <p>
            دستیار تحلیل و پیشنهاد برای مدیران کانال
        </p>

        <div class="safe-box">
            ✅ ربات فقط پیشنهاد می‌دهد.<br>
            🔒 بدون اجازه مدیر هیچ پستی را ویرایش یا منتشر نمی‌کند.<br>
            👤 تصمیم نهایی همیشه با مدیر کانال است.
        </div>

    </div>


    <div class="card">

        <h2>📝 تحلیل پست</h2>

        <textarea
            id="postText"
            placeholder="متن پست کانال را اینجا وارد کنید..."
        ></textarea>

        <button id="analyzeButton" onclick="analyzePost()">
            🔍 تحلیل و ارائه پیشنهاد
        </button>

        <div class="loading" id="loading">
            ⏳ در حال تحلیل پست...
        </div>

        <div class="error-box" id="errorBox"></div>

    </div>


    <div class="card result" id="result">

        <h2>📊 نتیجه بررسی</h2>

        <div class="score" id="score"></div>

        <div class="box">
            <strong>🔎 تحلیل:</strong>

            <div id="analysis"></div>
        </div>

        <div class="box suggestion">
            <strong>💡 پیشنهاد ویرایش:</strong>

            <div id="suggestion"></div>
        </div>

        <div class="box edited">
            <strong>✏️ نسخه پیشنهادی برای مدیر:</strong>

            <div id="edited"></div>
        </div>

        <div class="warning">
            🔒 <strong>توجه مدیر:</strong><br>
            این متن فقط پیشنهاد است.
            ربات هیچ تغییری روی پست کانال اعمال نمی‌کند.
            انتشار یا ویرایش فقط پس از تصمیم مدیر انجام می‌شود.
        </div>

    </div>


    <div class="card">

        <div class="status">
            🟢 سرور فعال است
        </div>

        <div class="small">
            اتصال Vercel و Flask برقرار است.
            <br>
            حالت فعلی سیستم: «پیشنهاد ویرایش توسط هوش مصنوعی»
        </div>

    </div>

</div>


<script>

async function analyzePost() {

    const text = document.getElementById("postText").value.trim();

    if (!text) {
        alert("لطفاً ابتدا متن پست را وارد کنید.");
        return;
    }

    const button = document.getElementById("analyzeButton");
    const loading = document.getElementById("loading");
    const result = document.getElementById("result");
    const errorBox = document.getElementById("errorBox");

    button.disabled = true;
    loading.style.display = "block";
    result.style.display = "none";
    errorBox.style.display = "none";
    errorBox.innerText = "";

    try {

        const response = await fetch("/api/analyze", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                text: text
            })

        });

        const data = await response.json();

        if (!response.ok) {

            const message =
                data.error ||
                "خطا در تحلیل پست";

            const details =
                data.details ||
                "";

            throw new Error(
                message +
                (details ? "\\n\\nجزئیات: " + details : "")
            );
        }

        document.getElementById("score").innerText =
            "امتیاز اولیه: " + data.score + "/10";

        document.getElementById("analysis").innerText =
            data.analysis;

        document.getElementById("suggestion").innerText =
            data.suggestion;

        document.getElementById("edited").innerText =
            data.edited_text;

        result.style.display = "block";

        window.scrollTo({
            top: result.offsetTop - 20,
            behavior: "smooth"
        });

    } catch (error) {

        errorBox.innerText = "❌ " + error.message;
        errorBox.style.display = "block";

        window.scrollTo({
            top: errorBox.offsetTop - 20,
            behavior: "smooth"
        });

    } finally {

        button.disabled = false;
        loading.style.display = "none";

    }
}

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/api/health")
def health():

    return jsonify({
        "status": "ok",
        "message": "ادمین هوشمند شیفتگان ۳۱۳ فعال است",
        "mode": "suggestion_only",
        "auto_edit": False,
        "auto_publish": False,
        "eitaayar_token_configured": bool(EITAAYAR_TOKEN),
        "openai_configured": bool(OPENAI_API_KEY),
        "openai_model": OPENAI_MODEL
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():

    try:

        data = request.get_json(silent=True) or {}

        text = (data.get("text") or "").strip()

        if not text:

            return jsonify({
                "error": "متن پست خالی است."
            }), 400


        if not OPENAI_API_KEY:

            return jsonify({
                "error": "OPENAI_API_KEY در محیط Vercel پیدا نشد."
            }), 500


        prompt = f"""
تو دستیار حرفه‌ای مدیریت یک کانال فارسی هستی.

وظیفه تو فقط «تحلیل و پیشنهاد ویرایش» است.

مهم:
- هرگز دستور انتشار پست نده.
- هرگز ادعا نکن که پست را منتشر یا ویرایش کرده‌ای.
- فقط پیشنهاد بده.
- تصمیم نهایی همیشه با مدیر کانال است.
- متن پیشنهادی را محترمانه، جذاب، روان و مناسب کانال مذهبی تنظیم کن.
- محتوای اصلی پست را بدون دلیل تغییر نده.
- اگر متن مناسب است، پیشنهاد بده فقط کمی بهتر شود.
- از اغراق، اطلاعات ساختگی و ادعاهای بدون منبع خودداری کن.

پست:

{text}

پاسخ باید فقط JSON معتبر باشد و دقیقاً این ساختار را داشته باشد:

{{
  "score": 0,
  "analysis": "تحلیل کوتاه و دقیق پست",
  "suggestion": "پیشنهادهای مشخص برای بهتر شدن پست",
  "edited_text": "نسخه پیشنهادی ویرایش‌شده متن"
}}

امتیاز را از 0 تا 10 تعیین کن.
"""


        payload = {

            "model": OPENAI_MODEL,

            "input": [

                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "تو یک ویراستار حرفه‌ای فارسی و دستیار مدیریت کانال هستی."
                        }
                    ]
                },

                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        }
                    ]
                }

            ],

            "text": {
                "format": {
                    "type": "json_object"
                }
            },

            "temperature": 0.4,

            "store": False
        }


        req = urllib.request.Request(

            "https://api.openai.com/v1/responses",

            data=json.dumps(payload).encode("utf-8"),

            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + OPENAI_API_KEY
            },

            method="POST"
        )


        with urllib.request.urlopen(req, timeout=60) as response:

            response_body = response.read().decode("utf-8")

            result = json.loads(response_body)

            request_id = response.headers.get("x-request-id", "")


        # استخراج متن خروجی Responses API

        content = ""

        for item in result.get("output", []):

            if item.get("type") == "message":

                for part in item.get("content", []):

                    if part.get("type") == "output_text":

                        content += part.get("text", "")


        content = content.strip()


        if not content:

            return jsonify({
                "error": "هوش مصنوعی پاسخ متنی برنگرداند.",
                "details": "OpenAI response did not contain output_text."
            }), 500


        # پاک کردن احتمالی Markdown

        if content.startswith("```"):

            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()


        ai_result = json.loads(content)


        score = ai_result.get("score", 0)


        try:
            score = float(score)
        except:
            score = 0


        score = max(0, min(10, score))


        return jsonify({

            "score": score,

            "analysis": ai_result.get(
                "analysis",
                "تحلیل انجام شد."
            ),

            "suggestion": ai_result.get(
                "suggestion",
                "پیشنهاد خاصی ارائه نشده است."
            ),

            "edited_text": ai_result.get(
                "edited_text",
                text
            ),

            "auto_edit": False,

            "auto_publish": False,

            "requires_admin_approval": True,

            "request_id": request_id

        })


    except urllib.error.HTTPError as e:

        status_code = e.code

        request_id = e.headers.get("x-request-id", "")

        try:

            raw_body = e.read().decode("utf-8")

        except:

            raw_body = ""


        # تلاش برای استخراج پیام استاندارد OpenAI

        error_message = ""

        error_type = ""

        error_code = ""


        try:

            error_json = json.loads(raw_body)

            error_object = error_json.get("error", {})

            error_message = error_object.get("message", "")

            error_type = error_object.get("type", "")

            error_code = error_object.get("code", "")

        except:

            pass


        # هرگز API Key یا Authorization را نمایش نمی‌دهیم

        safe_details = (

            "HTTP status: " + str(status_code)

        )


        if error_type:
            safe_details += "\\nنوع خطا: " + str(error_type)


        if error_code:
            safe_details += "\\nکد خطا: " + str(error_code)


        if error_message:
            safe_details += "\\nپیام OpenAI: " + str(error_message)


        if request_id:
            safe_details += "\\nRequest ID: " + str(request_id)


        return jsonify({

            "error": "OpenAI درخواست را قبول نکرد.",

            "details": safe_details

        }), 500


    except json.JSONDecodeError:

        return jsonify({

            "error": "پاسخ هوش مصنوعی قابل پردازش نبود.",

            "details": "پاسخ دریافتی JSON معتبر نبود."

        }), 500


    except urllib.error.URLError as e:

        return jsonify({

            "error": "ارتباط سرور Vercel با OpenAI برقرار نشد.",

            "details": str(e.reason)

        }), 500


    except Exception as e:

        return jsonify({

            "error": "خطای داخلی سرور.",

            "details": str(e)

        }), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
