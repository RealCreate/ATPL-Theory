/* ATPL Theory · single-page app (no build step). Routes:
   #/            subjects
   #/s/050       subject outline
   #/lo/<ref>    learning objective reader
   #/b/050       study text contents
   #/b/050/<n>   study text chapter (optional ?lo=<ref> scrolls to that objective) */
(() => {
  "use strict";

  const COLORS = {
    "010": ["#5e5ce6", "#3634a3"], "021": ["#ff9f0a", "#c93400"], "022": ["#30b0c7", "#0e6f80"],
    "031": ["#ac8e68", "#7f6545"], "032": ["#34c759", "#1f8a3c"], "033": ["#00c7be", "#0a7d78"],
    "040": ["#ff375f", "#c4173d"], "050": ["#0a84ff", "#0040dd"], "061": ["#bf5af2", "#8944ab"],
    "062": ["#ff453a", "#b8261c"], "070": ["#ffb800", "#c27c00"], "081": ["#5ac8fa", "#0071a4"],
    "090": ["#8e8e93", "#545458"],
  };
  const S = 'fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"';
  const ICONS = {
    "010": `<svg viewBox="0 0 24 24" ${S}><path d="M12 3v18M7 21h10M4 7h16M12 5l0 2"/><path d="M6.5 7 3.5 14a3 3 0 0 0 6 0L6.5 7zM17.5 7l-3 7a3 3 0 0 0 6 0l-3-7z"/></svg>`,
    "021": `<svg viewBox="0 0 24 24" ${S}><circle cx="12" cy="12" r="3.2"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/></svg>`,
    "022": `<svg viewBox="0 0 24 24" ${S}><circle cx="12" cy="13" r="8.5"/><path d="M12 13l4.5-4.5M7 13h1M16 13h1M12 7.5v1"/><circle cx="12" cy="13" r="1" fill="currentColor"/></svg>`,
    "031": `<svg viewBox="0 0 24 24" ${S}><circle cx="12" cy="5.5" r="2.2"/><path d="M6.2 8.5h11.6l2.4 12H3.8z"/></svg>`,
    "032": `<svg viewBox="0 0 24 24" ${S}><path d="M3.5 3.5v17h17"/><path d="M7 15.5l4-4.5 3 3 5.5-6.5"/><path d="M15.5 7.5h4v4"/></svg>`,
    "033": `<svg viewBox="0 0 24 24" ${S}><circle cx="6" cy="18.5" r="2"/><circle cx="18" cy="5.5" r="2"/><path d="M8 18.5h7.5a3 3 0 0 0 0-6h-7a3 3 0 0 1 0-6H16"/></svg>`,
    "040": `<svg viewBox="0 0 24 24" ${S}><path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/></svg>`,
    "050": `<svg viewBox="0 0 24 24" ${S}><path d="M7 18.5a4.5 4.5 0 0 1-.4-8.98A6 6 0 0 1 18.2 10 4.3 4.3 0 0 1 17.5 18.5z"/></svg>`,
    "061": `<svg viewBox="0 0 24 24" ${S}><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.6 3.8 5.6 3.8 9s-1.2 6.4-3.8 9c-2.6-2.6-3.8-5.6-3.8-9S9.4 5.6 12 3z"/></svg>`,
    "062": `<svg viewBox="0 0 24 24" ${S}><circle cx="12" cy="10" r="1.8"/><path d="M12 12v9M8.5 21h7M8.3 6.3a5.2 5.2 0 0 0 0 7.4M15.7 6.3a5.2 5.2 0 0 1 0 7.4M5.4 3.4a9.3 9.3 0 0 0 0 13.2M18.6 3.4a9.3 9.3 0 0 1 0 13.2"/></svg>`,
    "070": `<svg viewBox="0 0 24 24" ${S}><rect x="5" y="4" width="14" height="17" rx="2.2"/><path d="M9 4V2.8h6V4M8.8 11.5l2 2 4.4-4.4M9 17h6"/></svg>`,
    "081": `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M21 15.5v-2l-8-5V3.6a1.5 1.5 0 0 0-3 0v4.9l-8 5v2l8-2.5v5.4l-2 1.5V21l3.5-1 3.5 1v-1.1l-2-1.5V13z"/></svg>`,
    "090": `<svg viewBox="0 0 24 24" ${S}><path d="M3.5 15v-3a8.5 8.5 0 0 1 17 0v3"/><path d="M3.5 14.5h3v6h-1.5a1.5 1.5 0 0 1-1.5-1.5zM20.5 14.5h-3v6H19a1.5 1.5 0 0 0 1.5-1.5z"/></svg>`,
  };
  const CHEV = '<svg class="chev" viewBox="0 0 8 14" aria-hidden="true"><path d="M1.5 1.5 6.5 7l-5 5.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const DISC = '<svg class="disc" viewBox="0 0 10 10" aria-hidden="true"><path d="M3 1.5 6.8 5 3 8.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const TICK = '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 6.3 5 8.6l4.6-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  const $ = (s, el = document) => el.querySelector(s);
  const main = $("#main"), side = $("#side"), layout = $("#layout"), bar = $("#bar");
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const tile = (code, cls = "") => `<div class="tile ${cls}" style="background:linear-gradient(160deg,${COLORS[code][0]},${COLORS[code][1]})">${ICONS[code]}</div>`;
  const loTitle = (lo) => lo.title || lo.lo;

  /* ---------- storage ---------- */
  const store = {
    get(k, d) { try { const v = localStorage.getItem("atpl." + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem("atpl." + k, JSON.stringify(v)); } catch {} },
  };
  const studied = new Set(store.get("studied", []));
  const saveStudied = () => store.set("studied", [...studied]);
  const openChapters = new Set(store.get("open", []));
  const saveOpen = () => store.set("open", [...openChapters]);

  /* ---------- data ---------- */
  let SUBJECTS = null;
  const cache = new Map();
  async function getJSON(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error(url + " " + r.status);
    return r.json();
  }
  async function subjects() { return SUBJECTS ||= await getJSON("data/subjects.json"); }
  async function subject(code) {
    if (cache.has(code)) return cache.get(code);
    const d = await getJSON(`data/${code}.json`);
    // flatten for prev/next + lookups
    d.flat = [];
    d.chapters.forEach((ch, ci) => ch.subs.forEach((sb) => sb.topics.forEach((tp) => tp.los.forEach((lo) => {
      lo.ch = ci; lo.sub = sb; lo.topic = tp; lo.i = d.flat.length; d.flat.push(lo);
    }))));
    d.byRef = new Map(d.flat.map((l) => [l.ref, l]));
    cache.set(code, d);
    return d;
  }
  const countDone = (refs) => refs.reduce((n, r) => n + (studied.has(r) ? 1 : 0), 0);
  const books = new Map();
  async function book(code) {
    if (books.has(code)) return books.get(code);
    const b = await getJSON(`data/book-${code}.json`);
    b.chapterOf = new Map();
    b.chapters.forEach((c) => c.refs.forEach((r) => { if (!b.chapterOf.has(r)) b.chapterOf.set(r, c.n); }));
    books.set(code, b);
    return b;
  }
  const BOOK_IC = `<svg viewBox="0 0 24 24" ${S}><path d="M3 5.5C5.5 4 8.5 4 12 6c3.5-2 6.5-2 9-.5V19c-2.5-1.5-5.5-1.5-9 .5-3.5-2-6.5-2-9-.5z"/><path d="M12 6v13.5"/></svg>`;

  /* ---------- chrome ---------- */
  let backHref = null;
  function setBar({ title = "", back = null, backLabel = "" } = {}) {
    $("#barTitle").textContent = title;
    backHref = back;
    $("#back").hidden = !back;
    $("#backLabel").textContent = backLabel;
    document.title = title ? `${title} · ATPL Theory` : "ATPL Theory";
    onScroll();
  }
  $("#back").addEventListener("click", () => { if (backHref) location.hash = backHref; });
  function onScroll() {
    const y = window.scrollY;
    bar.classList.toggle("scrolled", y > 4);
    const big = $(".large h1, .hero h1, .reader h1", main);
    bar.classList.toggle("show-title", !!big && big.getBoundingClientRect().bottom < 60);
  }
  window.addEventListener("scroll", onScroll, { passive: true });

  function ring(pct, c) {
    const r = 19, L = 2 * Math.PI * r;
    return `<svg class="ring" viewBox="0 0 44 44" style="--c:${c}"><circle class="trk" cx="22" cy="22" r="${r}"/><circle class="val" cx="22" cy="22" r="${r}" stroke-dasharray="${L}" stroke-dashoffset="${L * (1 - pct)}"/></svg>`;
  }

  /* ---------- views ---------- */
  async function viewHome() {
    layout.classList.remove("with-side");
    setBar({ title: "ATPL Theory" });
    const subs = await subjects();
    const total = subs.reduce((n, s) => n + s.los, 0);
    const doneAll = studied.size;
    const last = store.get("last", null), lastBook = store.get("lastBook", null);
    let cont = "";
    if (lastBook && (!last || (lastBook.ts || 0) >= (last.ts || 0))) {
      const s = subs.find((x) => x.code === lastBook.code);
      if (s) cont = `<a class="continue" href="#/b/${esc(lastBook.code)}/${lastBook.n}">${tile(lastBook.code)}<div class="txt"><div class="k">Continue reading</div><div class="t">${esc(lastBook.title)}</div><div class="s">${esc(s.code)} ${esc(s.name)} · study text</div></div>${CHEV}</a>`;
    } else if (last) {
      const s = subs.find((x) => x.code === last.code);
      if (s) cont = `<a class="continue" href="#/lo/${esc(last.ref)}">${tile(last.code)}<div class="txt"><div class="k">Continue reading</div><div class="t">${esc(last.title)}</div><div class="s">${esc(s.code)} ${esc(s.name)} · ${esc(last.ref)}</div></div>${CHEV}</a>`;
    }
    main.innerHTML = `<div class="wrap">
      <div class="large"><h1>ATPL Theory</h1><p>EASA ATPL(A) · 13 subjects · ${total.toLocaleString()} learning objectives · Syllabus v6 (ECQB 2026)</p></div>
      ${cont}
      <div class="overall">${ring(total ? doneAll / total : 0, "var(--green)")}<div class="meta"><div class="k">Studied overall</div><div class="v">${doneAll.toLocaleString()} <span style="color:var(--label-2);font-weight:500;font-size:17px">of ${total.toLocaleString()}</span></div></div></div>
      <div class="section-h">Subjects</div>
      <div class="grid">${subs.map((s) => card(s)).join("")}</div>
      <p class="foot">Theory written against the official EASA learning objectives. Tick objectives as you study them; progress stays on this device.</p>
    </div>`;
    requestAnimationFrame(() => main.querySelectorAll(".bar-prog i").forEach((i) => (i.style.width = i.dataset.w)));
  }
  function card(s) {
    const prefix = s.code + ".";
    let done = 0;
    for (const r of studied) if (r.startsWith(prefix)) done++;
    const pct = s.los ? (done / s.los) * 100 : 0;
    const badge = s.book ? '<span class="badge full">Study text</span>' : s.theory >= s.los ? '<span class="badge full">Full theory</span>' : s.theory ? `<span class="badge">${s.theory} with theory</span>` : '<span class="badge">Syllabus</span>';
    return `<a class="card" href="#/s/${s.code}" style="--c:${COLORS[s.code][0]}">
      <div class="card-top">${tile(s.code)}<div><div class="code">${s.code}</div><div class="name">${esc(s.name)}</div></div></div>
      <div class="blurb">${esc(s.blurb)}</div>
      <div class="card-foot"><div class="bar-prog"><i data-w="${pct.toFixed(1)}%"></i></div><span class="n">${done}/${s.los}</span>${badge}</div>
    </a>`;
  }

  async function viewSubject(code) {
    layout.classList.remove("with-side");
    const subs = await subjects();
    const meta = subs.find((s) => s.code === code);
    if (!meta) return notFound();
    setBar({ title: meta.name, back: "#/", backLabel: "Subjects" });
    main.innerHTML = `<div class="loading">Loading…</div>`;
    const d = await subject(code);
    const c = COLORS[code][0];
    const done = countDone(d.flat.map((l) => l.ref));
    const notice = meta.theory ? "" : `<div class="notice"><div>📖</div><div><b>Syllabus view.</b> Every ATPL(A) learning objective for ${esc(meta.name)} is listed, so you can work through the syllabus and tick objectives off. Written theory for this subject hasn't been added yet.</div></div>`;
    const firstUndone = d.flat.find((l) => !studied.has(l.ref));
    main.innerHTML = `<div class="wrap" style="--c:${c}">
      <div class="hero">${tile(code, "lg")}<div style="flex:1;min-width:0"><div class="code">${code}</div><h1>${esc(meta.name)}</h1><div class="stats">${d.chapters.length} chapters · ${d.flat.length} objectives · ${done} studied</div></div>${ring(d.flat.length ? done / d.flat.length : 0, c)}</div>
      ${meta.book ? `<a class="continue book-cta" href="#/b/${code}"><div class="tile" style="background:linear-gradient(160deg,${COLORS[code][0]},${COLORS[code][1]})">${BOOK_IC}</div><div class="txt"><div class="k">Read as a book</div><div class="t">${esc(meta.name)} study text</div><div class="s">${meta.book - 1} chapters and a formula sheet, written to read straight through</div></div>${CHEV}</a>` : ""}
      ${firstUndone ? `<a class="continue" href="#/lo/${firstUndone.ref}"><div class="txt"><div class="k">${done ? "Next to study" : "Start studying"}</div><div class="t">${esc(loTitle(firstUndone))}</div><div class="s">${firstUndone.ref}</div></div>${CHEV}</a>` : ""}
      ${notice}
      ${d.chapters.map((ch, ci) => chapterBlock(d, ch, ci)).join("")}
    </div>`;
    main.querySelectorAll(".ch-head").forEach((b) => b.addEventListener("click", () => {
      const el = b.parentElement; el.classList.toggle("open");
      const key = el.dataset.ref; el.classList.contains("open") ? openChapters.add(key) : openChapters.delete(key); saveOpen();
    }));
    window.scrollTo(0, store.get("scroll." + code, 0));
  }
  function chapterBlock(d, ch, ci) {
    const los = ch.subs.flatMap((s) => s.topics.flatMap((t) => t.los));
    const done = countDone(los.map((l) => l.ref));
    const open = openChapters.has(ch.ref);
    const num = ch.ref.split(".")[1];
    return `<section class="chapter${open ? " open" : ""}" data-ref="${ch.ref}">
      <button class="ch-head" aria-expanded="${open}"><span class="ch-num">${num}</span><span class="ch-title"><div class="t">${esc(ch.title)}</div><div class="s">${los.length} objectives · ${done} studied</div></span>${DISC}</button>
      <div class="ch-body">${ch.subs.map((sb) => `
        ${sb.title ? `<div class="sub-h">${esc(sb.title)}</div>` : ""}
        ${sb.topics.map((tp) => `${tp.title && tp.title !== sb.title ? `<div class="topic-h">${esc(tp.title)}</div>` : ""}
          ${tp.los.map((lo) => `<a class="row${studied.has(lo.ref) ? " done" : ""}" href="#/lo/${lo.ref}"><span class="tick">${TICK}</span><span class="rt"><div class="ref">${lo.ref}</div><div class="ti">${esc(loTitle(lo))}</div></span>${lo.html ? "" : '<span class="dot empty" title="No theory yet"></span>'}${CHEV}</a>`).join("")}`).join("")}`).join("")}
      </div></section>`;
  }

  function renderSide(d, cur) {
    const code = d.code, c = COLORS[code][0];
    side.style.setProperty("--c", c);
    side.innerHTML = `<a class="s-head" href="#/s/${code}">${tile(code)}<div><div class="c">${code}</div><div class="n">${esc(d.name)}</div></div></a>
      ${d.chapters.map((ch, ci) => `<div class="s-ch${ci === cur.ch ? " open" : ""}"><button>${DISC}<span>${esc(ch.title)}</span></button><div class="s-list">${ch.subs.map((sb) =>
        `${sb.title ? `<div class="s-sub">${esc(sb.title)}</div>` : ""}${sb.topics.flatMap((t) => t.los).map((lo) =>
          `<a class="s-lo${lo.ref === cur.ref ? " cur" : ""}${studied.has(lo.ref) ? " done" : ""}" href="#/lo/${lo.ref}"><span>${esc(loTitle(lo))}</span></a>`).join("")}`).join("")}</div></div>`).join("")}`;
    side.querySelectorAll(".s-ch > button").forEach((b) => b.addEventListener("click", () => b.parentElement.classList.toggle("open")));
    const curEl = $(".s-lo.cur", side);
    if (curEl) {
      const r = curEl.getBoundingClientRect(), sr = side.getBoundingClientRect();
      if (r.top < sr.top + 60 || r.bottom > sr.bottom - 40) side.scrollTop += r.top - sr.top - sr.height / 3;
    }
  }

  async function viewLO(ref) {
    const code = ref.slice(0, 3);
    const subs = await subjects();
    const meta = subs.find((s) => s.code === code);
    if (!meta) return notFound();
    const d = await subject(code);
    const lo = d.byRef.get(ref);
    if (!lo) return notFound();
    const c = COLORS[code][0];
    const ch = d.chapters[lo.ch];
    layout.classList.add("with-side");
    setBar({ title: loTitle(lo), back: `#/s/${code}`, backLabel: meta.name });
    renderSide(d, lo);
    const prev = d.flat[lo.i - 1], next = d.flat[lo.i + 1];
    let inBook = "";
    if (meta.book) {
      try {
        const b = await book(code), n = b.chapterOf.get(ref);
        if (n) inBook = `<a class="in-book" href="#/b/${code}/${n}?lo=${ref}">${BOOK_IC}<span>Read this in the study text · ${esc(b.chapters[n - 1].label)}</span>${CHEV}</a>`;
      } catch {}
    }
    const body = lo.html
      ? `<div class="prose">${lo.html}</div>`
      : `<div class="empty-theory"><div class="ic"><svg viewBox="0 0 24 24" ${S}><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5v14z"/><path d="M8 7h8M8 11h6"/></svg></div><h3>Theory not written yet</h3><p>This subject currently shows the official learning objective only. Use it as your checklist and tick it off once you've covered it.</p></div>`;
    main.innerHTML = `<article class="read reader" style="--c:${c}">
      <nav class="crumbs"><a href="#/s/${code}">${code} ${esc(meta.name)}</a><span class="sep">›</span><span>${esc(ch.title)}</span>${lo.sub.title ? `<span class="sep">›</span><span>${esc(lo.sub.title)}</span>` : ""}</nav>
      <span class="lo-ref">LO ${lo.ref}</span>
      <h1${loTitle(lo).length > 90 ? ' class="long"' : ""}>${esc(loTitle(lo))}</h1>
      ${lo.title ? `<div class="objective"><div class="k">Learning objective</div><div class="v">${esc(lo.lo)}</div></div>` : ""}
      ${inBook}
      ${body}
      <div class="study"><button class="pill${studied.has(ref) ? " on" : ""}" id="studyBtn">${TICK.replace('viewBox="0 0 12 12"', 'viewBox="0 0 12 12" style="width:16px;height:16px"')}<span>${studied.has(ref) ? "Studied" : "Mark as studied"}</span></button></div>
      <div class="pn">
        ${prev ? `<a class="prev" href="#/lo/${prev.ref}"><span class="k">‹ Previous</span><span class="t">${esc(loTitle(prev))}</span></a>` : "<span></span>"}
        ${next ? `<a class="next" href="#/lo/${next.ref}"><span class="k">Next ›</span><span class="t">${esc(loTitle(next))}</span></a>` : ""}
      </div>
      <div class="kbd-hint">← → to move between objectives · S to mark as studied · / to search</div>
    </article>`;
    $("#studyBtn").addEventListener("click", () => toggleStudied(ref, d, lo));
    main.querySelectorAll("figure.dia img").forEach((img) => img.addEventListener("click", () => openLightbox(img)));
    store.set("last", { code, ref, title: loTitle(lo), ts: Date.now() });
    window.scrollTo(0, 0);
    nav.prev = prev && `#/lo/${prev.ref}`; nav.next = next && `#/lo/${next.ref}`;
  }
  function toggleStudied(ref, d, lo) {
    const on = !studied.has(ref);
    on ? studied.add(ref) : studied.delete(ref);
    saveStudied();
    const b = $("#studyBtn");
    b.classList.toggle("on", on);
    $("span", b).textContent = on ? "Studied" : "Mark as studied";
    if (navigator.vibrate) try { navigator.vibrate(on ? 8 : 0); } catch {}
    renderSide(d, lo);
  }
  const nav = { prev: null, next: null };

  /* ---------- study text (book) ---------- */
  async function viewBook(code) {
    layout.classList.remove("with-side");
    const subs = await subjects();
    const meta = subs.find((s) => s.code === code);
    if (!meta || !meta.book) return notFound();
    setBar({ title: `${meta.name} study text`, back: `#/s/${code}`, backLabel: meta.name });
    main.innerHTML = `<div class="loading">Loading…</div>`;
    const b = await book(code);
    const c = COLORS[code][0];
    const all = [...b.chapterOf.keys()], done = countDone(all);
    const lastBook = store.get("lastBook", null);
    const cont = lastBook && lastBook.code === code
      ? `<a class="continue" href="#/b/${code}/${lastBook.n}"><div class="txt"><div class="k">Continue reading</div><div class="t">${esc(lastBook.title)}</div><div class="s">${esc(b.chapters[lastBook.n - 1]?.label || "")}</div></div>${CHEV}</a>` : "";
    main.innerHTML = `<div class="wrap" style="--c:${c}">
      <div class="hero"><div class="tile lg" style="background:linear-gradient(160deg,${COLORS[code][0]},${COLORS[code][1]})">${BOOK_IC}</div><div style="flex:1;min-width:0"><div class="code">${code} ${esc(meta.name)}</div><h1>Study text</h1><div class="stats">${b.chapters.length - 1} chapters · ${all.length} objectives · ${done} studied</div></div>${ring(all.length ? done / all.length : 0, c)}</div>
      ${cont}
      <div class="notice"><div>📖</div><div>Written to read straight through, like a textbook. The <b>small grey codes</b> in the text name the learning objectives each paragraph covers: tap one to open that objective. Mark a chapter as studied at its end.</div></div>
      <div class="book-list">${b.chapters.map((ch) => {
        const dn = countDone(ch.refs), pct = ch.refs.length ? dn / ch.refs.length : 0;
        return `<a class="book-ch" href="#/b/${code}/${ch.n}"><span class="ch-num">${ch.label.startsWith("Chapter") ? ch.n : "A"}</span><span class="ch-title"><div class="t">${esc(ch.title)}</div><div class="s">${ch.sections.length} sections${ch.refs.length ? ` · ${dn}/${ch.refs.length} objectives studied` : ""}</div></span>${ch.refs.length ? ring(pct, c) : ""}${CHEV}</a>`;
      }).join("")}</div>
      <p class="foot">Prefer one objective per page? Open the <a href="#/s/${code}">objective view</a>.</p>
    </div>`;
  }

  function renderBookSide(code, b, ch) {
    side.style.setProperty("--c", COLORS[code][0]);
    side.innerHTML = `<a class="s-head" href="#/b/${code}"><div class="tile" style="background:linear-gradient(160deg,${COLORS[code][0]},${COLORS[code][1]})">${BOOK_IC}</div><div><div class="c">${code} study text</div><div class="n">Contents</div></div></a>
      ${b.chapters.map((c) => `<div class="s-ch${c.n === ch.n ? " open" : ""}"><button>${DISC}<span>${c.label.startsWith("Chapter") ? c.n + " · " : ""}${esc(c.title)}</span></button><div class="s-list">${c.n === ch.n
        ? c.sections.map((s) => `<a class="s-lo s-sec" href="#/b/${code}/${c.n}" data-sec="${s.id}"><span>${esc(s.title)}</span></a>`).join("")
        : `<a class="s-lo" href="#/b/${code}/${c.n}"><span>Open chapter</span></a>`}</div></div>`).join("")}`;
    side.querySelectorAll(".s-ch > button").forEach((x) => x.addEventListener("click", () => x.parentElement.classList.toggle("open")));
    side.querySelectorAll("[data-sec]").forEach((a) => a.addEventListener("click", (e) => {
      e.preventDefault();
      const el = document.getElementById(a.dataset.sec);
      if (el) window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - 70, behavior: "smooth" });
    }));
  }

  function paintTags(root) {
    root.querySelectorAll(".lo-tag").forEach((t) => {
      const refs = t.dataset.refs.split(" ");
      t.classList.toggle("done", refs.every((r) => studied.has(r)));
    });
  }

  let spy = null;
  async function viewChapter(code, n, loRef) {
    const subs = await subjects();
    const meta = subs.find((s) => s.code === code);
    if (!meta || !meta.book) return notFound();
    const b = await book(code);
    const ch = b.chapters[n - 1];
    if (!ch) return notFound();
    const c = COLORS[code][0];
    layout.classList.add("with-side");
    setBar({ title: ch.title, back: `#/b/${code}`, backLabel: "Contents" });
    renderBookSide(code, b, ch);
    const prev = b.chapters[n - 2], next = b.chapters[n];
    const total = ch.refs.length;
    main.innerHTML = `<article class="read reader book" style="--c:${c}">
      <nav class="crumbs"><a href="#/s/${code}">${code} ${esc(meta.name)}</a><span class="sep">›</span><a href="#/b/${code}">Study text</a></nav>
      <div class="kicker">${esc(ch.label)}</div>
      <h1>${esc(ch.title)}</h1>
      <div class="prose">${ch.html}</div>
      ${total ? `<div class="ch-foot"><div class="cf-k">This chapter covers ${total} learning objectives</div><div class="cf-v" id="cfCount"></div><button class="pill" id="chStudy"></button></div>` : ""}
      <div class="pn">
        ${prev ? `<a class="prev" href="#/b/${code}/${prev.n}"><span class="k">‹ ${esc(prev.label)}</span><span class="t">${esc(prev.title)}</span></a>` : "<span></span>"}
        ${next ? `<a class="next" href="#/b/${code}/${next.n}"><span class="k">${esc(next.label)} ›</span><span class="t">${esc(next.title)}</span></a>` : ""}
      </div>
    </article>`;
    const art = $("article.book", main);
    paintTags(art);
    const btn = $("#chStudy");
    const paintFoot = () => {
      if (!btn) return;
      const dn = countDone(ch.refs), all = dn === total;
      $("#cfCount").textContent = `${dn} of ${total} marked as studied`;
      btn.classList.toggle("on", all);
      btn.innerHTML = `${TICK.replace('viewBox="0 0 12 12"', 'viewBox="0 0 12 12" style="width:16px;height:16px"')}<span>${all ? "Chapter studied" : "Mark chapter as studied"}</span>`;
    };
    paintFoot();
    if (btn) btn.addEventListener("click", () => {
      const all = countDone(ch.refs) === total;
      ch.refs.forEach((r) => (all ? studied.delete(r) : studied.add(r)));
      saveStudied(); paintFoot(); paintTags(art);
      if (navigator.vibrate) try { navigator.vibrate(all ? 0 : 8); } catch {}
    });
    art.querySelectorAll("figure.dia img").forEach((img) => img.addEventListener("click", () => openLightbox(img)));
    store.set("lastBook", { code, n, title: ch.title, ts: Date.now() });
    nav.prev = prev && `#/b/${code}/${prev.n}`; nav.next = next && `#/b/${code}/${next.n}`;

    // Scroll: to a requested objective, else back to where the reader left off.
    const key = `bscroll.${code}.${n}`;
    requestAnimationFrame(() => {
      const target = loRef && art.querySelector(`.lo-tag[data-refs~="${loRef}"]`);
      if (target) {
        const block = target.closest("p, li, aside") || target;
        window.scrollTo(0, block.getBoundingClientRect().top + window.scrollY - 80);
        block.classList.add("flash");
        setTimeout(() => block.classList.remove("flash"), 2400);
      } else window.scrollTo(0, store.get(key, 0));
    });

    // Highlight the current section in the sidebar.
    if (spy) spy.disconnect();
    const links = new Map([...side.querySelectorAll("[data-sec]")].map((a) => [a.dataset.sec, a]));
    spy = new IntersectionObserver((es) => {
      es.forEach((e) => {
        if (!e.isIntersecting) return;
        links.forEach((a) => a.classList.remove("cur"));
        const a = links.get(e.target.id);
        if (a) a.classList.add("cur");
      });
    }, { rootMargin: "-70px 0px -70% 0px" });
    art.querySelectorAll(".prose h3[id]").forEach((h) => spy.observe(h));
  }

  function notFound() {
    layout.classList.remove("with-side");
    setBar({ title: "Not found", back: "#/", backLabel: "Subjects" });
    main.innerHTML = `<div class="read"><div class="empty-theory"><h3>Page not found</h3><p><a href="#/">Back to subjects</a></p></div></div>`;
  }

  /* ---------- router ---------- */
  let route = "";
  async function router() {
    const h = location.hash || "#/";
    if (route.startsWith("#/s/")) store.set("scroll." + route.slice(4), window.scrollY);
    const rb = route.match(/^#\/b\/(\d{3})\/(\d+)/);
    if (rb) store.set(`bscroll.${rb[1]}.${rb[2]}`, window.scrollY);
    if (spy && !h.startsWith("#/b/")) { spy.disconnect(); spy = null; }
    route = h;
    nav.prev = nav.next = null;
    try {
      let m;
      if ((m = h.match(/^#\/s\/(\d{3})$/))) await viewSubject(m[1]);
      else if ((m = h.match(/^#\/b\/(\d{3})$/))) await viewBook(m[1]);
      else if ((m = h.match(/^#\/b\/(\d{3})\/(\d+)(?:\?lo=([\d.]+))?$/))) await viewChapter(m[1], +m[2], m[3]);
      else if ((m = h.match(/^#\/lo\/([\d.]+)$/))) await viewLO(m[1]);
      else await viewHome();
    } catch (e) {
      console.error(e);
      main.innerHTML = `<div class="read"><div class="empty-theory"><h3>Couldn't load this page</h3><p>Check your connection and try again.</p></div></div>`;
    }
    if (!h.startsWith("#/s/")) window.scrollTo(0, 0);
    onScroll();
  }
  window.addEventListener("hashchange", router);

  /* ---------- keyboard + swipe ---------- */
  document.addEventListener("keydown", (e) => {
    if (e.target.closest("input, textarea")) return;
    if (!$("#lightbox").hidden || !$("#searchSheet").hidden) return;
    if (e.key === "ArrowRight" && nav.next) location.hash = nav.next;
    else if (e.key === "ArrowLeft" && nav.prev) location.hash = nav.prev;
    else if (e.key === "/") { e.preventDefault(); openSearch(); }
    else if ((e.key === "s" || e.key === "S") && $("#studyBtn")) $("#studyBtn").click();
    else if (e.key === "Escape" && backHref) location.hash = backHref;
  });
  let sx = 0, sy = 0, st = 0;
  main.addEventListener("touchstart", (e) => { const t = e.touches[0]; sx = t.clientX; sy = t.clientY; st = Date.now(); }, { passive: true });
  main.addEventListener("touchend", (e) => {
    if (!nav.prev && !nav.next) return;
    if (e.target.closest(".tbl")) return; // let tables scroll horizontally
    const t = e.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy;
    if (Date.now() - st < 600 && Math.abs(dx) > 80 && Math.abs(dy) < 45) {
      if (dx < 0 && nav.next) location.hash = nav.next;
      if (dx > 0 && nav.prev) location.hash = nav.prev;
    }
  }, { passive: true });

  /* ---------- search ---------- */
  let INDEX = null, subjMap = null;
  const sheet = $("#searchSheet"), q = $("#q"), results = $("#results");
  async function openSearch() {
    sheet.hidden = false;
    document.body.style.overflow = "hidden";
    q.value = store.get("q", "");
    setTimeout(() => { q.focus(); q.select(); }, 30);
    results.innerHTML = `<div class="hint">Loading…</div>`;
    if (!INDEX) {
      INDEX = await getJSON("data/search.json");
      subjMap = Object.fromEntries((await subjects()).map((s) => [s.code, s]));
      INDEX.forEach((r) => (r.k = (r[1] + " " + r[2]).toLowerCase()));
    }
    runSearch();
  }
  function closeSearch() { sheet.hidden = true; document.body.style.overflow = ""; }
  sheet.addEventListener("click", (e) => { if (e.target.closest("[data-close]")) closeSearch(); });
  results.addEventListener("click", (e) => { if (e.target.closest("a")) closeSearch(); });
  q.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeSearch();
    if (e.key === "Enter") { const a = $("a", results); if (a) { location.hash = a.getAttribute("href"); closeSearch(); } }
  });
  let qt;
  q.addEventListener("input", () => { clearTimeout(qt); qt = setTimeout(runSearch, 60); });
  function runSearch() {
    const v = q.value.trim().toLowerCase();
    store.set("q", q.value);
    if (!INDEX) return;
    if (v.length < 2) { results.innerHTML = `<div class="hint">Search all ${INDEX.length.toLocaleString()} learning objectives by keyword or reference, e.g. “jet stream”, “QNH” or “050.06”.</div>`; return; }
    const terms = v.split(/\s+/).filter(Boolean);
    const hits = [];
    for (const r of INDEX) { if (terms.every((t) => r.k.includes(t))) { hits.push(r); if (hits.length >= 80) break; } }
    if (!hits.length) { results.innerHTML = `<div class="hint">No objectives match “${esc(q.value)}”.</div>`; return; }
    const re = new RegExp("(" + terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")", "gi");
    const hl = (s) => esc(s).replace(re, "<mark>$1</mark>");
    results.innerHTML = hits.map(([code, ref, t]) =>
      `<a class="row${studied.has(ref) ? " done" : ""}" href="#/lo/${ref}" style="--c:${COLORS[code][0]}"><span class="tick">${TICK}</span><span class="rt"><div class="res-sub">${code} ${esc(subjMap[code].name)} · <span style="font-family:var(--mono)">${hl(ref)}</span></div><div class="ti">${hl(t)}</div></span>${CHEV}</a>`).join("");
  }
  $("#searchBtn").addEventListener("click", openSearch);

  /* ---------- lightbox ---------- */
  const lb = $("#lightbox"), lbImg = $("#lbImg"), lbScroll = $(".lb-scroll");
  function openLightbox(img) {
    lbImg.src = img.currentSrc || img.src; lbImg.alt = img.alt;
    lbScroll.classList.remove("zoom");
    lb.hidden = false; document.body.style.overflow = "hidden";
  }
  function closeLightbox() { lb.hidden = true; document.body.style.overflow = ""; }
  lb.addEventListener("click", (e) => {
    if (e.target.closest("[data-close]")) return closeLightbox();
    if (e.target === lbImg) { lbScroll.classList.toggle("zoom"); return; }
    closeLightbox();
  });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !lb.hidden) closeLightbox(); });

  /* ---------- boot ---------- */
  router();
  if ("serviceWorker" in navigator && location.protocol === "https:") navigator.serviceWorker.register("sw.js").catch(() => {});
})();
