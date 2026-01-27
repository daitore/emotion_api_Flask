# emotion.py
import re

def _normalize(s: str) -> str:
    """ゆれ吸収：空白を整える（最低限）"""
    s = (s or "").strip()
    s = s.replace("　", " ")
    s = re.sub(r"\s+", " ", s)
    return s

def judge_emotion(text: str):
    t = _normalize(text)

    # ざっくり辞書（漢字/ひらがなゆれも少し入れる）
    emotion_words = {
        "喜び": ["嬉しい", "うれしい", "やった", "最高", "助かった", "できた", "成功", "よかった", "ありがとう"],
        "期待": ["楽しみ", "期待", "やってみたい", "いけそう", "挑戦", "ワクワク", "わくわく"],
        "不安": ["不安", "怖い", "こわい", "心配", "やばい", "焦る", "眠れない"],
        "怒り": ["ムカつく", "むかつく", "腹立つ", "イライラ", "最悪", "ふざけるな", "怒"],
        "悲しみ": ["悲しい", "かなしい", "つらい", "しんどい", "泣", "落ち込む", "へこむ"],
        "困惑": ["わからない", "分からない", "意味不明", "困った", "どうすれば", "詰んだ", "混乱"],
    }

    # 強調語（少し加点）
    boosters = ["超", "めっちゃ", "すごく", "かなり", "本当に", "マジで"]

    # 否定語（近くにあると減点）
    negations = ["ない", "じゃない", "ではない", "なく", "なかった", "ません"]

    scores = {k: 0 for k in emotion_words}

    # 記号の雰囲気ボーナス
    if "!" in t or "！" in t:
        scores["喜び"] += 1
        scores["期待"] += 1
    if "?" in t or "？" in t:
        scores["困惑"] += 1
        scores["不安"] += 1

    # 強調語が入ってた回数（最大2まで使う）
    boost_count = sum(1 for b in boosters if b in t)
    boost_bonus = min(boost_count, 2)

    # メイン判定
    word_hit = False

    for emo, words in emotion_words.items():
        for w in words:
            idx = t.find(w)
            if idx == -1:
                continue

            word_hit = True

            add = 2 + boost_bonus

            window = t[idx: idx + len(w) + 6]
            if any(ng in window for ng in negations):
                add -= 1

            scores[emo] += add

    # ★ 辞書ワードが0回なら「記号だけ判定」をする
    if not word_hit:
        ex = t.count("!") + t.count("！")
        qu = t.count("?") + t.count("？")

        # 記号の組み合わせ
        if ("!?" in t) or ("！？" in t) or ("?!" in t) or ("？！" in t):
            return "困惑", scores

        # 強いびっくり
        if ex >= 2 and qu == 0:
            return "期待", scores  # 喜びでもOK（好みに合わせて）
        # 強いはてな
        if qu >= 2 and ex == 0:
            return "困惑", scores

        # どちらも少しある（迷い）
        if ex >= 2 and qu >= 2:
            return "困惑", scores

        return "中立", scores

    # マイナスは0に丸める（見た目用）
    for k in scores:
        if scores[k] < 0:
            scores[k] = 0

    # ★ 主・副 感情の判定（副は2点以上のときだけ表示）★
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top1, top2 = sorted_scores[0], sorted_scores[1]

    if top2[1] >= 2:
        emotion = f"主：{top1[0]} / 副：{top2[0]}"
    else:
        emotion = f"主：{top1[0]}"

    return emotion, scores



