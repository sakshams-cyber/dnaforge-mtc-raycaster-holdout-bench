// Holdout UI — vanilla JS, no build step.
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (x) => (x == null ? "—" : Math.abs(x) >= 100 ? Math.round(x).toLocaleString() : Number(x.toPrecision(3)).toString());
const SEV = {
  hold_risk: "Potential clinical hold issues",
  comment: "Other comments",
  cannot_verify: "Could not verify",
  info: "Checks that passed",
};
let state = { report: null, pages: {}, active: null };

function status(msg, isError = false) {
  const el = $("#status");
  if (!msg) return el.classList.add("hidden");
  el.textContent = msg;
  el.className = "status" + (isError ? " error" : "");
}

function showTab(name) {
  document.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  ["review", "memo", "bench"].forEach((t) => $("#" + t).classList.toggle("hidden", t !== name || (t !== "bench" && !state.report)));
  $("#empty").classList.toggle("hidden", !!state.report || name === "bench");
  if (name === "bench") loadBench();
}

async function loadDemo() {
  status("Analyzing the synthetic demo filing…");
  const r = await fetch("/api/demo?which=demo");
  handle(await r.json());
}

async function upload(file) {
  status(`Reading ${file.name} (${(file.size / 1e6).toFixed(1)} MB)… real filings can take a minute with the Claude extractor.`);
  const r = await fetch("/api/analyze", { method: "POST", headers: { "X-Filename": file.name }, body: file });
  handle(await r.json());
}

function handle(rep) {
  if (rep.error) return status("Error: " + rep.error, true);
  status("");
  state.report = rep;
  state.pages = Object.fromEntries(rep.pages.map((p) => [p.number, p]));
  render();
  showTab("review");
}

function render() {
  const r = state.report;
  $("#fileName").textContent = r.filename;
  const n = (s) => r.findings.filter((f) => f.severity === s).length;
  $("#counts").innerHTML = `
    <div class="count hold"><b>${n("hold_risk")}</b><span>hold risks</span></div>
    <div class="count comment"><b>${n("comment")}</b><span>comments</span></div>
    <div class="count"><b>${n("cannot_verify")}</b><span>unverified</span></div>`;
  $("#sections").innerHTML = r.sections
    .map((s) => `<li data-page="${s.start_page}"><span>${esc(s.name)}</span><span class="pg">${s.start_page === s.end_page ? "p. " + s.start_page : "pp. " + s.start_page + "–" + s.end_page}</span></li>`)
    .join("");
  $("#sections").querySelectorAll("li").forEach((li) => (li.onclick = () => showPages([{ page: +li.dataset.page, quote: "" }], "Section")));
  $("#meta").innerHTML = `${r.pages.length} pages · extractor: ${esc(r.meta.extractor)} · ${r.meta.seconds}s` +
    (r.meta.redacted_pages ? ` · <span class="badge redacted">${r.meta.redacted_pages} redacted pages</span>` : "") +
    (r.meta.ocr_pages ? ` · ${r.meta.ocr_pages} OCR pages` : "");
  renderDose(r.dose_chain);
  renderFindings(r.findings);
  renderMemo(r.memo_markdown);
}

