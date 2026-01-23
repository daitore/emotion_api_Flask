document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("btn");
  const textEl = document.getElementById("text");
  const resultEl = document.getElementById("result");
  const statusEl = document.getElementById("status");
  const excelArea = document.getElementById("excel-area");
  const excelLink = document.getElementById("excel-link");
  const clearBtn = document.getElementById("clearBtn");
  const KEY = "emotion_text";

  // 入力したら保存
  textEl.addEventListener("input", () => {
  localStorage.setItem(KEY, textEl.value);
  });

  // 起動時に復元
  textEl.value = localStorage.getItem(KEY) || "";

  // クリア
  clearBtn.addEventListener("click", () => {
  localStorage.removeItem(KEY);
  textEl.value = "";
  resultEl.textContent = "ここに結果が表示されます";
  excelArea.style.display = "none";
  });


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
  const label = obj.label || "中立";   // 表示用
  const main = obj.main || "中立";     // CSS用（主）

  const emoji = EMOJI_MAP[main] || "😐";

  resultEl.innerHTML = `
    <div class="emotion emotion-${main}">
      ${emoji} ${label}
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
