# emotion.py

def judge_emotion(text: str):
    t = (text or "").strip()

    emotion_words = {
        "喜び": ["嬉しい", "うれしい", "やった", "最高", "助かった", "できた", "成功", "よかった", "ありがとう"],
        "期待": ["楽しみ", "期待", "やってみたい", "いけそう", "挑戦", "ワクワク"],
        "不安": ["不安", "怖い", "心配", "やばい", "焦る", "眠れない", "こわい"],
        "怒り": ["ムカつく", "腹立つ", "イライラ", "最悪", "ふざけるな", "怒"],
        "悲しみ": ["悲しい", "つらい", "しんどい", "泣", "落ち込む", "へこむ"],
        "困惑": ["わからない", "意味不明", "困った", "どうすれば", "詰んだ", "混乱"],
    }

    bonus = {k: 0 for k in emotion_words}
    if "!" in t or "！" in t:
        bonus["喜び"] += 1
        bonus["期待"] += 1
    if "?" in t or "？" in t:
        bonus["困惑"] += 1
        bonus["不安"] += 1

    scores = {k: 0 for k in emotion_words}
    for emo, words in emotion_words.items():
        for w in words:
            if w in t:
                scores[emo] += 2
        scores[emo] += bonus[emo]

    best = max(scores, key=scores.get)
    emotion = "中立" if scores[best] == 0 else best
    return emotion, scores