function renderDose(c) {
  const el = $("#dosePanel");
  if (!c || !c.rows || !c.rows.length) {
    el.innerHTML = `<h2>Starting dose</h2><p class="muted">No usable tox values were extracted, so the starting dose could not be derived.</p>`;
    return;
  }
  const b = c.rows[0];
  const pg = (ps) => (ps && ps.length ? ps.map((p) => `<span class="chip" data-page="${p}">p. ${p}</span>`).join(" ") : "");
  const ratio = c.proposed_start_mg && c.mrsd_mg ? c.proposed_start_mg / c.mrsd_mg : null;
  el.innerHTML = `
    <h2>Starting dose · ${esc(c.method)}${c.biologic ? " · mg/kg scaling (biologic)" : ""}</h2>
    <div class="chain">
      <div class="step"><b>${fmt(b.value_mg_kg)}</b><span>${esc(b.species)} ${b.basis}, mg/kg/day</span></div><div class="op">÷ ${b.factor}</div>
      <div class="step"><b>${fmt(b.hed_mg_kg)}</b><span>HED mg/kg</span></div><div class="op">× ${c.human_weight_kg} kg</div>
      <div class="step"><b>${fmt(b.hed_mg)}</b><span>HED mg</span></div><div class="op">÷ ${b.divisor}</div>
      <div class="step final"><b>${fmt(c.mrsd_mg)} mg</b><span>derived maximum start</span></div>
    </div>
    ${c.verdict ? `<div class="verdict ${c.verdict}">${c.verdict === "exceeds"
      ? `Proposed ${fmt(c.proposed_start_mg)} mg is ${ratio.toFixed(1)}× the derived maximum`
      : `Proposed ${fmt(c.proposed_start_mg)} mg is within the derived maximum`} <span class="chips">${pg(c.proposed_pages)}</span></div>` : ""}
    <table class="rows"><thead><tr><th>Species</th><th>Study</th><th>${b.basis}</th><th>Factor</th><th>HED mg</th><th>Candidate start</th><th>Pages</th></tr></thead><tbody>
    ${c.rows.map((r, i) => `<tr class="${i === 0 ? "best" : ""}"><td>${esc(r.species)}${i === 0 ? " (most sensitive)" : ""}</td><td>${r.duration_days ? fmt(r.duration_days) + " d" : "—"}</td><td class="num">${fmt(r.value_mg_kg)}</td><td class="num">${r.factor}</td><td class="num">${fmt(r.hed_mg)}</td><td class="num">${fmt(r.candidate_start_mg)} mg</td><td>${pg(r.pages)}</td></tr>`).join("")}
    </tbody></table>`;
  el.querySelectorAll(".chip").forEach((ch) => (ch.onclick = (e) => { e.stopPropagation(); showPages([{ page: +ch.dataset.page, quote: "" }], "Starting dose"); }));
}

function renderFindings(fs) {
  const html = Object.keys(SEV).map((sev) => {
    const items = fs.filter((f) => f.severity === sev);
    if (!items.length) return "";
    return `<div class="group"><h2>${SEV[sev]} (${items.length})</h2>${items.map(card).join("")}</div>`;
  }).join("");
  $("#findings").innerHTML = html || `<div class="panel">No findings.</div>`;
  $("#findings").querySelectorAll(".finding").forEach((el) => {
    el.onclick = () => select(el.dataset.id);
    el.querySelectorAll(".chip").forEach((ch) => (ch.onclick = (e) => {
      e.stopPropagation();
      const f = fs.find((x) => x.id === el.dataset.id);
      showPages([f.evidence[+ch.dataset.i]], f.title);
    }));
  });
}

function card(f) {
  return `<div class="finding ${f.severity}" data-id="${f.id}">
    <div class="f-top"><span class="rule">${esc(f.rule)}</span><span class="f-title">${esc(f.title)}</span></div>
    ${f.detail ? `<div class="f-detail">${esc(f.detail)}</div>` : ""}
    ${f.suggestion ? `<div class="f-fix"><b>Fix:</b> ${esc(f.suggestion)}</div>` : ""}
    ${f.citation ? `<div class="f-basis">Basis: ${esc(f.citation)}</div>` : ""}
    <div class="chips">${(f.evidence || []).map((e, i) => `<span class="chip ${e.verified === false ? "unverified" : ""}" data-i="${i}" title="${esc(e.section)}">p. ${e.page}</span>`).join("")}</div>
  </div>`;
}

function select(id) {
  const f = state.report.findings.find((x) => x.id === id);
  document.querySelectorAll(".finding").forEach((el) => el.classList.toggle("active", el.dataset.id === id));
  showPages(f.evidence || [], f.title);
}

