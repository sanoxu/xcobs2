// console.log("hello world"); // 名前の通り、コンソールにログを出すやつです

// document.addEventListener("DOMContentLoaded", () => {
//   console.log("Flaskで動かしています！");

//   let pos = window.innerWidth;
//   const gif = document.getElementById('myGif');
  
//   // gif要素がページに存在する場合のみ動かす
//   if (gif) {
//     setInterval(() => {
//       pos -= 2; // 動かす量
//       gif.style.left = pos + 'px';
//       if (pos < -gif.width) pos = window.innerWidth; // 画面外に出たら戻す
//     }, 30); // 30msごとに実行
//   }

//   const links = document.querySelectorAll('.nav-link');
//   links.forEach(link => {
//     link.addEventListener('click', async (e) => {
//       e.preventDefault();
//       const url = link.getAttribute('href');
//       try {
//         const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' }});
//         if (res.ok) {
//           const html = await res.text();
//           document.getElementById('content').innerHTML = html;
//         } else {
//           console.error("Fetch failed", res.status);
//         }
//       } catch (error) {
//         console.error("Fetch error", error);
//       }
//     });
//   });
// });



// console.log("hello world"); // 動作確認用

// document.addEventListener("DOMContentLoaded", () => {
//   console.log("Flaskで動かしています！");

//   // GIF移動
//   let pos = window.innerWidth;
//   const gif = document.getElementById('myGif');
  
//   if (gif) {
//     setInterval(() => {
//       pos -= 2; // 左に移動
//       gif.style.left = pos + 'px';
//       if (pos < -gif.width) pos = window.innerWidth; // 画面外に出たら戻す
//     }, 30);
//   }

  // // 非同期ページ遷移
  // const links = document.querySelectorAll('.nav-link'); // ナビゲーションリンク
  // const contentDiv = document.getElementById('content'); // 差し替え先

  // links.forEach(link => {
  //   link.addEventListener('click', async (e) => {
  //     e.preventDefault(); // 通常のリンク遷移を止める
  //     const url = link.getAttribute('href');

  //     try {
  //       const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
  //       if (res.ok) {
  //         const html = await res.text();
  //         contentDiv.innerHTML = html; // ページ部分だけ書き換え
  //         console.log("ページを更新しました:", url);
  //       } else {
  //         console.error("Fetch failed", res.status);
  //       }
  //     } catch (error) {
  //       console.error("Fetch error", error);
  //     }
  //   });
  // });

  
  // const links = document.querySelectorAll('.nav-link'); 
  // const contentDiv = document.getElementById('content'); 

  // links.forEach(link => {
  //   link.addEventListener('click', async (e) => {
  //     e.preventDefault(); 
  //     const url = link.dataset.partialUrl;  // data-partial-url を読む

  //     try {
  //       const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
  //       if (res.ok) {
  //         const html = await res.text();
  //         contentDiv.innerHTML = html;
  //         console.log("ページを更新しました:", url);
  //       } else {
  //         console.error("Fetch failed", res.status);
  //       }
  //     } catch (error) {
  //       console.error("Fetch error", error);
  //     }
  //   });
  // });
// });



console.log("hello world"); // 動作確認用

document.addEventListener("DOMContentLoaded", () => {
  console.log("Flaskで動かしています！");

  // GIF移動
  let pos = window.innerWidth;
  const gif = document.getElementById('myGif');
  if (gif) {
    setInterval(() => {
      pos -= 2;
      gif.style.left = pos + 'px';
      if (pos < -gif.width) pos = window.innerWidth;
    }, 30);
  }

    const contentDiv = document.getElementById('content');
  const bgm = document.getElementById('bgm'); // 音楽プレイヤー

  document.addEventListener('click', async (e) => {
    const link = e.target.closest('.nav-link');
    if (!link) return;  // .nav-link以外は無視

    e.preventDefault();
    const url = link.getAttribute('href');
    console.log("リンク名:", url);

    // 音楽が再生中かどうかを記録
    const wasPlaying = !bgm.paused;

    try {
      const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
      if (res.ok) {
        const html = await res.text();
        contentDiv.innerHTML = html;

        if (wasPlaying) {
          bgm.play().catch(() => {
            console.warn("自動再生が制限されています");
          });
        }

        console.log("ページを更新しました:", url);
      } else {
        console.error("Fetch failed", res.status);
      }
    } catch (error) {
      console.error("Fetch error", error);
    }
  });

  // フォーム送信も同様に
  document.addEventListener('submit', async (e) => {
    const form = e.target;
    if (form.tagName.toLowerCase() !== 'form') return;

    e.preventDefault();
    const formData = new FormData(form);
    try {
      const res = await fetch(location.pathname, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      if (res.ok) {
        const html = await res.text();
        contentDiv.innerHTML = html;
        console.log("フォーム送信でページ更新");
      } else {
        console.error("Form fetch failed", res.status);
      }
    } catch (error) {
      console.error("Form fetch error", error);
    }
  });
});

//   const contentDiv = document.getElementById('content');
//   const links = document.querySelectorAll('.nav-link'); // ナビゲーションリンクを非同期化
//   const bgm = document.getElementById('bgm'); // 音楽プレイヤー
  
//   links.forEach(link => {
//     link.addEventListener('click', async (e) => {
//       e.preventDefault();
//       const url = link.getAttribute('href');
//       // const url = link.dataset.partialUrl;  // data-partial-url を読む
//       console.log("リンク名");
//       console.log(url);
//       try {
//         const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
//         if (res.ok) {
//           const html = await res.text();

//           // 音楽が再生中かどうかを記録
//           const wasPlaying = !bgm.paused;

//           contentDiv.innerHTML = html;

//           // 再生中だったら再度再生を試みる
//           if (wasPlaying) {
//             bgm.play().catch(() => {
//               console.warn("自動再生が制限されています");
//             });
//           }
          
//           console.log("ページを更新しました:", url);
//         } else {
//           console.error("Fetch failed", res.status);
//         }
//       } catch (error) {
//         console.error("Fetch error", error);
//       }
//     });
//   });

//   // フォーム送信も非同期化（全てのformを対象）
//   document.addEventListener('submit', async (e) => {
//     const form = e.target;
//     if (form.tagName.toLowerCase() !== 'form') return;

//     e.preventDefault();

//     const formData = new FormData(form);
//     try {
//       const res = await fetch(location.pathname, {
//         method: 'POST',
//         body: formData,
//         headers: { 'X-Requested-With': 'XMLHttpRequest' }
//       });
//       if (res.ok) {
//         const html = await res.text();
//         contentDiv.innerHTML = html;
//         console.log("フォーム送信でページ更新");
//       } else {
//         console.error("Form fetch failed", res.status);
//       }
//     } catch (error) {
//       console.error("Form fetch error", error);
//     }
//   });
// });
