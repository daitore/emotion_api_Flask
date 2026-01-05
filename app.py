from flask import Flask, request, render_template_string, jsonify, send_file
from io import BytesIO
from openpyxl import Workbook

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

@app.route("/")
def index():
    return render_template("index.html")

# 簡易感情判定関数
def judge_emotion(text: str):
    t = (text or "").strip()# 文章の前後の空白を削除

    # ざっくり辞書（好きに増やしてOK）
    emotion_words = {
        "喜び": ["嬉しい", "やった", "最高", "助かった", "できた", "成功", "よかった", "ありがとう"],
        "期待": ["楽しみ", "期待", "やってみたい", "いけそう", "挑戦", "ワクワク"],
        "不安": ["不安", "怖い", "心配", "やばい", "焦る", "眠れない", "こわい"],
        "怒り": ["ムカつく", "腹立つ", "イライラ", "最悪", "ふざけるな", "怒"],
        "悲しみ": ["悲しい", "つらい", "しんどい", "泣", "落ち込む", "へこむ"],
        "困惑": ["わからない", "意味不明", "困った", "どうすれば", "詰んだ", "混乱"],
    }

    # 感嘆符・疑問符でちょい加点（おまけ）
    bonus = {"喜び": 0, "期待": 0, "不安": 0, "怒り": 0, "悲しみ": 0, "困惑": 0}
    if "!" in t or "！" in t:
        bonus["喜び"] += 1
        bonus["期待"] += 1
    if "?" in t or "？" in t:
        bonus["困惑"] += 1
        bonus["不安"] += 1

    # スコア計算
    scores = {k: 0 for k in emotion_words.keys()}  # 感情ごと 喜び のスコア初期化,0点スタート
    for emo, words in emotion_words.items():  # 感情 喜び と単語リストのペアをループ
        for w in words:
            if w in t:
                scores[emo] += 2  # 見つかったら2点（ここは調整OK）
        scores[emo] += bonus[emo]  # 文章全体の雰囲気で 追加点

    # 一番高い感情を採用（全部0なら中立）
    best_emo = max(scores, key=scores.get)
    if scores[best_emo] == 0:
        return "中立"
    return best_emo,scores


FORM_HTML = """
<h3>感情判定</h3>
<form method="post" action="/judge">
  <textarea name="text" rows="5" cols="60" placeholder="文章を入力"></textarea><br>
  <button type="submit">判定</button>
</form>
"""

RESULT_HTML = """
<h3>結果</h3>
<p><b>感情:</b> {{emotion}}</p>
<p><b>入力:</b> {{text}}</p>
<p><a href="/download.xlsx?text={{text|urlencode}}">Excelをダウンロード</a></p>
<hr>
<p><a href="/">戻る</a></p>
"""

# A用：フォーム画面
@app.get("/")
def index():
    return render_template_string(FORM_HTML)

# A用：判定して画面表示
@app.post("/judge")
def judge():
    text = (request.form.get("text") or "").strip()
    emotion, scores = judge_emotion(text)
    return render_template_string(RESULT_HTML, text=text, emotion=emotion, scores=scores)

# A用：Excelをその場で作ってDL
@app.get("/download.xlsx")
def download_xlsx():
    text = (request.args.get("text") or "").strip()
    emotion, scores = judge_emotion(text)

    wb = Workbook()
    ws = wb.active
    ws.title = "result"
    ws["A1"] = "text"
    ws["B1"] = text
    ws["A2"] = "emotion"
    ws["B2"] = emotion

    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    return send_file(
        bio,
        as_attachment=True,
        download_name="emotion_result.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# B用：API（JSONで返す）
@app.post("/api/emotion")
def api_emotion():
    data = request.get_json(silent=True) or {}#JSONデータを取得,json形式でない場合は空の辞書を返す
    text = (data.get("text") or "").strip()   ## textキーの値を取得、存在しない場合は空文字列を返す
    if not text:
        return jsonify({"error": "text が空です"}), 400# textが空の場合、エラーメッセージを返す

    emotion, scores = judge_emotion(text)#感情判定を実行
    return jsonify({"text": text, "emotion": emotion, "scores": scores})# 結果をJSON形式で返す

if __name__ == "__main__":
    app.run(debug=True)
