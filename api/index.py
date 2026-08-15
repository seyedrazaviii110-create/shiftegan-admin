from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!doctype html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>ادمین شیفتگان ۳۱۳</title>
    </head>
    <body style="font-family:sans-serif;text-align:center;padding:50px">

        <h1>🤖 ادمین هوشمند شیفتگان ۳۱۳</h1>

        <h2>✅ اتصال Flask و Vercel برقرار است</h2>

        <p>مرحله اول با موفقیت انجام شد.</p>

    </body>
    </html>
    """
