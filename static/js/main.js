document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("btn");
  const textEl = document.getElementById("text");
  const resultEl = document.getElementById("result");
  const statusEl = document.getElementById("status");
  const excelArea = document.getElementById("excel-area");
  const excelLink = document.getElementById("excel-link");

  const EMOJI_MAP = {
    "喜び": "😊",
    "期待": "✨",
    "不安": "😟",
    "怒り": "😡",
    "悲しみ": "😢",
    "困惑": "😕",
    "中立": "😐"
  };

  function showEmotionOnly(obj) {
    const emo = obj.emotion || "中立";
    const emoji = EMOJI_MAP[emo] || "😐";

    resultEl.innerHTML = `
      <div class="emotion emotion-${emo}">
        ${emoji} ${emo}
      </div>
    `;

    const text = (textEl.value || "").trim();
    excelLink.href = `/download.xlsx?text=${encodeURIComponent(text)}`;
    excelArea.style.display = "block";
  }

  btn.addEventListener("click", async () => {
    const text = (textEl.value || "").trim();
    if (!text) {
      resultEl.textContent = "文章を入力してね";
      return;
    }

    statusEl.textContent = "判定中…";

    try {
      const res = await fetch("/api/emotion", {
        method: "POST",
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify({ text })
      });

      const data = await res.json();
      showEmotionOnly(data);
    } catch (e) {
      resultEl.textContent = "通信エラー";
    } finally {
      statusEl.textContent = "";
    }
  });
});
