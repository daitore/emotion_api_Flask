from flask import Flask, request, jsonify, send_file, render_template
from io import BytesIO
from openpyxl import Workbook

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # JSONで日本語をそのまま返す


# ルート：フォーム付きトップページ（templates/index.html）
@app.get("/")
def index():
    return render_template("index.html")


# 簡易感情判定関数（必ず emotion と scores を返す）
def judge_emotion(text: str):
    t = (text or "").strip()

    emotion_words = {
        "喜び": ["嬉しい", "やった", "最高", "助かった", "できた", "成功", "よかった", "ありがとう"],
        "期待": ["楽しみ", "期待", "やってみたい", "いけそう", "挑戦", "ワクワク"],
        "不安": ["不安", "怖い", "心配", "やばい", "焦る", "眠れない", "こわい"],
        "怒り": ["ムカつく", "腹立つ", "イライラ", "最悪", "ふざけるな", "怒"],
        "悲しみ": ["悲しい", "つらい", "しんどい", "泣", "落ち込む", "へこむ"],
        "困惑": ["わからない", "意味不明", "困った", "どうすれば", "詰んだ", "混乱"],
    }

    bonus = {k: 0 for k in emotion_words.keys()}
    if "!" in t or "！" in t:
        bonus["喜び"] += 1
        bonus["期待"] += 1
    if "?" in t or "？" in t:
        bonus["困惑"] += 1
        bonus["不安"] += 1

    scores = {k: 0 for k in emotion_words.keys()}
    for emo, words in emotion_words.items():
        for w in words:
            if w in t:
                scores[emo] += 2
        scores[emo] += bonus[emo]

    best_emo = max(scores, key=scores.get)
    emotion = "中立" if scores[best_emo] == 0 else best_emo
    return emotion, scores


# Excelをその場で作ってDL（フォーム側から使う想定）
# 例: /download.xlsx?text=今日は最高
@app.get("/download.xlsx")
def download_xlsx():
    text = (request.args.get("text") or "").strip()
    if not text:
        # 空でも落とせるように最低限のExcelを返す
        text = ""

    emotion, scores = judge_emotion(text)

    wb = Workbook()
    ws = wb.active
    ws.title = "result"

    ws["A1"] = "text"
    ws["B1"] = text
    ws["A2"] = "emotion"
    ws["B2"] = emotion

    # scoresも書いておく（任意）
    ws["A4"] = "scores"
    row = 5
    for k, v in scores.items():
        ws[f"A{row}"] = k
        ws[f"B{row}"] = v
        row += 1

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    return send_file(
        bio,
        as_attachment=True,
        download_name="emotion_result.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# API（JSONで返す）
@app.post("/api/emotion")
def api_emotion():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text が空です"}), 400

    emotion, scores = judge_emotion(text)
    return jsonify({"text": text, "emotion": emotion, "scores": scores})


if __name__ == "__main__":
    # Windowsローカル用（Render本番はgunicornが起動するのでここは使われない）
    app.run(host="127.0.0.1", port=5000, debug=True)