// Find the quote in raw page text, tolerant to whitespace, and wrap it in <mark>.
function highlight(text, quote) {
  if (!quote) return esc(text);
  const words = quote.replace(/\|/g, " ").split(/\s+/).filter(Boolean).map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  if (!words.length) return esc(text);
  const rx = new RegExp(words.join("[\\s|]+"), "i");
  const m = text.match(rx);
  if (!m) return esc(text);
  return esc(text.slice(0, m.index)) + "<mark>" + esc(m[0]) + "</mark>" + esc(text.slice(m.index + m[0].length));
}

function showPages(evs, title) {
  $("#viewerHead").textContent = title || "Pages";
  const byPage = {};
  evs.forEach((e) => { if (e && e.page) (byPage[e.page] = byPage[e.page] || []).push(e.quote || ""); });
  $("#viewerBody").innerHTML = Object.keys(byPage).sort((a, b) => a - b).map((n) => {
    const p = state.pages[n];
    if (!p) return `<div class="page"><div class="page-head">Page ${n}</div><pre class="muted">Page not found in this filing.</pre></div>`;
    let html = esc(p.text);
    const q = byPage[n].find(Boolean);
    if (q) html = highlight(p.text, q);
    return `<div class="page"><div class="page-head"><span>Page ${n} · ${esc(p.section)}</span>${p.redactions ? `<span class="badge redacted">${p.redactions} redactions</span>` : ""}</div><pre>${html}</pre></div>`;
  }).join("");
  const mk = $("#viewerBody mark");
  if (mk) mk.scrollIntoView({ block: "center" });
}

// Minimal markdown: headings, tables, ordered/unordered lists, bold, italics.
function md(src) {
  const inline = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/\*(.+?)\*/g, "<i>$1</i>");
  const out = [];
  const lines = src.split("\n");
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    if (/^#{1,3} /.test(l)) { const h = l.match(/^#+/)[0].length; out.push(`<h${h}>${inline(l.slice(h + 1))}</h${h}>`); continue; }
    if (l.startsWith("|")) {
      const rows = [];
      while (i < lines.length && lines[i].startsWith("|")) rows.push(lines[i++]);
      i--;
      const cells = (r) => r.split("|").slice(1, -1).map((c) => c.trim());
      out.push("<table><thead><tr>" + cells(rows[0]).map((c) => `<th>${inline(c)}</th>`).join("") + "</tr></thead><tbody>" +
        rows.slice(2).map((r) => "<tr>" + cells(r).map((c) => `<td>${inline(c)}</td>`).join("") + "</tr>").join("") + "</tbody></table>");
      continue;
    }
    if (/^\d+\. /.test(l)) {
      const items = [];
      while (i < lines.length && (/^\d+\. /.test(lines[i]) || /^ {4}/.test(lines[i]))) {
        if (/^\d+\. /.test(lines[i])) items.push(inline(lines[i].replace(/^\d+\. /, "")));
        else items[items.length - 1] += "<br>" + inline(lines[i].trim());
        i++;
      }
      i--;
      out.push("<ol>" + items.map((x) => `<li>${x}</li>`).join("") + "</ol>");
      continue;
    }
    if (/^- /.test(l)) { out.push(`<ul><li>${inline(l.slice(2))}</li></ul>`); continue; }
    if (l.trim()) out.push(`<p>${inline(l)}</p>`);
  }
  return out.join("\n");
}

function renderMemo(text) {
  $("#memoBody").innerHTML = md(text);
}

