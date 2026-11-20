/* Legal Clinic: keep working without internet.

   1. Asks the site's service worker (/sw.js) to save the Clinic's files on this phone,
      so the Clinic opens and works later with no connection.
   2. If "Send to an IMR lawyer" is pressed with no connection, the draft is kept ONLY on
      this phone (IndexedDB 'imr-clinic', store 'outbox'), and is sent to the Clinic's
      usual form address by itself when the phone is online again: by the service worker
      (Background Sync where the browser has it) or by this page on its next visit.
      Once sent, it is deleted from the phone; only its reference number is remembered so
      the page can say "Sent". The person can delete a waiting draft at any time.

   Nothing here sends data anywhere except the Clinic form the page already used.
   Messages are in the Clinic's eight languages (drafts, not yet reviewed by native
   speakers, like the rest of i18n.js). */
(function () {
  var MARKS = 'clinic-outbox', MARK = '/__imr-outbox-waiting';
  var S = {
    en: {
      saved: 'Saved on this phone',
      savedBody: 'There is no internet right now. Your draft (reference {ref}) is kept on this phone and will be sent to the Clinic by itself when the phone is online again. You can close this page.',
      waiting: 'A draft is waiting on this phone (reference {ref}). It will be sent to the Clinic by itself when you are online.',
      sendNow: 'Try to send now', del: 'Delete it from this phone', delSure: 'Press again to delete',
      deleted: 'Deleted from this phone.', sent: 'Sent. The Clinic has received your draft (reference {ref}). An officer will contact you.',
      ready: 'This page now works on this phone without internet.',
      offlineNote: 'No internet? The form is then kept only on this phone until it can be sent, and is deleted from the phone once it is sent.'
    },
    id: {
      saved: 'Tersimpan di ponsel ini',
      savedBody: 'Saat ini tidak ada internet. Draf anda (nomor referensi {ref}) disimpan di ponsel ini dan akan terkirim sendiri ke Klinik begitu ponsel tersambung ke internet lagi. Anda boleh menutup halaman ini.',
      waiting: 'Ada draf yang menunggu di ponsel ini (nomor referensi {ref}). Draf tersebut akan terkirim sendiri ke Klinik begitu anda tersambung ke internet.',
      sendNow: 'Coba kirim sekarang', del: 'Hapus dari ponsel ini', delSure: 'Tekan sekali lagi untuk menghapus',
      deleted: 'Sudah dihapus dari ponsel ini.', sent: 'Terkirim. Klinik telah menerima draf anda (nomor referensi {ref}). Petugas kami akan menghubungi anda.',
      ready: 'Halaman ini sekarang bisa dibuka di ponsel ini tanpa internet.',
      offlineNote: 'Tidak ada internet? Formulir akan disimpan hanya di ponsel ini sampai bisa dikirim, lalu dihapus dari ponsel setelah terkirim.'
    },
    ar: {
      saved: 'محفوظ على هذا الهاتف',
      savedBody: 'لا يوجد اتصال بالإنترنت الآن. مسودتك (الرقم المرجعي {ref}) محفوظة على هذا الهاتف، وستُرسل إلى العيادة تلقائيًا عند عودة الاتصال. يمكنك إغلاق هذه الصفحة.',
      waiting: 'هناك مسودة تنتظر على هذا الهاتف (الرقم المرجعي {ref}). ستُرسل إلى العيادة تلقائيًا عند الاتصال بالإنترنت.',
      sendNow: 'حاول الإرسال الآن', del: 'احذفها من هذا الهاتف', delSure: 'اضغط مرة أخرى للحذف',
      deleted: 'حُذفت من هذا الهاتف.', sent: 'أُرسلت. استلمت العيادة مسودتك (الرقم المرجعي {ref}). سيتواصل معك أحد الموظفين.',
      ready: 'تعمل هذه الصفحة الآن على هذا الهاتف دون إنترنت.',
      offlineNote: 'لا يوجد إنترنت؟ يُحفظ النموذج على هذا الهاتف فقط حتى يمكن إرساله، ثم يُحذف من الهاتف بعد الإرسال.'
    },
    fa: {
      saved: 'روی این گوشی ذخیره شد',
      savedBody: 'الان اینترنت وصل نیست. پیش‌نویس شما (شماره پیگیری {ref}) روی این گوشی نگه داشته می‌شود و وقتی گوشی دوباره به اینترنت وصل شد، خودبه‌خود برای کلینیک فرستاده می‌شود. می‌توانید این صفحه را ببندید.',
      waiting: 'یک پیش‌نویس روی این گوشی منتظر است (شماره پیگیری {ref}). وقتی به اینترنت وصل شوید، خودبه‌خود برای کلینیک فرستاده می‌شود.',
      sendNow: 'همین حالا ارسال کن', del: 'از این گوشی پاک کن', delSure: 'برای پاک کردن دوباره بزنید',
      deleted: 'از این گوشی پاک شد.', sent: 'ارسال شد. کلینیک پیش‌نویس شما را دریافت کرد (شماره پیگیری {ref}). یکی از کارکنان با شما تماس می‌گیرد.',
      ready: 'این صفحه اکنون روی این گوشی بدون اینترنت هم کار می‌کند.',
      offlineNote: 'اینترنت ندارید؟ فرم فقط روی این گوشی نگه داشته می‌شود تا بتوان آن را فرستاد، و پس از ارسال از گوشی پاک می‌شود.'
    },
    bn: {
      saved: 'এই ফোনে সংরক্ষিত',
      savedBody: 'এখন ইন্টারনেট নেই। আপনার খসড়া (রেফারেন্স {ref}) এই ফোনে রাখা আছে, ফোনে আবার ইন্টারনেট এলে এটি নিজে থেকেই ক্লিনিকে পাঠানো হবে। আপনি এই পাতা বন্ধ করতে পারেন।',
      waiting: 'এই ফোনে একটি খসড়া অপেক্ষা করছে (রেফারেন্স {ref})। ইন্টারনেট এলে এটি নিজে থেকেই ক্লিনিকে পাঠানো হবে।',
      sendNow: 'এখনই পাঠানোর চেষ্টা করুন', del: 'এই ফোন থেকে মুছুন', delSure: 'মুছতে আবার চাপুন',
      deleted: 'এই ফোন থেকে মুছে ফেলা হয়েছে।', sent: 'পাঠানো হয়েছে। ক্লিনিক আপনার খসড়া পেয়েছে (রেফারেন্স {ref})। একজন কর্মকর্তা আপনার সঙ্গে যোগাযোগ করবেন।',
      ready: 'এই পাতা এখন এই ফোনে ইন্টারনেট ছাড়াও চলে।',
      offlineNote: 'ইন্টারনেট নেই? তাহলে ফর্মটি পাঠানো না যাওয়া পর্যন্ত শুধু এই ফোনে রাখা থাকে, আর পাঠানো হলে ফোন থেকে মুছে যায়।'
    },
    ne: {
      saved: 'यो फोनमा सुरक्षित गरियो',
      savedBody: 'अहिले इन्टरनेट छैन। तपाईंको मस्यौदा (सन्दर्भ नम्बर {ref}) यो फोनमा राखिएको छ, र फोनमा फेरि इन्टरनेट आएपछि आफैं क्लिनिकमा पठाइनेछ। तपाईं यो पेज बन्द गर्न सक्नुहुन्छ।',
      waiting: 'यो फोनमा एउटा मस्यौदा पर्खिरहेको छ (सन्दर्भ नम्बर {ref})। इन्टरनेट आएपछि यो आफैं क्लिनिकमा पठाइनेछ।',
      sendNow: 'अहिले पठाउने प्रयास गर्नुहोस्', del: 'यो फोनबाट मेटाउनुहोस्', delSure: 'मेटाउन फेरि थिच्नुहोस्',
      deleted: 'यो फोनबाट मेटाइयो।', sent: 'पठाइयो। क्लिनिकले तपाईंको मस्यौदा पायो (सन्दर्भ नम्बर {ref})। एक जना अधिकारीले तपाईंलाई सम्पर्क गर्नुहुनेछ।',
      ready: 'यो पेज अब यो फोनमा इन्टरनेट बिना पनि चल्छ।',
      offlineNote: 'इन्टरनेट छैन? फारम पठाउन नसकेसम्म यो फोनमा मात्र राखिन्छ, र पठाएपछि फोनबाट मेटाइन्छ।'
    },
    tl: {
      saved: 'Naka-save sa teleponong ito',
      savedBody: 'Walang internet ngayon. Ang iyong draft (reference {ref}) ay nakatago sa teleponong ito at kusang ipapadala sa Clinic kapag may internet na ulit. Puwede mo nang isara ang pahinang ito.',
      waiting: 'May draft na naghihintay sa teleponong ito (reference {ref}). Kusa itong ipapadala sa Clinic kapag may internet ka na.',
      sendNow: 'Subukang ipadala ngayon', del: 'Burahin sa teleponong ito', delSure: 'Pindutin ulit para burahin',
      deleted: 'Nabura na sa teleponong ito.', sent: 'Naipadala na. Natanggap ng Clinic ang iyong draft (reference {ref}). Kokontakin ka ng isang opisyal.',
      ready: 'Gumagana na ang pahinang ito sa teleponong ito kahit walang internet.',
      offlineNote: 'Walang internet? Itatago lang ang form sa teleponong ito hanggang maipadala, at buburahin sa telepono kapag naipadala na.'
    },
    vi: {
      saved: 'Đã lưu trên điện thoại này',
      savedBody: 'Hiện không có internet. Bản nháp của bạn (mã hồ sơ {ref}) được giữ trên điện thoại này và sẽ tự động gửi đến Phòng tư vấn khi điện thoại có internet trở lại. Bạn có thể đóng trang này.',
      waiting: 'Có một bản nháp đang chờ trên điện thoại này (mã hồ sơ {ref}). Bản nháp sẽ tự động được gửi khi bạn có internet.',
      sendNow: 'Thử gửi ngay', del: 'Xóa khỏi điện thoại này', delSure: 'Nhấn lần nữa để xóa',
      deleted: 'Đã xóa khỏi điện thoại này.', sent: 'Đã gửi. Phòng tư vấn đã nhận bản nháp của bạn (mã hồ sơ {ref}). Một cán bộ sẽ liên hệ với bạn.',
      ready: 'Trang này giờ đã dùng được trên điện thoại này khi không có internet.',
      offlineNote: 'Không có internet? Biểu mẫu sẽ chỉ được giữ trên điện thoại này cho đến khi gửi được, và sẽ bị xóa khỏi điện thoại sau khi gửi.'
    }
  };
  function lang() {
    var b = document.querySelector('#langs [aria-pressed="true"]');
    var l = (b && b.dataset.lang) || (function () { try { return localStorage.getItem('imr-clinic-lang'); } catch (e) { return null; } })() || 'en';
    return S[l] ? l : 'en';
  }
  function t(k, ref) { var l = lang(); return (S[l][k] || S.en[k]).replace('{ref}', ref || ''); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); }

  // ---------- storage ----------
  function db() {
    return new Promise(function (resolve, reject) {
      if (!window.indexedDB) return reject(new Error('no indexedDB'));
      var r = indexedDB.open('imr-clinic', 1);
      r.onupgradeneeded = function () {
        var d = r.result;
        if (!d.objectStoreNames.contains('outbox')) d.createObjectStore('outbox', {keyPath: 'ref'});
        if (!d.objectStoreNames.contains('sent')) d.createObjectStore('sent', {keyPath: 'ref'});
      };
      r.onsuccess = function () { resolve(r.result); };
      r.onerror = function () { reject(r.error); };
    });
  }
  function tx(store, mode, fn) {
    return db().then(function (d) {
      return new Promise(function (resolve, reject) {
        var t = d.transaction(store, mode), out;
        Promise.resolve(fn(t.objectStore(store))).then(function (v) { out = v; });
        t.oncomplete = function () { resolve(out && out.result !== undefined ? out.result : out); };
        t.onerror = function () { reject(t.error); };
      });
    });
  }
  function mark(on) {
    if (!window.caches) return Promise.resolve();
    return caches.open(MARKS).then(function (c) { return on ? c.put(MARK, new Response('1')) : c.delete(MARK); }).catch(function () {});
  }
  function hasWaiting() { return window.caches ? caches.open(MARKS).then(function (c) { return c.match(MARK); }).then(Boolean).catch(function () { return false; }) : Promise.resolve(false); }

  // FormData cannot be stored directly: keep it as [name, value, filename] rows.
  function save(ref, fd) {
    var fields = [];
    fd.forEach(function (v, k) { fields.push(v instanceof Blob ? [k, v, v.name || 'file'] : [k, v]); });
    return tx('outbox', 'readwrite', function (s) { s.put({ref: ref, created: Date.now(), fields: fields}); })
      .then(function () { return mark(true); })
      .then(function () {
        if (navigator.serviceWorker && navigator.serviceWorker.ready) {
          navigator.serviceWorker.ready.then(function (reg) { if (reg.sync) return reg.sync.register('imr-clinic-outbox'); }).catch(function () {});
        }
      });
  }
  function list(store) { return tx(store || 'outbox', 'readonly', function (s) { return s.getAll(); }).then(function (r) { return r || []; }); }
  function remove(ref) {
    return tx('outbox', 'readwrite', function (s) { s.delete(ref); }).then(function () {
      return list().then(function (l) { if (!l.length) return mark(false); });
    });
  }
  // One sender at a time: the service worker if it controls this page, otherwise this page.
  var busy = null;
  function sendAll() {
    var sw = navigator.serviceWorker && navigator.serviceWorker.controller;
    if (sw) { sw.postMessage({type: 'flush-outbox'}); return Promise.resolve(); }
    if (busy) return busy;
    busy = pageSend().then(function () { busy = null; }, function () { busy = null; });
    return busy;
  }
  function pageSend() {
    return list().then(function (items) {
      return items.reduce(function (p, item) {
        return p.then(function () {
          var fd = new FormData();
          item.fields.forEach(function (f) { if (f[2]) fd.append(f[0], f[1], f[2]); else fd.append(f[0], f[1]); });
          return fetch('/', {method: 'POST', body: fd}).then(function (r) {
            if (!r.ok) return;
            return db().then(function (d) {
              return new Promise(function (resolve) {
                var t = d.transaction(['outbox', 'sent'], 'readwrite');
                t.objectStore('outbox').delete(item.ref);
                // Shown on this page now, so not needed for the next visit.
                t.objectStore('sent').delete(item.ref);
                t.oncomplete = t.onerror = function () { resolve(); };
              });
            }).then(function () { showSent(item.ref); });
          }).catch(function () {});
        });
      }, Promise.resolve());
    }).then(function () { return list().then(function (l) { if (!l.length) return mark(false); }); });
  }

  // ---------- messages on the page ----------
  function box() {
    var b = document.getElementById('imr-outbox');
    if (!b) {
      b = document.createElement('div'); b.id = 'imr-outbox'; b.className = 'imr-outbox';
      b.setAttribute('role', 'status'); b.setAttribute('data-noi18n', '');
      var at = document.getElementById('rail') || document.querySelector('main') || document.body.firstElementChild;
      at.parentNode.insertBefore(b, at);
      var css = document.createElement('style');
      css.textContent = '.imr-outbox{max-width:812px;margin:16px auto;padding:14px 18px;border-left:5px solid currentColor;background:#fff;color:#172D24;font:17px/1.5 "Figtree",system-ui,sans-serif;box-sizing:border-box}.imr-outbox:empty{display:none}.imr-outbox b{display:block;font-size:19px;margin-bottom:4px}.imr-outbox .ob-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:10px}.imr-outbox button{font:600 16px/1 "Figtree",system-ui,sans-serif;min-height:44px;padding:0 16px;border-radius:6px;border:2px solid #172D24;background:#fff;color:#172D24;cursor:pointer}.imr-outbox button.ob-send{background:#172D24;color:#fff}.imr-outbox .ob-item+.ob-item{margin-top:12px;padding-top:12px;border-top:1px solid #B2C7BC}';
      document.head.appendChild(css);
    }
    return b;
  }
  function itemHTML(ref, title, body) {
    return '<div class="ob-item" data-ref="' + esc(ref) + '">' + (title ? '<b>' + esc(title) + '</b>' : '') + '<span>' + esc(body) + '</span>' +
      '<div class="ob-row"><button type="button" class="ob-send">' + esc(t('sendNow')) + '</button><button type="button" class="ob-del">' + esc(t('del')) + '</button></div></div>';
  }
  function paint() {
    return list().then(function (items) {
      var b = box(), keep = Array.prototype.filter.call(b.querySelectorAll('.ob-note'), function () { return true; });
      b.innerHTML = items.map(function (i) { return itemHTML(i.ref, '', t('waiting', i.ref)); }).join('');
      keep.forEach(function (n) { b.appendChild(n); });
    }).catch(function () {});
  }
  function note(text) { var b = box(), n = document.createElement('p'); n.className = 'ob-note'; n.style.margin = '6px 0 0'; n.textContent = text; b.appendChild(n); }
  function showSent(ref) {
    paint().then(function () { note(t('sent', ref)); });
    var f = document.getElementById('sendfail'); if (f && f.dataset.queued === ref) { f.hidden = true; }
  }
  // Tell the person about drafts sent since their last visit, once.
  function sentSinceLastVisit() {
    return list('sent').then(function (rows) {
      if (!rows.length) return;
      rows.forEach(function (r) { note(t('sent', r.ref)); });
      return tx('sent', 'readwrite', function (s) { s.clear(); });
    }).catch(function () {});
  }

  document.addEventListener('click', function (e) {
    var it = e.target.closest('.imr-outbox .ob-item, #sendfail [data-ref]'); if (!it) return;
    var ref = it.dataset.ref;
    if (e.target.closest('.ob-send')) { sendAll().then(paint); }
    if (e.target.closest('.ob-del')) {
      var btn = e.target.closest('.ob-del');
      if (btn.dataset.sure !== '1') { btn.dataset.sure = '1'; btn.textContent = t('delSure'); return; }
      remove(ref).then(function () { if (it.closest('#sendfail')) it.closest('#sendfail').hidden = true; return paint(); }).then(function () { note(t('deleted')); });
    }
  });

  // Called by the Clinic form when sending failed for lack of a connection.
  function queue(ref, fd) {
    return save(ref, fd).then(function () {
      var f = document.getElementById('sendfail');
      if (f) {
        f.hidden = false; f.dataset.queued = ref; f.setAttribute('role', 'status');
        f.innerHTML = '<div data-ref="' + esc(ref) + '"><b>' + esc(t('saved')) + '</b> ' + esc(t('savedBody', ref)) +
          '<div class="ob-row" style="display:flex;flex-wrap:wrap;gap:10px;margin-top:10px"><button type="button" class="b2 ob-send">' + esc(t('sendNow')) + '</button><button type="button" class="b2 ob-del">' + esc(t('del')) + '</button></div></div>';
        f.focus && f.setAttribute('tabindex', '-1'); f.focus && f.focus();
      }
      return true;
    });
  }

  window.IMROutbox = {queue: queue, sendAll: sendAll, list: list, remove: remove};

  function start() {
    // Privacy line under the form: say what happens without internet.
    var pv = document.querySelector('#intake .privacy');
    if (pv && !document.getElementById('ob-privacy')) { var p = document.createElement('p'); p.id = 'ob-privacy'; p.className = 'privacy'; p.setAttribute('data-noi18n', ''); p.textContent = t('offlineNote'); pv.insertAdjacentElement('afterend', p); }
    document.addEventListener('click', function (e) { if (e.target.closest('#langs [data-lang]')) setTimeout(function () { var p = document.getElementById('ob-privacy'); if (p) p.textContent = t('offlineNote'); paint(); }, 0); });
    hasWaiting().then(function (w) { if (w) { paint(); if (navigator.onLine) sendAll().then(paint); } });
    sentSinceLastVisit();
    window.addEventListener('online', function () { hasWaiting().then(function (w) { if (w) sendAll().then(paint); }); });
    if (navigator.serviceWorker) {
      navigator.serviceWorker.addEventListener('message', function (e) { if (e.data && e.data.type === 'clinic-sent') showSent(e.data.ref); });
      // Save the Clinic for offline use (small: the page, its scripts and the font).
      navigator.serviceWorker.ready.then(function (reg) {
        if (!reg.active) return;
        var lite = !!(navigator.connection && navigator.connection.saveData);
        reg.active.postMessage({type: 'save-clinic', lite: lite});
        try { if (!localStorage.getItem('imr-clinic-offline')) { localStorage.setItem('imr-clinic-offline', '1'); setTimeout(function () { var h = document.querySelector('.helpline'); if (h && !document.getElementById('ob-ready')) { var p = document.createElement('p'); p.id = 'ob-ready'; p.className = 'helpline'; p.setAttribute('data-noi18n', ''); p.setAttribute('role', 'status'); p.textContent = '✓ ' + t('ready'); h.insertAdjacentElement('afterend', p); } }, 1500); } } catch (e) {}
      }).catch(function () {});
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
