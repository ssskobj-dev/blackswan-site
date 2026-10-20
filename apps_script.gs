/**
 * BlackSwan 依頼フォームの受け口（Google Apps Script・無料）
 *
 * 役割：form.html から送られた内容を
 *   1) スプレッドシートに1行追加（件数管理に使う）
 *   2) Googleドライブに「依頼日_商品名」フォルダを作って写真を保存
 *   3) あなたにメールで通知（内容＋フォルダのリンク）
 *   4) 同じメールアドレスの今月の件数が上限を超えていたら、受け付けずにエラーを返す
 *
 * 設定手順（10分）
 *  1. Googleドライブで「BlackSwan依頼」フォルダを作り、URLの末尾のID（/folders/の後ろ）を FOLDER_ID に貼る
 *  2. 新しいスプレッドシートを作り、URLの /d/ と /edit の間のIDを SHEET_ID に貼る
 *  3. script.google.com → 新しいプロジェクト → このコードを全部貼る → 保存
 *  4. 右上「デプロイ」→「新しいデプロイ」→ 種類「ウェブアプリ」
 *     次のユーザーとして実行：自分 ／ アクセスできるユーザー：全員 → デプロイ
 *  5. 表示された「ウェブアプリのURL」を form.html の ENDPOINT に貼る
 *  ※ コードを直したら、もう一度「デプロイ」→「デプロイを管理」→ 新しいバージョンにする
 */

const FOLDER_ID = '【ドライブのフォルダID】';
const SHEET_ID  = '【スプレッドシートのID】';
const NOTIFY_TO = 'head.sourcing@longevity-ooo.com';
// プランごとの月間上限。「契約」シート（メール／プラン／上限）があればそちらを優先する
const PLAN_LIMITS = { 'ライト': 2, 'スタンダード': 6, 'プロ': 15, 'クラファン': 6 };
const DEFAULT_LIMIT = 6;

function doPost(e) {
  try {
    const d = JSON.parse(e.postData.contents);
    const email = String(d.email || '').trim().toLowerCase();
    if (!email || !d.product) return out({ ok: false, error: 'missing' });

    const sheet = getSheet();
    const limit = limitFor(email, d.plan);
    const used = countThisMonth(sheet, email);
    if (used >= limit) {
      MailApp.sendEmail(NOTIFY_TO, `[BlackSwan] 上限超過の依頼 ${email}`, `今月 ${used} 件（上限 ${limit}）を超える依頼がありました。\n商品：${d.product}\nプラン：${d.plan}\n追加1件かプラン変更を案内してください。`);
      return out({ ok: false, error: 'limit' });
    }

    // ドライブにフォルダを作って写真を保存
    const root = DriveApp.getFolderById(FOLDER_ID);
    const stamp = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyyMMdd_HHmm');
    const folder = root.createFolder(`${stamp}_${d.product}`.replace(/[\/\\:*?"<>|]/g, '_'));
    (d.files || []).forEach(f => {
      const blob = Utilities.newBlob(Utilities.base64Decode(f.data), f.type || 'application/octet-stream', f.name);
      folder.createFile(blob);
    });
    // フォーム内容もテキストで保存（制作時にそのまま読める）
    folder.createFile('依頼フォーム.txt', toForm(d), 'text/plain');

    // シートに記録
    sheet.appendRow([new Date(), email, d.name, d.product, d.platform, used + 1, folder.getUrl(), d.format, d.publish, 'received', d.plan || '', limit]);

    // 通知
    MailApp.sendEmail({
      to: NOTIFY_TO,
      subject: `[BlackSwan] 新規依頼 ${d.product}（${email} 今月${used + 1}/${limit}件）`,
      body: toForm(d) + `\n\nフォルダ：${folder.getUrl()}`
    });
    // 依頼者に受付メール
    MailApp.sendEmail({
      to: email,
      subject: `【BlackSwan】依頼を受け付けました：${d.product}`,
      body: `${d.name} 様\n\n依頼を受け付けました。翌営業日を目安に、スライドのリンクをこのメールアドレスへお送りします。\n（今月 ${used + 1} 件目／上限 ${limit} 件）\n\n初稿をそのまま納品します。文字・色・順番の調整はスライド上でお願いします。当方の誤字や転記ミスは、納品から7日以内にご連絡ください。\n\nBlackSwan ／ Spacify合同会社`
    });
    return out({ ok: true, count: used + 1 });
  } catch (err) {
    return out({ ok: false, error: String(err) });
  }
}

// 上限の決め方：「契約」シート（A:メール B:プラン C:上限）に行があればそれ。なければフォームで選んだプラン名から。
function limitFor(email, plan) {
  try {
    const ss = SpreadsheetApp.openById(SHEET_ID);
    const c = ss.getSheetByName('契約');
    if (c) {
      const rows = c.getDataRange().getValues().slice(1);
      const hit = rows.find(r => String(r[0]).toLowerCase() === email);
      if (hit && Number(hit[2]) > 0) return Number(hit[2]);
    }
  } catch (e) {}
  const key = Object.keys(PLAN_LIMITS).find(k => String(plan || '').indexOf(k) === 0);
  return key ? PLAN_LIMITS[key] : DEFAULT_LIMIT;
}

function getSheet() {
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let s = ss.getSheetByName('依頼');
  if (!s) { s = ss.insertSheet('依頼'); s.appendRow(['日時', 'メール', '名前', '商品', '掲載先', '今月件数', 'フォルダ', '納品形式', '公開可否', '状態', 'プラン', '上限']); }
  return s;
}

function countThisMonth(sheet, email) {
  const rows = sheet.getDataRange().getValues().slice(1);
  const now = new Date(), y = now.getFullYear(), m = now.getMonth();
  return rows.filter(r => r[0] instanceof Date && r[0].getFullYear() === y && r[0].getMonth() === m && String(r[1]).toLowerCase() === email).length;
}

function toForm(d) {
  const L = [
    ['ご契約プラン', 'plan'], ['商品・サービス名', 'product'], ['一言で言うと', 'oneliner'], ['カテゴリ', 'category'], ['掲載先', 'platform'],
    ['ターゲット', 'target'], ['独自性', 'usp'], ['数字で言えること＋根拠', 'numbers'], ['仕様', 'spec'], ['使い方・使うシーン', 'usage'],
    ['一般販売予定価格', 'list_price'], ['リターン', 'returns'], ['お届け予定', 'delivery'],
    ['ストーリー', 'story'], ['リスク・注意事項', 'risks'], ['FAQにしたい質問', 'faq'], ['好みの方向', 'style'],
    ['写真の切り抜き', 'cutout'], ['共有フォルダURL', 'photos_url'], ['納品形式', 'format'], ['制作例として公開', 'publish'], ['その他', 'memo']
  ];
  return [`【依頼者】${d.name}（${d.email}）`, ...L.map(([k, v]) => `【${k}】${d[v] || ''}`)].join('\n');
}

function out(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
