document.addEventListener("DOMContentLoaded", () => { // HTMLが全部読み込まれたら実行
  const btn = document.getElementById("btn"); //最初にHTMLの部品を全部読込む
  const textEl = document.getElementById("text");
  const resultEl = document.getElementById("result");
  const statusEl = document.getElementById("status");
  const excelArea = document.getElementById("excel-area");
  const excelLink = document.getElementById("excel-link");
  const clearBtn = document.getElementById("clearBtn");
  const KEY = "emotion_text";// ローカルストレージのキー名

  // 入力したらlocalStorage に自動保存
  textEl.addEventListener("input", () => {
  localStorage.setItem(KEY, textEl.value);
  });

  // 起動時に復元なければ空文字
  textEl.value = localStorage.getItem(KEY) || "";

  // クリアボタンの流れ
  clearBtn.addEventListener("click", () => {
  localStorage.removeItem(KEY); // ローカルストレージから削除
  textEl.value = ""; // テキストエリアを空に
  resultEl.textContent = "ここに結果が表示されます";
  excelArea.style.display = "none"; // エクセルダウンロードエリアを非表示
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

  //ボタンを押したときの流れ
  btn.addEventListener("click", async () => {
    const text = (textEl.value || "").trim(); // 前後の空白を削除
    if (!text) {                               //テキストが空なら
      resultEl.textContent = "文章を入力してね";
      return;
    }

    statusEl.textContent = "判定中…";
    try{
      //感情判定APIを安全に呼び出す
       const res = await fetch("/api/emotion", {  //サーバーにPOSTで送る
        method: "POST",
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify({ text })
      });

      const data = await res.json(); // 結果をJSONで受け取る
      showEmotionOnly(data);  // 結果を表示する関数を呼び出す
    } catch (e) {  //エラーが出たときの処理
      resultEl.textContent = "通信エラー";
    } finally {  // 最後に必ず実行する処理
      statusEl.textContent = "";
    }
  });
});