async function loadBench() {
  const el = $("#benchBody");
  el.innerHTML = `<div class="panel">Loading…</div>`;
  const r = await (await fetch("/api/bench")).json();
  if (!r.available) {
    el.innerHTML = `<div class="panel"><h2>HoldoutBench</h2><p>No results yet. Run:</p>
      <p><code>python -m holdout bench make --base your_filing.pdf --per-op 3</code><br>
      <code>python -m holdout bench run --agent holdout</code><br>
      <code>python -m holdout bench run --agent baseline</code><br>
      <code>python -m holdout bench score</code></p></div>`;
    return;
  }
  const agents = Object.entries(r.agents);
  const ops = [...new Set(agents.flatMap(([, a]) => Object.keys(a.per_operator)))].sort();
  const pct = (x) => (x == null ? "—" : Math.round(x * 100) + "%");
  el.innerHTML = `
    <div class="kpis">${agents.map(([n, a]) => `<div class="kpi"><b>${pct(a.recall)}</b><span>${esc(n)} · planted errors caught</span></div>`).join("")}</div>
    <div class="panel"><h2>Planted errors caught, by error type</h2>${chart(agents, ops)}
      <p class="muted">${r.n_tasks} tasks on ${r.n_bases} base filing(s). An issue counts only with the right rule on the mutated page, and only if the agent did not also report it on the clean copy.</p></div>
    <div class="panel"><h2>Detail</h2><table class="rows"><thead><tr><th>Agent</th><th>Recall</th>${ops.map((o) => `<th>${esc(o.replace(/_/g, " "))}</th>`).join("")}<th>Flags on clean</th><th>s/filing</th><th>Errors</th></tr></thead><tbody>
      ${agents.map(([n, a]) => `<tr><td>${esc(n)}</td><td class="num">${pct(a.recall)}</td>${ops.map((o) => `<td class="num">${pct(a.per_operator[o])}</td>`).join("")}<td class="num">${Object.values(a.flags_on_clean_filings).reduce((x, y) => x + y, 0)}</td><td class="num">${a.mean_seconds ?? "—"}</td><td class="num">${a.errors}</td></tr>`).join("")}
    </tbody></table></div>`;
}

function chart(agents, ops) {
  const W = 900, H = 300, L = 44, B = 64, T = 16;
  const gw = (W - L - 10) / ops.length, bw = Math.min(28, (gw - 16) / agents.length);
  const colors = ["#1d4ed8", "#9aa3af", "#a15c07", "#16181d"];
  const y = (v) => T + (H - T - B) * (1 - v);
  let s = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Share of planted errors caught by error type">`;
  [0, 0.5, 1].forEach((v) => (s += `<line x1="${L}" x2="${W - 10}" y1="${y(v)}" y2="${y(v)}" stroke="#ebe9e3"/><text x="${L - 6}" y="${y(v) + 4}" text-anchor="end" font-size="11" fill="#7b808a">${v * 100}%</text>`));
  ops.forEach((op, i) => {
    const x0 = L + i * gw + (gw - bw * agents.length) / 2;
    agents.forEach(([n, a], k) => {
      const v = a.per_operator[op] ?? 0;
      s += `<rect x="${x0 + k * bw}" y="${y(v)}" width="${bw - 2}" height="${y(0) - y(v)}" fill="${colors[k % colors.length]}"><title>${esc(n)} · ${esc(op)}: ${Math.round(v * 100)}%</title></rect>`;
    });
    s += `<text x="${L + i * gw + gw / 2}" y="${H - B + 18}" text-anchor="middle" font-size="11" fill="#4a4f5a">${esc(op.replace(/_/g, " "))}</text>`;
  });
  agents.forEach(([n], k) => (s += `<rect x="${L + k * 150}" y="${H - 22}" width="10" height="10" fill="${colors[k % colors.length]}"/><text x="${L + k * 150 + 16}" y="${H - 13}" font-size="12" fill="#16181d">${esc(n)}</text>`));
  return s + "</svg>";
}

// wire up
document.querySelectorAll(".tab-btn").forEach((b) => (b.onclick = () => showTab(b.dataset.tab)));
$("#demoBtn").onclick = loadDemo;
$("#demoLink").onclick = (e) => { e.preventDefault(); loadDemo(); };
$("#fileInput").onchange = (e) => e.target.files[0] && upload(e.target.files[0]);
$("#copyMemo").onclick = () => navigator.clipboard.writeText(state.report?.memo_markdown || "");
$("#downloadMemo").onclick = () => {
  const blob = new Blob([state.report?.memo_markdown || ""], { type: "text/markdown" });
  const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: "holdout-review.md" });
  a.click();
};
document.addEventListener("dragover", (e) => e.preventDefault());
document.addEventListener("drop", (e) => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f) upload(f); });
