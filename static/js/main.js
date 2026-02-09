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

  function showEmotionOnly(obj) { // 結果を表示する関数
  const label = obj.label || "中立";   // 画面表示用データ取り出し
  const main = obj.main || "中立";     // CSS用（主）データ取り出し

  const emoji = EMOJI_MAP[main] || "😐"; // 絵文字マップから取得
  resultEl.innerHTML = //    結果を画面に表示
      ${emoji} ${label}
    </div>
  `;

  const text = (textEl.value || "").trim(); // 入力分取得
  excelLink.href = `/download.xlsx?text=${encodeURIComponent(text)}`; // ダウンロードリンク設定
  excelArea.style.display = "block"; // 非表示ダウンロードエ欄を表示
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
