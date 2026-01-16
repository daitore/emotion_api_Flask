# 強い感情だけを拾う」設計,弱い不安,静かな困惑は 中立に落ちやすい。
import re

def _normalize(s: str) -> str:
    """ゆれ吸収：全角/半角や空白を整えて、小文字化（英字用）"""
    s = (s or "").strip()
    s = s.replace("　", " ")
    s = re.sub(r"\s+", " ", s)
    return s

def judge_emotion(text: str):
    t = _normalize(text)

    # まずは “ゆれ” を辞書側で吸収（漢字・ひらがな両方を入れる）
    emotion_words = {
        "喜び": ["嬉しい", "うれしい", "やった", "最高", "助かった", "できた", "成功", "よかった", "ありがとう"],
        "期待": ["楽しみ", "期待", "やってみたい", "いけそう", "挑戦", "ワクワク", "わくわく"],
        "不安": ["不安", "怖い", "こわい", "心配", "やばい", "焦る", "眠れない"],
        "怒り": ["ムカつく", "腹立つ", "イライラ", "最悪", "ふざけるな", "怒", "むかつく"],
        "悲しみ": ["悲しい", "かなしい", "つらい", "しんどい", "泣", "落ち込む", "へこむ"],
        "困惑": ["わからない", "分からない", "意味不明", "困った", "どうすれば", "詰んだ", "混乱"],
    }

    # 強調語（ちょい加点）
    boosters = ["超", "めっちゃ", "すごく", "かなり", "本当に", "マジで"]

    # 否定語（直前にあると減点）
    negations = ["ない", "じゃない", "ではない", "なく", "なかった", "ません"]

    # スコア初期化
    scores = {k: 0 for k in emotion_words}

    # 記号ボーナス
    if "!" in t or "！" in t:
        scores["喜び"] += 1
        scores["期待"] += 1
        scores["怒り"] += 1  # 怒りの強調にもなる
    if "?" in t or "？" in t:
        scores["困惑"] += 1
        scores["不安"] += 1

    # 強調語ボーナス（文章に含まれてたら少し全体底上げ）
    boost_count = sum(1 for b in boosters if b in t)

    # メイン判定
    for emo, words in emotion_words.items():
        for w in words:
            idx = t.find(w)
            if idx == -1:
                continue

            # 基本点
            add = 2

            # 強調語があると少し加点
            add += min(boost_count, 2)  # 最大+2くらいで十分

            # 直後/近くに否定があると減点（ざっくり）
            window = t[idx: idx + len(w) + 6]  # キーワードの後ろ少し
            if any(ng in window for ng in negations):
                add -= 1  # 否定ならマイナスにする

            scores[emo] += add

    # マイナスになりすぎたら0に丸める（見やすくする）
    for k in scores:
        if scores[k] < 0:
            scores[k] = 0

    # ベストを決める
    best = max(scores, key=scores.get)
    emotion = "中立" if scores[best] == 0 else best
    return emotion, scores
