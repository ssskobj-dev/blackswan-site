BlackSwan 申し込みサイト（GitHub Pages用）

index.html      申し込みページ（3プラン・面談予約・Stripe決済・依頼フォームへの導線）
依頼チャット_BlackSwan_CAMPFIRE.txt  CAMPFIRE出品ページをスキルで作るための依頼文
form.html       依頼フォーム（写真アップロード付き。送信先は apps_script.gs）
tokusho.html    特定商取引法に基づく表記
apps_script.gs  依頼フォームの受け口（Google Apps Script に貼る。手順はファイル冒頭）

公開手順
1. GitHub で公開リポジトリを作る（例：blackswan-site）。この4ファイルをアップロード
2. Settings → Pages → Deploy from a branch → main → Save
3. apps_script.gs の手順どおり Google Apps Script を設定し、ウェブアプリURLを form.html の ENDPOINT に貼る
4. Stripe の決済完了ページ（Stripeの設定「決済後の確認ページ」）に、依頼フォームのURL
   https://ユーザー名.github.io/blackswan-site/form.html を入れる

残っている確認事項
- 住所に建物名・部屋番号があれば tokusho.html に追記
