/**
 * Puts each "Report a problem" submission from theimr.org into the data-fix tracker
 * ("00 Tracker perbaikan data (ambil tugas di sini)", Drive folder "09 Perbaikan data"), tab "08 Laporan dari situs".
 *
 * Setup (once, by the tracker's owner):
 *  1. Open the tracker spreadsheet > Extensions > Apps Script. Paste this file. Save.
 *  2. Project Settings > Script properties > add  KEY = a long random word (keep it private).
 *  3. Deploy > New deployment > Web app. Execute as: Me. Who has access: Anyone. Copy the web app URL.
 *  4. Netlify > theimr.org > Forms > Form notifications > Add notification > Outgoing webhook.
 *     Event: New form submission. Form: data-problem. URL: the web app URL + "?k=" + the KEY from step 2.
 *  5. Send a test report from https://theimr.org/report/ and check the new row.
 *
 * The reporter's email address is NOT copied into the tracker (volunteers can open it); it stays in Netlify Forms.
 */
var TAB = '08 Laporan dari situs';
var HEAD = ['No', 'Negara/lembaga', 'Tugas', 'Prioritas', 'Diklaim oleh', 'Tanggal klaim', 'Status', 'Hasil (singkat)', 'Tautan resmi', 'File di Drive', 'Catatan'];
var KIND = {
  wrong: 'Ada yang salah', link: 'Tautan rusak atau tidak resmi', missing: 'Ada yang belum tercatat',
  outdated: 'Hukumnya sudah berubah', translation: 'Masalah terjemahan', other: 'Lainnya'
};

function doPost(e) {
  var key = PropertiesService.getScriptProperties().getProperty('KEY');
  if (!key || !e || !e.parameter || e.parameter.k !== key) return out({ok: false, error: 'key'});
  var body = {};
  try { body = JSON.parse(e.postData.contents); } catch (err) { return out({ok: false, error: 'json'}); }
  if (body.form_name && body.form_name !== 'data-problem') return out({ok: true, skipped: body.form_name});
  var d = body.data || {};
  if (d.website) return out({ok: true, skipped: 'honeypot'});
  var lock = LockService.getScriptLock(); lock.waitLock(20000);
  try {
    var sh = sheet();
    var n = sh.getLastRow(); // header is row 1
    var page = clip(d.page, 300), entry = clip(d.entry, 300);
    var task = '[' + (KIND[d.kind] || d.kind || 'Laporan') + '] ' + clip(d.details, 1500) +
      (page ? '\nHalaman: ' + page : '') + (entry ? '\nEntri: ' + entry : '') +
      '\nTugas: periksa laporan ini dengan sumber resmi; perbaiki data lewat pull request bila benar.';
    sh.appendRow([
      'L-' + ('00' + n).slice(-3), country(entry, page), task,
      (d.kind === 'wrong' || d.kind === 'outdated') ? 1 : 2, '', '', 'Belum', '',
      clip(d.source, 500), '',
      'Masuk ' + Utilities.formatDate(new Date(body.created_at || Date.now()), 'Asia/Jakarta', 'yyyy-MM-dd HH:mm') + ' WIB lewat theimr.org/report' +
        ' (bahasa ' + (d.language || 'en') + '). Pelapor minta dibalas: ' + (d.email ? 'ya, alamat ada di Netlify Forms' : 'tidak') + '.'
    ]);
  } finally { lock.releaseLock(); }
  return out({ok: true});
}

function sheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(TAB);
  if (!sh) {
    sh = ss.insertSheet(TAB);
    sh.appendRow(HEAD); sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEAD.length).setFontWeight('bold');
    sh.setColumnWidth(3, 520);
  }
  return sh;
}

// "gcc|SA|Labour Law" -> "SA"; "/court-decisions/d/ph-..." -> ""; "/compare/?a=ID" -> "ID"
function country(entry, page) {
  var m = /^[a-z-]+\|([A-Z]{2})\|/.exec(entry || '') || /[?&](?:c|a)=([A-Z]{2})\b/.exec(page || '') || /^([A-Z]{2}) \(coverage\)/.exec(entry || '');
  return m ? m[1] : '';
}
function clip(s, n) { s = String(s == null ? '' : s).replace(/^[=+\-@]/, "'$&"); return s.length > n ? s.slice(0, n) + '…' : s; }
function out(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
