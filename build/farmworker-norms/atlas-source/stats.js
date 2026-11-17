/* IMR statistics engine: lets visitors compare groups of countries, test relationships and fit regressions with controls,
   with confidence intervals, p-values and a plain-language reading. Shared by the Migration Law Atlas, the Farmworker Norms
   Atlas and Government Hate Speech. Usage: IMRStats.mount(element, {rows, vars, presets, idLabel, filename, note}). */
(function () {
  "use strict";

  /* ---------- distributions ---------- */
  function lgamma(x) {
    const c = [76.18009172947146, -86.50532032941677, 24.01409824083091, -1.231739572450155, 0.1208650973866179e-2, -0.5395239384953e-5];
    let y = x, tmp = x + 5.5, ser = 1.000000000190015;
    tmp -= (x + 0.5) * Math.log(tmp);
    for (let j = 0; j < 6; j++) ser += c[j] / ++y;
    return -tmp + Math.log(2.5066282746310005 * ser / x);
  }
  function betacf(a, b, x) {
    const MAXIT = 300, EPS = 3e-14, FPMIN = 1e-300;
    let qab = a + b, qap = a + 1, qam = a - 1, c = 1, d = 1 - qab * x / qap;
    if (Math.abs(d) < FPMIN) d = FPMIN; d = 1 / d; let h = d;
    for (let m = 1; m <= MAXIT; m++) {
      const m2 = 2 * m;
      let aa = m * (b - m) * x / ((qam + m2) * (a + m2));
      d = 1 + aa * d; if (Math.abs(d) < FPMIN) d = FPMIN; c = 1 + aa / c; if (Math.abs(c) < FPMIN) c = FPMIN; d = 1 / d; h *= d * c;
      aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2));
      d = 1 + aa * d; if (Math.abs(d) < FPMIN) d = FPMIN; c = 1 + aa / c; if (Math.abs(c) < FPMIN) c = FPMIN; d = 1 / d;
      const del = d * c; h *= del; if (Math.abs(del - 1) < EPS) break;
    }
    return h;
  }
  function ibeta(x, a, b) { // regularized incomplete beta I_x(a,b)
    if (x <= 0) return 0; if (x >= 1) return 1;
    const bt = Math.exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * Math.log(x) + b * Math.log(1 - x));
    return x < (a + 1) / (a + b + 2) ? bt * betacf(a, b, x) / a : 1 - bt * betacf(b, a, 1 - x) / b;
  }
  function gammq(a, x) { // regularized upper incomplete gamma Q(a,x)
    if (x <= 0) return 1;
    const gln = lgamma(a);
    if (x < a + 1) {
      let ap = a, sum = 1 / a, del = sum;
      for (let n = 0; n < 500; n++) { ap++; del *= x / ap; sum += del; if (Math.abs(del) < Math.abs(sum) * 3e-14) break; }
      return 1 - sum * Math.exp(-x + a * Math.log(x) - gln);
    }
    let b = x + 1 - a, c = 1e300, d = 1 / b, h = d;
    for (let i = 1; i < 500; i++) {
      const an = -i * (i - a); b += 2; d = an * d + b; if (Math.abs(d) < 1e-300) d = 1e-300; c = b + an / c; if (Math.abs(c) < 1e-300) c = 1e-300;
      d = 1 / d; const del = d * c; h *= del; if (Math.abs(del - 1) < 3e-14) break;
    }
    return Math.exp(-x + a * Math.log(x) - gln) * h;
  }
  const pT = (t, df) => df > 0 && isFinite(t) ? ibeta(df / (df + t * t), df / 2, 0.5) : (isFinite(t) ? NaN : 0); // two-sided
  const pF = (f, d1, d2) => f > 0 ? ibeta(d2 / (d2 + d1 * f), d2 / 2, d1 / 2) : 1;
  const pChi = (x, k) => gammq(k / 2, x / 2);
  const pZ = z => pChi(z * z, 1);
  function tCrit(df, p) { // two-sided critical value
    p = p || 0.05; if (!(df > 0)) return NaN;
    let lo = 0, hi = 1000;
    for (let i = 0; i < 100; i++) { const mid = (lo + hi) / 2; if (pT(mid, df) > p) lo = mid; else hi = mid; }
    return (lo + hi) / 2;
  }
  const Z95 = 1.959963984540054;

  /* ---------- descriptives ---------- */
  const sum = a => a.reduce((s, v) => s + v, 0);
  const mean = a => sum(a) / a.length;
  const variance = a => { const m = mean(a); return a.reduce((s, v) => s + (v - m) * (v - m), 0) / (a.length - 1); };
  const sd = a => Math.sqrt(variance(a));
  function quantile(a, q) { const s = [...a].sort((x, y) => x - y), i = (s.length - 1) * q, lo = Math.floor(i); return s[lo] + (s[Math.ceil(i)] - s[lo]) * (i - lo); }
  function ranks(a) {
    const idx = a.map((v, i) => [v, i]).sort((x, y) => x[0] - y[0]), r = new Array(a.length); let ties = 0;
    for (let i = 0; i < idx.length;) {
      let j = i; while (j + 1 < idx.length && idx[j + 1][0] === idx[i][0]) j++;
      const rk = (i + j) / 2 + 1, t = j - i + 1; if (t > 1) ties += t * t * t - t;
      for (let k = i; k <= j; k++) r[idx[k][1]] = rk; i = j + 1;
    }
    r.ties = ties; return r;
  }

  /* ---------- tests ---------- */
  function oneSample(a) {
    const n = a.length, m = mean(a), se = sd(a) / Math.sqrt(n), df = n - 1, t = m / se, tc = tCrit(df);
    return { n, m, se, df, t, p: pT(t, df), lo: m - tc * se, hi: m + tc * se };
  }
  function signedRank(a) { // Wilcoxon signed-rank, normal approximation
    const d = a.filter(v => v !== 0), n = d.length; if (n < 5) return null;
    const r = ranks(d.map(Math.abs)); let W = 0; d.forEach((v, i) => { if (v > 0) W += r[i]; });
    const mu = n * (n + 1) / 4, s2 = n * (n + 1) * (2 * n + 1) / 24 - r.ties / 48, z = (W - mu) / Math.sqrt(s2);
    return { W, z, p: pZ(z) };
  }
  function welch(a, b) {
    const na = a.length, nb = b.length, va = variance(a), vb = variance(b), d = mean(a) - mean(b);
    const se = Math.sqrt(va / na + vb / nb), df = Math.pow(va / na + vb / nb, 2) / (Math.pow(va / na, 2) / (na - 1) + Math.pow(vb / nb, 2) / (nb - 1));
    const t = d / se, tc = tCrit(df), sp = Math.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2));
    return { d, se, df, t, p: pT(t, df), lo: d - tc * se, hi: d + tc * se, cohen: d / sp };
  }
  function mannWhitney(a, b) {
    const all = a.concat(b), r = ranks(all), n1 = a.length, n2 = b.length, N = n1 + n2;
    const R1 = sum(r.slice(0, n1)), U = R1 - n1 * (n1 + 1) / 2, mu = n1 * n2 / 2;
    const s2 = n1 * n2 / 12 * ((N + 1) - r.ties / (N * (N - 1))), z = (U - mu) / Math.sqrt(s2);
    return { U, z, p: pZ(z), auc: U / (n1 * n2) };
  }
  function anova(groups) {
    const all = groups.flat(), gm = mean(all), k = groups.length, N = all.length;
    let ssb = 0, ssw = 0; groups.forEach(g => { const m = mean(g); ssb += g.length * (m - gm) * (m - gm); g.forEach(v => ssw += (v - m) * (v - m)); });
    const d1 = k - 1, d2 = N - k, F = (ssb / d1) / (ssw / d2);
    return { F, d1, d2, p: pF(F, d1, d2), eta2: ssb / (ssb + ssw) };
  }
  function kruskal(groups) {
    const all = groups.flat(), r = ranks(all), N = all.length; let H = 0, o = 0;
    groups.forEach(g => { const R = sum(r.slice(o, o + g.length)); H += R * R / g.length; o += g.length; });
    H = 12 / (N * (N + 1)) * H - 3 * (N + 1); H /= 1 - r.ties / (N * N * N - N);
    return { H, df: groups.length - 1, p: pChi(H, groups.length - 1) };
  }
  function wilson(k, n) { const p = k / n, z = Z95, den = 1 + z * z / n, c = (p + z * z / (2 * n)) / den, h = z * Math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den; return { p, lo: Math.max(0, c - h), hi: Math.min(1, c + h) }; }
  function chisq(tab) { // tab: rows = groups, cols = [yes, no]
    const R = tab.map(sum), Cc = tab[0].map((_, j) => sum(tab.map(r => r[j]))), N = sum(R); let X = 0, minE = Infinity;
    tab.forEach((r, i) => r.forEach((o, j) => { const e = R[i] * Cc[j] / N; minE = Math.min(minE, e); if (e > 0) X += (o - e) * (o - e) / e; }));
    const df = (tab.length - 1) * (Cc.length - 1);
    return { X, df, p: pChi(X, df), V: Math.sqrt(X / (N * Math.min(tab.length - 1, Cc.length - 1))), minE };
  }
  function fisher(a, b, c, d) { // two-sided Fisher exact for [[a,b],[c,d]]
    const r1 = a + b, r2 = c + d, c1 = a + c, n = r1 + r2;
    const lf = x => lgamma(x + 1), lp = x => lf(r1) + lf(r2) + lf(c1) + lf(n - c1) - lf(n) - lf(x) - lf(r1 - x) - lf(c1 - x) - lf(r2 - c1 + x);
    const p0 = lp(a); let p = 0;
    for (let x = Math.max(0, c1 - r2); x <= Math.min(r1, c1); x++) { const v = lp(x); if (v <= p0 + 1e-7) p += Math.exp(v); }
    return Math.min(1, p);
  }
  function pearson(x, y) {
    const n = x.length, mx = mean(x), my = mean(y); let sxy = 0, sxx = 0, syy = 0;
    for (let i = 0; i < n; i++) { const dx = x[i] - mx, dy = y[i] - my; sxy += dx * dy; sxx += dx * dx; syy += dy * dy; }
    const r = sxy / Math.sqrt(sxx * syy), t = r * Math.sqrt((n - 2) / (1 - r * r)), z = Math.atanh(r), se = 1 / Math.sqrt(n - 3);
    return { r, n, p: pT(t, n - 2), lo: Math.tanh(z - Z95 * se), hi: Math.tanh(z + Z95 * se) };
  }
  const spearman = (x, y) => pearson(ranks(x), ranks(y));

  /* ---------- linear algebra and models ---------- */
  function inv(M) {
    const n = M.length, A = M.map((r, i) => [...r, ...M.map((_, j) => +(i === j))]);
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
      if (Math.abs(A[p][c]) < 1e-12) return null;
      [A[c], A[p]] = [A[p], A[c]];
      const v = A[c][c]; for (let j = 0; j < 2 * n; j++) A[c][j] /= v;
      for (let r = 0; r < n; r++) if (r !== c) { const f = A[r][c]; if (f) for (let j = 0; j < 2 * n; j++) A[r][j] -= f * A[c][j]; }
    }
    return A.map(r => r.slice(n));
  }
  function ols(X, y) { // X includes intercept column
    const n = X.length, k = X[0].length, XtX = [], Xty = [];
    for (let i = 0; i < k; i++) { XtX.push(new Array(k).fill(0)); Xty.push(0); }
    X.forEach((r, o) => { for (let i = 0; i < k; i++) { Xty[i] += r[i] * y[o]; for (let j = 0; j < k; j++) XtX[i][j] += r[i] * r[j]; } });
    const V = inv(XtX); if (!V) return null;
    const b = V.map(r => sum(r.map((v, j) => v * Xty[j])));
    const fit = X.map(r => sum(r.map((v, j) => v * b[j]))), res = y.map((v, i) => v - fit[i]);
    const sse = sum(res.map(e => e * e)), my = mean(y), sst = sum(y.map(v => (v - my) * (v - my))), df = n - k, s2 = sse / df, tc = tCrit(df);
    const se = V.map((r, i) => Math.sqrt(s2 * r[i]));
    const r2 = 1 - sse / sst, F = ((sst - sse) / (k - 1)) / s2;
    return { b, se, t: b.map((v, i) => v / se[i]), p: b.map((v, i) => pT(v / se[i], df)), lo: b.map((v, i) => v - tc * se[i]), hi: b.map((v, i) => v + tc * se[i]),
      n, k, df, r2, adj: 1 - (1 - r2) * (n - 1) / df, F, pF: pF(F, k - 1, df), V, s2 };
  }
  function logit(X, y) {
    const n = X.length, k = X[0].length; let b = new Array(k).fill(0), H = null, ll = 0, conv = false;
    for (let it = 0; it < 60; it++) {
      const g = new Array(k).fill(0), Hm = []; for (let i = 0; i < k; i++) Hm.push(new Array(k).fill(0)); ll = 0;
      X.forEach((r, o) => {
        const eta = sum(r.map((v, j) => v * b[j])), p = 1 / (1 + Math.exp(-eta)), w = p * (1 - p);
        ll += y[o] ? Math.log(Math.max(p, 1e-300)) : Math.log(Math.max(1 - p, 1e-300));
        for (let i = 0; i < k; i++) { g[i] += (y[o] - p) * r[i]; for (let j = 0; j < k; j++) Hm[i][j] += w * r[i] * r[j]; }
      });
      H = inv(Hm); if (!H) return null;
      const step = H.map(row => sum(row.map((v, j) => v * g[j])));
      b = b.map((v, i) => v + step[i]);
      if (Math.max(...step.map(Math.abs)) < 1e-8) { conv = true; break; }
    }
    const ybar = mean(y), ll0 = n * (ybar * Math.log(ybar) + (1 - ybar) * Math.log(1 - ybar));
    const se = H.map((r, i) => Math.sqrt(r[i]));
    const sep = !conv || b.some(v => Math.abs(v) > 12) || se.some(v => !isFinite(v) || v > 50);
    return { b, se, z: b.map((v, i) => v / se[i]), p: b.map((v, i) => pZ(v / se[i])), lo: b.map((v, i) => v - Z95 * se[i]), hi: b.map((v, i) => v + Z95 * se[i]),
      n, k, ll, ll0, r2: 1 - ll / ll0, sep, V: H };
  }

  /* ---------- permutation tests, multiple comparisons, survival ---------- */
  const NPERM = 5000, NPAIR = 2000;
  function rng(seed) { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function shuffle(a, r) { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function tail(obs, sims, alt) { // share of reshuffles at least as extreme as the observed statistic, counting the observed one
    const e = 1e-9 * (1 + Math.abs(obs)); let c = 0;
    sims.forEach(v => { if (alt === "greater" ? v >= obs - e : alt === "less" ? v <= obs + e : Math.abs(v) >= Math.abs(obs) - e) c++; });
    return (c + 1) / (sims.length + 1);
  }
  function permDiff(a, b, alt, B) { // difference in means (or shares) between two groups, with group labels reshuffled
    B = B || NPERM; const all = a.concat(b), n1 = a.length, n2 = b.length, tot = sum(all), r = rng(20261030), obs = mean(a) - mean(b), sims = [];
    for (let k = 0; k < B; k++) { shuffle(all, r); let s = 0; for (let i = 0; i < n1; i++) s += all[i]; sims.push(s / n1 - (tot - s) / n2); }
    return { obs, p: tail(obs, sims, alt || "two"), B };
  }
  function permGroups(groups, B) { // k groups; sum of S²/n per group orders reshuffles exactly as F (numbers) or chi-square (yes/no) does
    B = B || NPERM; const all = groups.flat(), ns = groups.map(g => g.length);
    const stat = arr => { let o = 0, s = 0; ns.forEach(n => { let t = 0; for (let i = o; i < o + n; i++) t += arr[i]; s += t * t / n; o += n; }); return s; };
    const obs = stat(all), r = rng(20261030), sims = []; for (let k = 0; k < B; k++) sims.push(stat(shuffle(all, r)));
    return { p: tail(obs, sims, "greater"), B };
  }
  function permCor(x, y, alt, B) { // correlation with one variable reshuffled
    B = B || NPERM; const mx = mean(x), xc = x.map(v => v - mx), yy = y.slice();
    const stat = arr => { let s = 0; for (let i = 0; i < xc.length; i++) s += xc[i] * arr[i]; return s; };
    const obs = stat(y), r = rng(20261030), sims = []; for (let k = 0; k < B; k++) sims.push(stat(shuffle(yy, r)));
    return { p: tail(obs, sims, alt || "two"), B };
  }
  function permSign(a, alt, B) { // sign-flip test of a mean of zero
    B = B || NPERM; const obs = sum(a), r = rng(20261030), sims = [];
    for (let k = 0; k < B; k++) { let s = 0; for (let i = 0; i < a.length; i++) s += r() < 0.5 ? -a[i] : a[i]; sims.push(s); }
    return { p: tail(obs, sims, alt || "two"), B };
  }
  function holm(ps) { // Holm step-down adjustment
    const o = ps.map((p, i) => [p, i]).sort((a, b) => a[0] - b[0]), m = ps.length, out = new Array(m); let run = 0;
    o.forEach(([p, i], j) => { run = Math.max(run, Math.min(1, (m - j) * p)); out[i] = run; });
    return out;
  }
  function km(t, e) { // Kaplan-Meier: steps [{t, s}] where s is the share not yet ratified
    const idx = t.map((_, i) => i).sort((a, b) => t[a] - t[b]); let n = t.length, s = 1; const out = [{ t: 0, s: 1 }];
    for (let i = 0; i < idx.length;) {
      const tt = t[idx[i]]; let d = 0, c = 0;
      while (i < idx.length && t[idx[i]] === tt) { e[idx[i]] ? d++ : c++; i++; }
      if (d) { s *= 1 - d / n; out.push({ t: tt, s }); }
      n -= d + c;
    }
    return out;
  }
  const kmAt = (steps, t) => { let s = 1; steps.forEach(p => { if (p.t <= t) s = p.s; }); return s; };
  const kmMedian = steps => { const h = steps.find(p => p.s <= 0.5); return h ? h.t : null; };
  function logrank(groups) { // groups: [{t:[], e:[]}]; k-group log-rank test
    const k = groups.length, times = [...new Set(groups.flatMap(g => g.t.filter((_, i) => g.e[i])))].sort((a, b) => a - b);
    const O = new Array(k).fill(0), E = new Array(k).fill(0), V = Array.from({ length: k }, () => new Array(k).fill(0));
    times.forEach(tt => {
      const nj = groups.map(g => g.t.filter(v => v >= tt).length), dj = groups.map(g => g.t.filter((v, i) => v === tt && g.e[i]).length), N = sum(nj), D = sum(dj);
      if (N < 2) return;
      for (let a = 0; a < k; a++) { O[a] += dj[a]; E[a] += D * nj[a] / N; for (let b = 0; b < k; b++) V[a][b] += D * (N - D) / (N - 1) * nj[a] / N * ((a === b ? 1 : 0) - nj[b] / N); }
    });
    const U = O.slice(0, k - 1).map((o, i) => o - E[i]), Vi = inv(V.slice(0, k - 1).map(r => r.slice(0, k - 1)));
    if (!Vi) return null;
    let X = 0; for (let a = 0; a < k - 1; a++) for (let b = 0; b < k - 1; b++) X += U[a] * Vi[a][b] * U[b];
    return { X, df: k - 1, p: pChi(X, k - 1), O, E };
  }

  /* ---------- language ---------- */
  const T = {
    en: {
      modes: ["Compare groups", "Relationship", "Regression with controls", "Time to ratification"],
      modeHelp: ["Is an outcome different between groups of countries?", "Do two measures move together across countries?", "Which factors still matter once the others are held constant?", "How fast do countries join a treaty, and do some groups join faster?"],
      outcome: "Outcome", group: "Compare across", x: "Explanatory measure", y: "Outcome", preds: "Explanatory factors (up to 4)", add: "Add factor", none: "None", logx: "Log scale", allzero: "All countries: is the average different from zero?",
      try: "Try a question", data: "Download the data (CSV)", res: "Download these results (CSV)", n: "Countries in this analysis", missing: "left out for missing data",
      ev: ["very strong evidence", "strong evidence", "moderate evidence", "weak evidence", "no clear evidence"],
      caveat: "Association, not cause. These figures cover almost every state, not a random sample, so read the p-value as how often a pattern this strong would appear if the grouping or measure were assigned to countries at random. Small groups give wide intervals.",
      method: "How this was calculated", higher: "higher", lower: "lower", yes: "Yes", no: "No", group_: "Group", mean_: "Average", ci: "95% interval", median_: "Median",
      share: "Share", term: "Factor", coef: "Estimate", or_: "Odds ratio", pval: "p-value", intercept: "Intercept", ref: "compared with", std: "Standardized effect (per 1 standard deviation; yes/no factors as is)",
      sepw: "Some countries are perfectly separated by these factors, so the estimates are unstable. Try fewer factors.",
      fewer: "Too few countries with data for this analysis.", small: "Groups with fewer than 3 countries are left out.",
      plain: "What it means",
      hyp: "Hypothesis test", h0: "Null hypothesis (H₀)", h1: "Alternative hypothesis (H₁)", testn: "Test", stat: "Test statistic", alpha: "Significance level (α)", alt: "Alternative hypothesis",
      alts: ["Two-sided (≠)", "Greater than (>)", "Less than (<)"], decision: "Decision",
      rej: a => `Reject H₀ at α = ${a}. A result this extreme would be unlikely if H₀ were true.`,
      keep: a => `Fail to reject H₀ at α = ${a}. The data are compatible with H₀; this does not prove H₀ is true.`,
      rejS: "Reject H₀", keepS: "Not rejected", overall: "Whole model", perfac: "Each factor: H₀ is that its coefficient is 0, holding the others constant.",
      h0note: "The p-value is the probability of a result at least this extreme if H₀ were true. Intervals are 95%.",
      pm: "p-value from", pms: ["Standard test", "Permutation (5,000 reshuffles)"], treaty: "Treaty", allc: "All countries (one curve)",
      pairs: "Which pairs differ?", pair: "Pair", diff: "Difference", praw: "p", pholm: "Holm-adjusted p", yrs: "Years since the treaty was adopted", ratd: "Share of countries that have ratified",
      med: "Median wait", notr: "not reached", by10: "Ratified within 10 years", by25: "Within 25 years", nowr: "Ratified so far", ev_: "ratified"
    },
    id: {
      modes: ["Bandingkan kelompok", "Hubungan", "Regresi dengan kontrol", "Waktu menuju ratifikasi"],
      modeHelp: ["Apakah suatu hasil berbeda antar kelompok negara?", "Apakah dua ukuran bergerak bersama di antara negara?", "Faktor mana yang tetap berpengaruh setelah faktor lain dikendalikan?", "Seberapa cepat negara bergabung dengan suatu perjanjian, dan apakah kelompok tertentu bergabung lebih cepat?"],
      outcome: "Hasil", group: "Bandingkan menurut", x: "Ukuran penjelas", y: "Hasil", preds: "Faktor penjelas (maks. 4)", add: "Tambah faktor", none: "Tidak ada", logx: "Skala log", allzero: "Semua negara: apakah rata-ratanya berbeda dari nol?",
      try: "Coba pertanyaan", data: "Unduh data (CSV)", res: "Unduh hasil ini (CSV)", n: "Negara dalam analisis ini", missing: "tidak diikutkan karena data kosong",
      ev: ["bukti sangat kuat", "bukti kuat", "bukti cukup", "bukti lemah", "tidak ada bukti yang jelas"],
      caveat: "Asosiasi, bukan sebab-akibat. Angka ini mencakup hampir semua negara, bukan sampel acak, jadi baca nilai p sebagai seberapa sering pola sekuat ini muncul jika pengelompokan atau ukuran itu dibagikan ke negara secara acak. Kelompok kecil menghasilkan interval yang lebar.",
      method: "Cara perhitungannya", higher: "lebih tinggi", lower: "lebih rendah", yes: "Ya", no: "Tidak", group_: "Kelompok", mean_: "Rata-rata", ci: "Interval 95%", median_: "Median",
      share: "Persentase", term: "Faktor", coef: "Estimasi", or_: "Rasio odds", pval: "Nilai p", intercept: "Intersep", ref: "dibandingkan dengan", std: "Efek terstandar (per 1 simpangan baku; faktor ya/tidak apa adanya)",
      sepw: "Beberapa negara terpisah sempurna oleh faktor-faktor ini, sehingga estimasinya tidak stabil. Coba lebih sedikit faktor.",
      fewer: "Terlalu sedikit negara dengan data untuk analisis ini.", small: "Kelompok dengan kurang dari 3 negara tidak diikutkan.",
      plain: "Artinya",
      hyp: "Uji hipotesis", h0: "Hipotesis nol (H₀)", h1: "Hipotesis alternatif (H₁)", testn: "Uji", stat: "Statistik uji", alpha: "Tingkat signifikansi (α)", alt: "Hipotesis alternatif",
      alts: ["Dua arah (≠)", "Lebih besar (>)", "Lebih kecil (<)"], decision: "Keputusan",
      rej: a => `Tolak H₀ pada α = ${a}. Hasil seekstrem ini kecil kemungkinannya jika H₀ benar.`,
      keep: a => `Gagal menolak H₀ pada α = ${a}. Data sejalan dengan H₀; ini tidak membuktikan H₀ benar.`,
      rejS: "Tolak H₀", keepS: "Tidak ditolak", overall: "Model keseluruhan", perfac: "Setiap faktor: H₀ adalah koefisiennya 0, dengan faktor lain dianggap tetap.",
      h0note: "Nilai p adalah peluang mendapat hasil seekstrem ini atau lebih jika H₀ benar. Interval 95%.",
      pm: "Nilai p dari", pms: ["Uji standar", "Permutasi (5.000 pengacakan)"], treaty: "Perjanjian", allc: "Semua negara (satu kurva)",
      pairs: "Pasangan mana yang berbeda?", pair: "Pasangan", diff: "Selisih", praw: "p", pholm: "p disesuaikan (Holm)", yrs: "Tahun sejak perjanjian diadopsi", ratd: "Persentase negara yang sudah meratifikasi",
      med: "Median waktu tunggu", notr: "belum tercapai", by10: "Meratifikasi dalam 10 tahun", by25: "Dalam 25 tahun", nowr: "Sudah meratifikasi", ev_: "meratifikasi"
    }
  };
  const lang = () => (document.documentElement.lang || "en").slice(0, 2) === "id" ? "id" : "en";
  const L = () => T[lang()];
  const lab = v => (lang() === "id" && v.label_id) || v.label;
  const evid = p => L().ev[p < 0.001 ? 0 : p < 0.01 ? 1 : p < 0.05 ? 2 : p < 0.1 ? 3 : 4];
  const fp = p => p < 0.001 ? "< 0.001" : fn(p, 3);
  const P = p => p < 0.001 ? "p < 0.001" : "p = " + fn(p, 3);
  const evS = (p, en, id) => p < 0.1 ? sent(`That is <span class="ev">${evid(p)}</span> of ${en}`, `Ini <span class="ev">${evid(p)}</span> adanya ${id}`) : sent(`There is <span class="ev">no clear evidence</span> of ${en}`, `<span class="ev">Tidak ada bukti yang jelas</span> adanya ${id}`);
  function fn(v, d) {
    if (v == null || !isFinite(v)) return "—";
    const a = Math.abs(v); d = d != null ? d : a >= 1000 ? 0 : a >= 100 ? 1 : a >= 1 ? 2 : 3;
    return v.toLocaleString(lang() === "id" ? "id-ID" : "en-GB", { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  const pct = v => fn(v * 100, 1) + "%";
  const esc = s => String(s == null ? "" : s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const sent = (en, id) => lang() === "id" ? id : en;

  /* ---------- styles ---------- */
  const CSS = `
.imrst{white-space:normal;--st-fg:var(--fg,#172D24);--st-mute:var(--muted,#3D5A4D);--st-rule:var(--rule,#B2C7BC);--st-bg:var(--surface,#FFFFFF);--st-acc:#1E6B4A;--st-blue:var(--t4,#256ABF);--st-chip:var(--chip,#D8E5DE);font-size:15px;line-height:1.55;color:var(--st-fg)}
.imrst *{box-sizing:border-box}
.st-modes{display:flex;flex-wrap:wrap;gap:0;border:1px solid var(--st-fg);width:max-content;max-width:100%}
.st-modes button{font:inherit;font-size:14px;font-weight:600;min-height:44px;padding:0 16px;border:0;border-right:1px solid var(--st-fg);background:transparent;color:var(--st-fg);cursor:pointer}
.st-modes button:last-child{border-right:0}
.st-modes button[aria-pressed="true"]{background:var(--st-fg);color:var(--st-bg)}
.st-help{margin:8px 0 0;color:var(--st-mute)}
.st-presets{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 0;align-items:center}
.st-presets span{font-size:13px;color:var(--st-mute);margin-right:4px}
.st-presets button{font:inherit;font-size:13.5px;min-height:36px;padding:4px 12px;border:1px solid var(--st-rule);background:var(--st-bg);color:var(--st-fg);cursor:pointer;text-align:left}
.st-presets button:hover{border-color:var(--st-fg)}
.st-ctl{display:flex;flex-wrap:wrap;gap:12px 16px;margin:18px 0 0;align-items:flex-end}
.st-ctl label{display:flex;flex-direction:column;gap:4px;font-size:13px;color:var(--st-mute);min-width:0;flex:1 1 240px}
.st-ctl label.chk{flex:0 0 auto;flex-direction:row;align-items:center;gap:6px;min-height:40px}
.st-ctl select{font:inherit;font-size:14px;color:var(--st-fg);background:var(--st-bg);border:1px solid var(--st-rule);padding:8px 10px;min-height:40px;max-width:100%;width:100%}
.st-out{margin-top:20px;display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:24px;align-items:start}
.st-chart{border:1px solid var(--st-rule);background:var(--st-bg);padding:12px}
.st-chart svg{display:block;width:100%;height:auto}
.st-chart text{font-family:var(--f-mono,"JetBrains Mono",monospace);font-size:11px;fill:var(--st-mute)}
.st-plain{border-top:4px solid var(--st-fg);padding-top:12px}
.st-plain h3{margin:0 0 8px;font-size:17px}
.st-plain p{margin:0 0 10px}
.st-plain .ev{font-weight:700}
.st-tbl{width:100%;border-collapse:collapse;font-size:13.5px;margin-top:12px}
.st-tbl th{text-align:left;font-weight:600;font-size:12px;color:var(--st-mute);padding:6px 8px 6px 0;border-bottom:1px solid var(--st-fg)}
.st-tbl td{padding:6px 8px 6px 0;border-bottom:1px solid var(--st-rule);vertical-align:top}
.st-tbl td.n{font-family:var(--f-mono,"JetBrains Mono",monospace);font-variant-numeric:tabular-nums;white-space:nowrap}
.st-tw{overflow-x:auto}
.st-note{font-size:13px;color:var(--st-mute);margin:10px 0 0}
.imrst details{margin-top:10px}.imrst summary{cursor:pointer;font-size:13.5px;font-weight:600}
.st-acts{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.st-acts button{font:inherit;font-size:13.5px;font-weight:600;min-height:40px;padding:0 14px;border:1px solid var(--st-fg);background:transparent;color:var(--st-fg);cursor:pointer}
.st-acts button:hover{background:var(--st-fg);color:var(--st-bg)}
.st-preds{display:flex;flex-direction:column;gap:8px;flex:1 1 100%}
.st-preds .row{display:flex;gap:8px;align-items:center}
.st-preds .row select{flex:1}
.st-preds .rm{font:inherit;min-width:40px;min-height:40px;border:1px solid var(--st-rule);background:var(--st-bg);color:var(--st-fg);cursor:pointer}
.st-sig{color:var(--st-acc);font-weight:700}
.st-hyp{border:1px solid var(--st-fg);background:var(--st-bg);padding:12px 14px;margin-bottom:16px}
.st-hyp h3{margin:0 0 8px;font-size:17px}
.st-hyp dl{display:grid;grid-template-columns:minmax(120px,max-content) 1fr;gap:6px 14px;margin:0}
.st-hyp dt{font-size:13px;color:var(--st-mute)}.st-hyp dd{margin:0}
.st-hyp dd.n{font-family:var(--f-mono,"JetBrains Mono",monospace);font-size:13px}
.st-rej{font-weight:700;color:var(--st-acc)}.st-keep{font-weight:700}
@media (max-width:520px){.st-hyp dl{grid-template-columns:1fr}.st-hyp dd{margin-bottom:6px}}
@media (max-width:820px){.st-out{grid-template-columns:1fr}}
`;
  function addCSS() { if (document.getElementById("st-css")) return; const s = document.createElement("style"); s.id = "st-css"; s.textContent = CSS; document.head.appendChild(s); }

  /* ---------- charts (SVG strings) ---------- */
  const W = 560;
  function niceTicks(lo, hi, n) {
    if (lo === hi) { lo -= 1; hi += 1; }
    const step0 = (hi - lo) / (n || 5), mag = Math.pow(10, Math.floor(Math.log10(step0))), f = step0 / mag;
    const step = (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * mag, out = [];
    for (let v = Math.ceil(lo / step) * step; v <= hi + step * 1e-9; v += step) out.push(+v.toPrecision(12));
    return out;
  }
  const tickLab = (v, log) => log ? fn(Math.pow(10, v), Math.pow(10, v) < 10 ? 1 : 0) : fn(v, Math.abs(v) >= 100 || Number.isInteger(v) ? 0 : 1);
  function dotPlot(groups, xlabel, binary) { // groups: [{name, vals:[{id,v}], m, lo, hi}]
    const left = 150, right = 16, rowH = 40, top = 10, H = top + groups.length * rowH + 36;
    let lo = binary ? 0 : Math.min(...groups.flatMap(g => g.vals.map(d => d.v).concat([g.lo]))), hi = binary ? 1 : Math.max(...groups.flatMap(g => g.vals.map(d => d.v).concat([g.hi])));
    const pad = (hi - lo) * 0.04 || 1; if (!binary) { lo -= pad; hi += pad; }
    const ticks = niceTicks(lo, hi, 5); lo = Math.min(lo, ticks[0]); hi = Math.max(hi, ticks[ticks.length - 1]);
    const X = v => left + (v - lo) / (hi - lo) * (W - left - right);
    let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(xlabel)}">`;
    ticks.forEach(t => { s += `<line x1="${X(t)}" x2="${X(t)}" y1="${top}" y2="${H - 30}" stroke="var(--st-rule)" stroke-width="1"/><text x="${X(t)}" y="${H - 16}" text-anchor="middle">${binary ? fn(t * 100, 0) + "%" : tickLab(t)}</text>`; });
    groups.forEach((g, i) => {
      const cy = top + i * rowH + rowH / 2;
      s += `<text x="${left - 10}" y="${cy + 4}" text-anchor="end" style="fill:var(--st-fg)">${esc(g.name.length > 22 ? g.name.slice(0, 21) + "…" : g.name)} (${g.vals.length})</text>`;
      if (binary) {
        s += `<rect x="${X(0)}" y="${cy - 9}" width="${X(g.m) - X(0)}" height="18" fill="var(--st-blue)" opacity=".8"><title>${esc(g.name)}: ${pct(g.m)}</title></rect>`;
      } else {
        g.vals.forEach((d, j) => { const jy = cy + ((j * 7919) % 17 - 8); s += `<circle cx="${X(d.v)}" cy="${jy}" r="3" fill="var(--st-blue)" opacity=".38"><title>${esc(d.id)}: ${fn(d.v)}</title></circle>`; });
      }
      s += `<line x1="${X(g.lo)}" x2="${X(g.hi)}" y1="${cy}" y2="${cy}" stroke="var(--st-fg)" stroke-width="3"/><line x1="${X(g.m)}" x2="${X(g.m)}" y1="${cy - 11}" y2="${cy + 11}" stroke="var(--st-acc)" stroke-width="3"/>`;
    });
    s += `<text x="${(left + W - right) / 2}" y="${H - 2}" text-anchor="middle">${esc(xlabel)}</text></svg>`;
    return s;
  }
  function scatter(pts, xl, yl, line, logx, logy, binary) { // pts: [{id,x,y}], line: fn(x)->{f,lo,hi}
    const l = 52, r = 12, t = 10, b = 40, H = 340;
    const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
    let x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = binary ? 0 : Math.min(...ys), y1 = binary ? 1 : Math.max(...ys);
    const px = (x1 - x0) * 0.04 || 1, py = (y1 - y0) * 0.06 || 1; x0 -= px; x1 += px; if (!binary) { y0 -= py; y1 += py; } else { y0 = -0.08; y1 = 1.08; }
    const X = v => l + (v - x0) / (x1 - x0) * (W - l - r), Y = v => H - b - (v - y0) / (y1 - y0) * (H - t - b);
    let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(yl)} / ${esc(xl)}">`;
    niceTicks(x0, x1, 6).forEach(v => { if (v < x0 || v > x1) return; s += `<line x1="${X(v)}" x2="${X(v)}" y1="${t}" y2="${H - b}" stroke="var(--st-rule)"/><text x="${X(v)}" y="${H - b + 14}" text-anchor="middle">${tickLab(v, logx)}</text>`; });
    (binary ? [0, 0.5, 1] : niceTicks(y0, y1, 5)).forEach(v => { if (v < y0 || v > y1) return; s += `<line x1="${l}" x2="${W - r}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--st-rule)"/><text x="${l - 6}" y="${Y(v) + 4}" text-anchor="end">${binary ? fn(v * 100, 0) + "%" : tickLab(v, logy)}</text>`; });
    if (line) {
      const steps = 60, seg = [], up = [], dn = [];
      for (let i = 0; i <= steps; i++) { const xv = x0 + px + (x1 - x0 - 2 * px) * i / steps, o = line(xv); seg.push(`${X(xv)},${Y(o.f)}`); up.push(`${X(xv)},${Y(o.hi)}`); dn.unshift(`${X(xv)},${Y(o.lo)}`); }
      s += `<polygon points="${up.concat(dn).join(" ")}" fill="var(--st-acc)" opacity=".12"/><polyline points="${seg.join(" ")}" fill="none" stroke="var(--st-acc)" stroke-width="2.5"/>`;
    }
    pts.forEach((p, i) => { const yy = binary ? p.y + ((i * 7919) % 13 - 6) / 100 : p.y; s += `<circle cx="${X(p.x)}" cy="${Y(yy)}" r="3.5" fill="var(--st-blue)" opacity=".5"><title>${esc(p.id)}: ${tickLab(p.x, logx)}, ${binary ? (p.y ? L().yes : L().no) : tickLab(p.y, logy)}</title></circle>`; });
    s += `<text x="${(l + W - r) / 2}" y="${H - 6}" text-anchor="middle">${esc(xl)}${logx ? " (log)" : ""}</text>`;
    s += `<text transform="translate(12 ${(t + H - b) / 2}) rotate(-90)" text-anchor="middle">${esc(yl)}${logy ? " (log)" : ""}</text></svg>`;
    return s;
  }
  function forest(rows) { // rows: [{name, est, lo, hi, p}]
    const left = 190, right = 16, rowH = 30, top = 10, H = top + rows.length * rowH + 34;
    let lo = Math.min(0, ...rows.map(r => r.lo)), hi = Math.max(0, ...rows.map(r => r.hi)); const pad = (hi - lo) * 0.05 || 1; lo -= pad; hi += pad;
    const X = v => left + (v - lo) / (hi - lo) * (W - left - right);
    let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Coefficients">`;
    niceTicks(lo, hi, 5).forEach(t => { s += `<line x1="${X(t)}" x2="${X(t)}" y1="${top}" y2="${H - 28}" stroke="var(--st-rule)"/><text x="${X(t)}" y="${H - 14}" text-anchor="middle">${fn(t, 1)}</text>`; });
    s += `<line x1="${X(0)}" x2="${X(0)}" y1="${top}" y2="${H - 28}" stroke="var(--st-fg)" stroke-dasharray="3 3"/>`;
    rows.forEach((r, i) => { const cy = top + i * rowH + rowH / 2, c = r.p < 0.05 ? "var(--st-acc)" : "var(--st-mute)";
      s += `<text x="${left - 8}" y="${cy + 4}" text-anchor="end" style="fill:var(--st-fg)">${esc(r.name.length > 28 ? r.name.slice(0, 27) + "…" : r.name)}</text><line x1="${X(r.lo)}" x2="${X(r.hi)}" y1="${cy}" y2="${cy}" stroke="${c}" stroke-width="3"/><circle cx="${X(r.est)}" cy="${cy}" r="5" fill="${c}"><title>${esc(r.name)}: ${fn(r.est)} (${fn(r.lo)} to ${fn(r.hi)})</title></circle>`; });
    return s + "</svg>";
  }

  /* ---------- component ---------- */
  function mount(el, cfg) {
    addCSS();
    const st = { mode: 0, y: null, g: null, x: null, y2: null, logx: false, logy: false, ry: null, preds: [], alpha: 0.05, alt: "two", perm: false, ev: null, sg: "__all" };
    const SURV = cfg.surv || null; if (SURV) st.ev = SURV.events[0].key;
    const permOn = () => st.perm && (st.mode === 0 || st.mode === 1);
    const pick = (p, pm) => permOn() ? pm.p : p;
    const tname = (en, id, cap) => permOn() ? (cap ? sent(`Permutation test (${fn(NPERM, 0)} reshuffles)`, `Uji permutasi (${fn(NPERM, 0)} pengacakan)`) : sent("permutation test", "uji permutasi")) : sent(en, id);
    const pmExtra = (std, pm) => permOn() ? sent("standard test ", "uji standar ") + P(std) : sent("permutation ", "permutasi ") + P(pm.p);
    const pmLine = (pm, en, id) => sent(`Reshuffling ${en} ${fn(pm.B, 0)} times, as if they had been assigned at random, gives a permutation ${P(pm.p)}.`, `Mengacak ${id} sebanyak ${fn(pm.B, 0)} kali, seolah-olah dibagikan secara acak, memberi ${P(pm.p)} (uji permutasi).`);
    const adj = (p, s) => st.alt === "two" ? p : ((st.alt === "greater") === (s > 0) ? p / 2 : 1 - p / 2);
    const sym = () => ({ two: "≠", greater: ">", less: "<" })[st.alt];
    const V = cfg.vars.filter(v => cfg.rows.some(r => r[v.key] != null && r[v.key] !== ""));
    const byKey = Object.fromEntries(V.map(v => [v.key, v]));
    const of = types => V.filter(v => types.includes(v.type));
    const first = (types, pref) => (pref && byKey[pref] && types.includes(byKey[pref].type) ? pref : (of(types)[0] || {}).key);
    st.y = first(["num", "bin"], cfg.defaults && cfg.defaults.y); st.g = first(["cat", "bin"], cfg.defaults && cfg.defaults.g);
    st.x = first(["num"], cfg.defaults && cfg.defaults.x); st.y2 = first(["num", "bin"], cfg.defaults && cfg.defaults.y2) ; st.ry = st.y2;
    st.logx = !!(byKey[st.x] && byKey[st.x].log);
    let lastRes = [];
    el.classList.add("imrst"); el.setAttribute("data-noi18n", "");

    const val = (r, k) => { const v = r[k]; return v == null || v === "" || (typeof v === "number" && !isFinite(v)) ? null : v; };
    const groupName = (v, x) => v.type === "bin" ? (x ? (lang() === "id" && v.yes_id) || v.yes || L().yes : (lang() === "id" && v.no_id) || v.no || L().no) : (lang() === "id" && v.cats_id && v.cats_id[x]) || x;
    const opts = (types, sel, extra) => (extra || "") + of(types).map(v => `<option value="${v.key}"${v.key === sel ? " selected" : ""}>${esc(lab(v))}</option>`).join("");

    function controls() {
      const l = L(); let h = "";
      if (st.mode === 0) {
        const allz = byKey[st.y] && byKey[st.y].zero;
        h += `<label>${l.outcome}<select data-k="y">${opts(["num", "bin"], st.y)}</select></label>`;
        h += `<label>${l.group}<select data-k="g">${allz ? `<option value="__all"${st.g === "__all" ? " selected" : ""}>${l.allzero}</option>` : ""}${opts(["cat", "bin"], st.g)}</select></label>`;
      } else if (st.mode === 1) {
        h += `<label>${l.x}<select data-k="x">${opts(["num"], st.x)}</select></label>`;
        h += `<label class="chk"><input type="checkbox" data-k="logx"${st.logx ? " checked" : ""}> ${l.logx}</label>`;
        h += `<label>${l.y}<select data-k="y2">${opts(["num", "bin"], st.y2)}</select></label>`;
        if (byKey[st.y2] && byKey[st.y2].type === "num") h += `<label class="chk"><input type="checkbox" data-k="logy"${st.logy ? " checked" : ""}> ${l.logx}</label>`;
      } else if (st.mode === 3) {
        h += `<label>${l.treaty}<select data-k="ev">${SURV.events.map(e => `<option value="${e.key}"${e.key === st.ev ? " selected" : ""}>${esc((lang() === "id" && e.label_id) || e.label)}</option>`).join("")}</select></label>`;
        h += `<label>${l.group}<select data-k="sg"><option value="__all"${st.sg === "__all" ? " selected" : ""}>${l.allc}</option>${opts(["cat", "bin"], st.sg)}</select></label>`;
      } else {
        h += `<label>${l.y}<select data-k="ry">${opts(["num", "bin"], st.ry)}</select></label>`;
        h += `<div class="st-preds"><span style="font-size:13px;color:var(--st-mute)">${l.preds}</span>` + st.preds.map((p, i) => `<div class="row"><select data-p="${i}" aria-label="${l.preds} ${i + 1}">${opts(["num", "bin", "cat"], p)}</select><button type="button" class="rm" data-rm="${i}" aria-label="Remove">×</button></div>`).join("") +
          (st.preds.length < 4 ? `<div><button type="button" class="st-addp" style="font:inherit;font-size:13.5px;min-height:40px;padding:0 14px;border:1px dashed var(--st-fg);background:transparent;color:var(--st-fg);cursor:pointer">+ ${l.add}</button></div>` : "") + `</div>`;
      }
      const altOK = st.mode === 1 || (st.mode === 0 && (st.g === "__all" || (byKey[st.g] && byKey[st.g].type === "bin")));
      if (!altOK) st.alt = "two";
      h += `<label style="flex:0 1 200px">${l.alpha}<select data-k="alpha">${[0.1, 0.05, 0.01].map(a => `<option value="${a}"${st.alpha === a ? " selected" : ""}>${fn(a, 2)}</option>`).join("")}</select></label>`;
      if (st.mode < 2) h += `<label style="flex:0 1 240px">${l.pm}<select data-k="perm">${l.pms.map((m, i) => `<option value="${i}"${+st.perm === i ? " selected" : ""}>${m}</option>`).join("")}</select></label>`;
      if (altOK) h += `<label style="flex:0 1 220px">${l.alt}<select data-k="alt">${["two", "greater", "less"].map((a, i) => `<option value="${a}"${st.alt === a ? " selected" : ""}>${l.alts[i]}</option>`).join("")}</select></label>`;
      return h;
    }

    function render() {
      const l = L();
      const presets = (cfg.presets || []).filter(p => [p.y, p.g, p.x, p.y2, p.ry, p.sg, ...(p.preds || [])].every(k => !k || k === "__all" || byKey[k]) && (p.mode !== 3 || (SURV && SURV.events.some(e => e.key === p.ev))));
      el.innerHTML = `<div class="st-modes" role="group" aria-label="Analysis">${l.modes.map((m, i) => i === 3 && !SURV ? "" : `<button type="button" data-mode="${i}" aria-pressed="${st.mode === i}">${m}</button>`).join("")}</div>
        <p class="st-help">${l.modeHelp[st.mode]}</p>
        ${presets.length ? `<div class="st-presets"><span>${l.try}:</span>${presets.map((p, i) => `<button type="button" data-preset="${i}">${esc(lang() === "id" && p.q_id || p.q)}</button>`).join("")}</div>` : ""}
        <div class="st-ctl">${controls()}</div>
        <div class="st-out" aria-live="polite"></div>
        <div class="st-acts"><button type="button" data-dl="data">${l.data}</button><button type="button" data-dl="res">${l.res}</button></div>
        ${cfg.note ? `<p class="st-note">${lang() === "id" && cfg.note_id || cfg.note}</p>` : ""}`;
      el.querySelectorAll("[data-mode]").forEach(b => b.onclick = () => { st.mode = +b.dataset.mode; if (st.mode === 2 && !st.preds.length) st.preds = (cfg.defaults && cfg.defaults.preds || [st.x]).filter(k => byKey[k]); render(); });
      el.querySelectorAll("[data-preset]").forEach(b => b.onclick = () => { const p = presets[+b.dataset.preset]; Object.assign(st, { mode: p.mode, logx: !!p.logx, logy: !!p.logy, alt: "two" }); ["y", "g", "x", "y2", "ry", "ev", "sg"].forEach(k => { if (p[k]) st[k] = p[k]; }); if (p.preds) st.preds = p.preds.slice(); render(); });
      el.querySelectorAll(".st-ctl select[data-k]").forEach(s => s.onchange = () => { st[s.dataset.k] = s.dataset.k === "alpha" ? +s.value : s.dataset.k === "perm" ? s.value === "1" : s.value; if (s.dataset.k === "x") st.logx = !!byKey[s.value].log; if (s.dataset.k === "y2") st.logy = false; if (s.dataset.k === "y" && st.g === "__all" && !byKey[s.value].zero) st.g = first(["cat", "bin"]); render(); });
      el.querySelectorAll(".st-ctl input[data-k]").forEach(c => c.onchange = () => { st[c.dataset.k] = c.checked; render(); });
      el.querySelectorAll("[data-p]").forEach(s => s.onchange = () => { st.preds[+s.dataset.p] = s.value; render(); });
      el.querySelectorAll("[data-rm]").forEach(b => b.onclick = () => { st.preds.splice(+b.dataset.rm, 1); render(); });
      const ap = el.querySelector(".st-addp"); if (ap) ap.onclick = () => { const k = of(["num", "bin", "cat"]).find(v => v.key !== st.ry && !st.preds.includes(v.key)); if (k) st.preds.push(k.key); render(); };
      el.querySelectorAll("[data-dl]").forEach(b => b.onclick = () => download(b.dataset.dl));
      const out = el.querySelector(".st-out");
      try { out.innerHTML = [compare, relate, regress, survival][st.mode](); } catch (e) { out.innerHTML = `<p class="st-note">${esc(e.message)}</p>`; }
    }

    function hypBox(h) {
      const l = L(), rej = h.p < st.alpha, a = fn(st.alpha, 2);
      return `<div class="st-hyp"><h3>${l.hyp}</h3><dl>
        <dt>${l.h0}</dt><dd>${h.h0}</dd><dt>${l.h1}</dt><dd>${h.h1}</dd>
        <dt>${l.testn}</dt><dd>${h.test}</dd><dt>${l.stat}</dt><dd class="n">${h.stat}; ${P(h.p)}${h.extra ? "; " + h.extra : ""}</dd>
        <dt>${l.decision}</dt><dd class="${rej ? "st-rej" : "st-keep"}">${rej ? l.rej(a) : l.keep(a)}</dd></dl>
        ${h.note ? `<p class="st-note">${h.note}</p>` : ""}<p class="st-note">${l.h0note}</p></div>`;
    }
    function plain(title, paras, n, dropped, extra, hyp) {
      const l = L();
      return `${hyp ? hypBox(hyp) : ""}<div class="st-plain"><h3>${l.plain}</h3>${paras.map(p => `<p>${p}</p>`).join("")}<p class="st-note">${l.n}: ${n}${dropped ? `; ${dropped} ${l.missing}` : ""}.</p><p class="st-note">${l.caveat}</p>${extra || ""}</div>`;
    }
    const methodBox = html => `<details><summary>${L().method}</summary>${html}</details>`;

    /* ---- compare groups ---- */
    function compare() {
      const l = L(), yv = byKey[st.y]; if (!yv) return `<p class="st-note">${l.fewer}</p>`;
      const ybin = yv.type === "bin";
      if (st.g === "__all") {
        const rs = cfg.rows.filter(r => val(r, st.y) != null), a = rs.map(r => +r[st.y]), dropped = cfg.rows.length - rs.length;
        if (a.length < 5) return `<p class="st-note">${l.fewer}</p>`;
        const o = oneSample(a), w = signedRank(a), pm = permSign(a, st.alt), pa = pick(adj(o.p, o.t), pm);
        lastRes = [["test", "n", "mean", "ci_low", "ci_high", "t", "df", "p", "wilcoxon_p"], ["one-sample t", o.n, o.m, o.lo, o.hi, o.t, o.df, o.p, w ? w.p : ""], [], ["sign_flip_permutation_p", "reshuffles", "alternative"], [pm.p, pm.B, st.alt]];
        const dir = o.m > 0 ? l.higher : l.lower;
        const chart = dotPlot([{ name: lab(yv), vals: rs.map(r => ({ id: r[cfg.idKey || "id"], v: +r[st.y] })), m: o.m, lo: o.lo, hi: o.hi }], lab(yv));
        const p1 = sent(`On average, <b>${esc(lab(yv))}</b> is ${fn(o.m)} (95% interval ${fn(o.lo)} to ${fn(o.hi)}). ${evS(pa, "a change away from zero", "perubahan dari nol")} (${tname("one-sample t-test", "uji t satu sampel")}, ${P(pa)}).`,
          `Rata-rata <b>${esc(lab(yv))}</b> adalah ${fn(o.m)} (interval 95% ${fn(o.lo)} sampai ${fn(o.hi)}). ${evS(pa, "a change away from zero", "perubahan dari nol")} (${tname("one-sample t-test", "uji t satu sampel")}, ${P(pa)}).`);
        const p2 = (w ? sent(`The rank-based Wilcoxon test gives ${P(w.p)}. `, `Uji Wilcoxon berbasis peringkat memberi ${P(w.p)}. `) : "") + sent(`Flipping the sign of each country's value at random ${fn(pm.B, 0)} times gives a permutation ${P(pm.p)}.`, `Membalik tanda nilai tiap negara secara acak sebanyak ${fn(pm.B, 0)} kali memberi ${P(pm.p)} (uji permutasi).`);
        return `<div class="st-chart">${chart}</div>${plain("", [p1, p2], o.n, dropped, methodBox(`<p class="st-note">One-sample t-test of the mean against zero, t(${fn(o.df, 0)}) = ${fn(o.t)}; Wilcoxon signed-rank test with normal approximation.</p>`), { h0: sent(`The average ${esc(lab(yv))} is 0 (μ = 0).`, `Rata-rata ${esc(lab(yv))} adalah 0 (μ = 0).`), h1: sent(`The average is ${({two:'not equal to',greater:'greater than',less:'less than'})[st.alt]} 0 (μ ${sym()} 0).`, `Rata-ratanya ${({two:'tidak sama dengan',greater:'lebih besar dari',less:'lebih kecil dari'})[st.alt]} 0 (μ ${sym()} 0).`), test: tname('One-sample t-test', 'Uji t satu sampel', 1), stat: `t(${fn(o.df, 0)}) = ${fn(o.t)}`, p: pa, extra: pmExtra(adj(o.p, o.t), pm) })}`;
      }
      const gv = byKey[st.g]; if (!gv) return `<p class="st-note">${l.fewer}</p>`;
      const rs = cfg.rows.filter(r => val(r, st.y) != null && val(r, st.g) != null), dropped = cfg.rows.length - rs.length;
      const keys = [...new Set(rs.map(r => r[st.g]))];
      let groups = keys.map(k => ({ key: k, name: groupName(gv, k), rows: rs.filter(r => r[st.g] === k) }));
      const tooSmall = groups.some(g => g.rows.length < 3); groups = groups.filter(g => g.rows.length >= 3);
      if (groups.length < 2) return `<p class="st-note">${l.fewer}</p>`;
      if (gv.type === "bin") groups.sort((a, b) => (b.key ? 1 : 0) - (a.key ? 1 : 0)); else if (gv.order) groups.sort((a, b) => gv.order.indexOf(a.key) - gv.order.indexOf(b.key));
      const N = sum(groups.map(g => g.rows.length));
      if (!ybin) {
        groups.forEach(g => { g.a = g.rows.map(r => +r[st.y]); g.m = mean(g.a); const se = sd(g.a) / Math.sqrt(g.a.length), tc = tCrit(g.a.length - 1); g.lo = g.m - tc * se; g.hi = g.m + tc * se; g.vals = g.rows.map(r => ({ id: r[cfg.idKey || "id"], v: +r[st.y] })); g.med = quantile(g.a, 0.5); });
        const chart = dotPlot(groups, lab(yv));
        const tbl = `<div class="st-tw"><table class="st-tbl"><thead><tr><th>${l.group_}</th><th>n</th><th>${l.mean_}</th><th>${l.ci}</th><th>${l.median_}</th></tr></thead><tbody>${groups.map(g => `<tr><td>${esc(g.name)}</td><td class="n">${g.a.length}</td><td class="n">${fn(g.m)}</td><td class="n">${fn(g.lo)} – ${fn(g.hi)}</td><td class="n">${fn(g.med)}</td></tr>`).join("")}</tbody></table></div>`;
        let paras, meth, hyp, pw = null;
        if (groups.length === 2) {
          const [A, B] = groups, w = welch(A.a, B.a), u = mannWhitney(A.a, B.a), dir = w.d > 0 ? l.higher : l.lower, pm = permDiff(A.a, B.a, st.alt), pa = pick(adj(w.p, w.t), pm);
          hyp = { h0: sent(`The average ${esc(lab(yv))} is the same in ${esc(A.name)} and ${esc(B.name)} (μ₁ = μ₂).`, `Rata-rata ${esc(lab(yv))} sama pada ${esc(A.name)} dan ${esc(B.name)} (μ₁ = μ₂).`), h1: sent(`The average in ${esc(A.name)} is ${({two:"different from that",greater:"higher than that",less:"lower than that"})[st.alt]} in ${esc(B.name)} (μ₁ ${sym()} μ₂).`, `Rata-rata pada ${esc(A.name)} ${({two:"berbeda dari",greater:"lebih tinggi dari",less:"lebih rendah dari"})[st.alt]} pada ${esc(B.name)} (μ₁ ${sym()} μ₂).`), test: tname("Welch t-test", "Uji t Welch", 1), stat: `t(${fn(w.df, 1)}) = ${fn(w.t)}`, p: pa, extra: `Mann-Whitney ${P(adj(u.p, u.z))}; ${pmExtra(adj(w.p, w.t), pm)}` };
          lastRes = [["group_a", "group_b", "n_a", "n_b", "mean_a", "mean_b", "difference", "ci_low", "ci_high", "welch_t", "df", "p", "cohens_d", "mann_whitney_p", "permutation_p", "reshuffles", "alternative"], [A.name, B.name, A.a.length, B.a.length, A.m, B.m, w.d, w.lo, w.hi, w.t, w.df, w.p, w.cohen, u.p, pm.p, pm.B, st.alt]];
          paras = [sent(`<b>${esc(lab(yv))}</b> is ${dir} in <b>${esc(A.name)}</b> (average ${fn(A.m)}) than in <b>${esc(B.name)}</b> (${fn(B.m)}), by ${fn(Math.abs(w.d))} (95% interval for the difference: ${fn(w.d < 0 ? -w.hi : w.lo)} to ${fn(w.d < 0 ? -w.lo : w.hi)}).`,
              `<b>${esc(lab(yv))}</b> ${dir} pada <b>${esc(A.name)}</b> (rata-rata ${fn(A.m)}) dibanding <b>${esc(B.name)}</b> (${fn(B.m)}), selisih ${fn(Math.abs(w.d))} (interval 95% untuk selisih: ${fn(w.d < 0 ? -w.hi : w.lo)} sampai ${fn(w.d < 0 ? -w.lo : w.hi)}).`),
            sent(`${evS(pa, "a real difference", "perbedaan nyata")} (${tname("Welch t-test", "uji t Welch")}, ${P(pa)}). The rank-based Mann-Whitney test, which is less affected by outliers, gives ${P(adj(u.p, u.z))}. The size of the gap is ${Math.abs(w.cohen) < 0.2 ? "negligible" : Math.abs(w.cohen) < 0.5 ? "small" : Math.abs(w.cohen) < 0.8 ? "medium" : "large"} (Cohen's d = ${fn(w.cohen)}).`,
              `${evS(pa, "a real difference", "perbedaan nyata")} (${tname("Welch t-test", "uji t Welch")}, ${P(pa)}). Uji Mann-Whitney berbasis peringkat, yang kurang terpengaruh pencilan, memberi ${P(adj(u.p, u.z))}. Besarnya selisih ${Math.abs(w.cohen) < 0.2 ? "sangat kecil" : Math.abs(w.cohen) < 0.5 ? "kecil" : Math.abs(w.cohen) < 0.8 ? "sedang" : "besar"} (Cohen's d = ${fn(w.cohen)}).`), pmLine(pm, "the group labels", "label kelompok")];
          meth = `<p class="st-note">Welch's t-test (unequal variances): t(${fn(w.df, 1)}) = ${fn(w.t)}. Mann-Whitney U = ${fn(u.U, 0)}, z = ${fn(u.z)}, with tie correction. 95% intervals for group means use the t distribution.</p>`;
        } else {
          const an = anova(groups.map(g => g.a)), kw = kruskal(groups.map(g => g.a)), srt = [...groups].sort((a, b) => b.m - a.m), pm = permGroups(groups.map(g => g.a)), pa = pick(an.p, pm);
          pw = pairwise(groups, (A, B) => permOn() ? permDiff(A.a, B.a, "two", NPAIR).p : welch(A.a, B.a).p, (A, B) => A.m - B.m, false);
          hyp = { h0: sent(`The average ${esc(lab(yv))} is the same in all ${groups.length} groups.`, `Rata-rata ${esc(lab(yv))} sama pada ke-${groups.length} kelompok.`), h1: sent("At least one group's average differs.", "Setidaknya satu kelompok memiliki rata-rata berbeda."), test: tname("One-way ANOVA", "ANOVA satu arah", 1), stat: `F(${an.d1}, ${an.d2}) = ${fn(an.F)}`, p: pa, extra: `Kruskal-Wallis ${P(kw.p)}; ${pmExtra(an.p, pm)}` };
          lastRes = [["group", "n", "mean", "ci_low", "ci_high", "median"], ...groups.map(g => [g.name, g.a.length, g.m, g.lo, g.hi, g.med]), [], ["anova_F", "df1", "df2", "p", "eta_squared", "kruskal_H", "kruskal_p", "permutation_p", "reshuffles"], [an.F, an.d1, an.d2, an.p, an.eta2, kw.H, kw.p, pm.p, pm.B], [], ...pw.csv];
          paras = [sent(`Average <b>${esc(lab(yv))}</b> is highest in <b>${esc(srt[0].name)}</b> (${fn(srt[0].m)}) and lowest in <b>${esc(srt[srt.length - 1].name)}</b> (${fn(srt[srt.length - 1].m)}).`,
              `Rata-rata <b>${esc(lab(yv))}</b> tertinggi pada <b>${esc(srt[0].name)}</b> (${fn(srt[0].m)}) dan terendah pada <b>${esc(srt[srt.length - 1].name)}</b> (${fn(srt[srt.length - 1].m)}).`),
            sent(`${evS(pa, "a difference between the groups", "perbedaan antarkelompok")} (${tname("ANOVA", "ANOVA")}, ${P(pa)}; the rank-based Kruskal-Wallis test gives ${P(kw.p)}). Group membership accounts for ${fn(an.eta2 * 100, 0)}% of the variation between countries.`,
              `${evS(pa, "a difference between the groups", "perbedaan antarkelompok")} (${tname("ANOVA", "ANOVA")}, ${P(pa)}; uji Kruskal-Wallis berbasis peringkat memberi ${P(kw.p)}). Keanggotaan kelompok menjelaskan ${fn(an.eta2 * 100, 0)}% variasi antarnegara.`), pmLine(pm, "the group labels", "label kelompok"), pw.say];
          meth = `<p class="st-note">One-way ANOVA: F(${an.d1}, ${an.d2}) = ${fn(an.F)}, η² = ${fn(an.eta2)}. Kruskal-Wallis H = ${fn(kw.H)}, df = ${kw.df}, with tie correction. Pairwise comparisons use ${permOn() ? `permutation tests (${fn(NPAIR, 0)} reshuffles per pair)` : "Welch t-tests"}, with Holm's step-down correction for the ${pw.m} comparisons.</p>`;
        }
        return `<div class="st-chart">${chart}${tbl}${pw ? pw.tbl : ""}${tooSmall ? `<p class="st-note">${l.small}</p>` : ""}</div>${plain("", paras, N, dropped, methodBox(meth), hyp)}`;
      }
      // binary outcome
      groups.forEach(g => { g.k = g.rows.filter(r => !!r[st.y]).length; g.n = g.rows.length; const w = wilson(g.k, g.n); g.m = w.p; g.lo = w.lo; g.hi = w.hi; g.vals = g.rows.map(r => ({ id: r[cfg.idKey || "id"], v: r[st.y] ? 1 : 0 })); });
      const tab = groups.map(g => [g.k, g.n - g.k]), cs = chisq(tab);
      const yes = esc((lang() === "id" && yv.yes_id) || yv.yes || lab(yv)), phr = esc((lang() === "id" && yv.phrase_id) || yv.phrase || sent("fall under “" + ((yv.yes) || lab(yv)) + "”", "termasuk “" + ((yv.yes_id) || lab(yv)) + "”"));
      const chart = dotPlot(groups, `${lab(yv)} (%)`, true);
      const tbl = `<div class="st-tw"><table class="st-tbl"><thead><tr><th>${l.group_}</th><th>n</th><th>${l.share}</th><th>${l.ci}</th></tr></thead><tbody>${groups.map(g => `<tr><td>${esc(g.name)}</td><td class="n">${g.k} / ${g.n}</td><td class="n">${pct(g.m)}</td><td class="n">${pct(g.lo)} – ${pct(g.hi)}</td></tr>`).join("")}</tbody></table></div>`;
      let paras, meth, p, hyp, pw = null;
      if (groups.length === 2) {
        const [A, B] = groups, d = A.m - B.m, nlo = d - Math.sqrt(Math.pow(A.m - A.lo, 2) + Math.pow(B.hi - B.m, 2)), nhi = d + Math.sqrt(Math.pow(A.hi - A.m, 2) + Math.pow(B.m - B.lo, 2)), dlo = d < 0 ? -nhi : nlo, dhi = d < 0 ? -nlo : nhi, se = Math.sqrt(A.m * (1 - A.m) / A.n + B.m * (1 - B.m) / B.n);
        const useF = cs.minE < 5, pstd = adj(useF ? fisher(A.k, A.n - A.k, B.k, B.n - B.k) : cs.p, d), pm = permDiff(A.rows.map(r => r[st.y] ? 1 : 0), B.rows.map(r => r[st.y] ? 1 : 0), st.alt); p = pick(pstd, pm);
        hyp = { h0: sent(`The share that ${phr} is the same in ${esc(A.name)} and ${esc(B.name)} (π₁ = π₂).`, `Persentase yang ${phr} sama pada ${esc(A.name)} dan ${esc(B.name)} (π₁ = π₂).`), h1: sent(`The share in ${esc(A.name)} is ${({two:"different from that",greater:"higher than that",less:"lower than that"})[st.alt]} in ${esc(B.name)} (π₁ ${sym()} π₂).`, `Persentase pada ${esc(A.name)} ${({two:"berbeda dari",greater:"lebih tinggi dari",less:"lebih rendah dari"})[st.alt]} pada ${esc(B.name)} (π₁ ${sym()} π₂).`), test: permOn() ? tname("", "", 1) : useF ? sent("Fisher's exact test", "Uji eksak Fisher") : sent("Chi-square test", "Uji chi-kuadrat"), stat: permOn() ? `${sent("difference", "selisih")} = ${fn(d * 100, 1)} ${sent("percentage points", "poin persentase")}` : useF ? sent("exact", "eksak") : `χ²(1) = ${fn(cs.X)}`, p, extra: pmExtra(pstd, pm) };
        const a = A.k + .5, b = A.n - A.k + .5, c = B.k + .5, dd = B.n - B.k + .5, or = a * dd / (b * c), sl = Math.sqrt(1 / a + 1 / b + 1 / c + 1 / dd);
        lastRes = [["group_a", "group_b", "share_a", "share_b", "difference", "ci_low", "ci_high", "odds_ratio", "or_low", "or_high", useF ? "fisher_p" : "chi2_p", "permutation_p", "reshuffles", "alternative"], [A.name, B.name, A.m, B.m, d, nlo, nhi, or, or * Math.exp(-Z95 * sl), or * Math.exp(Z95 * sl), pstd, pm.p, pm.B, st.alt]];
        paras = [sent(`Among <b>${esc(A.name)}</b>, ${pct(A.m)} (${A.k} of ${A.n}) ${phr}, against ${pct(B.m)} (${B.k} of ${B.n}) among <b>${esc(B.name)}</b>: a gap of ${fn(Math.abs(d) * 100, 1)} percentage points (95% interval ${fn(dlo * 100, 1)} to ${fn(dhi * 100, 1)}).`,
            `Di antara <b>${esc(A.name)}</b>, ${pct(A.m)} (${A.k} dari ${A.n}) ${phr}, dibanding ${pct(B.m)} (${B.k} dari ${B.n}) di antara <b>${esc(B.name)}</b>: selisih ${fn(Math.abs(d) * 100, 1)} poin persentase (interval 95% ${fn(dlo * 100, 1)} sampai ${fn(dhi * 100, 1)}).`),
          sent(`${evS(p, "a real difference", "perbedaan nyata")} (${permOn() ? tname("", "") : useF ? "Fisher's exact test" : "chi-square test"}, ${P(p)}). The odds are ${fn(or)} times as high in the first group.`,
            `${evS(p, "a real difference", "perbedaan nyata")} (${permOn() ? tname("", "") : useF ? "uji eksak Fisher" : "uji chi-kuadrat"}, ${P(p)}). Peluangnya (odds) ${fn(or)} kali pada kelompok pertama.`), pmLine(pm, "the group labels", "label kelompok")];
        meth = `<p class="st-note">${useF ? "Fisher's exact test (some expected counts below 5)" : `Pearson chi-square = ${fn(cs.X)}, df = 1`}. Intervals for shares are Wilson score intervals; the difference uses Newcombe's hybrid score interval; the odds ratio adds 0.5 to each cell.</p>`;
      } else {
        const pm = permGroups(groups.map(g => g.rows.map(r => r[st.y] ? 1 : 0))), srt = [...groups].sort((a, b) => b.m - a.m); p = pick(cs.p, pm);
        pw = pairwise(groups, (A, B) => permOn() ? permDiff(A.vals.map(v => v.v), B.vals.map(v => v.v), "two", NPAIR).p : fisher(A.k, A.n - A.k, B.k, B.n - B.k), (A, B) => A.m - B.m, true);
        hyp = { h0: sent(`The share that ${phr} is the same in all ${groups.length} groups.`, `Persentase yang ${phr} sama pada ke-${groups.length} kelompok.`), h1: sent("The share differs in at least one group.", "Persentasenya berbeda setidaknya pada satu kelompok."), test: tname("Chi-square test of independence", "Uji chi-kuadrat independensi", 1), stat: `χ²(${cs.df}) = ${fn(cs.X)}`, p, extra: pmExtra(cs.p, pm) };
        lastRes = [["group", "yes", "n", "share", "ci_low", "ci_high"], ...groups.map(g => [g.name, g.k, g.n, g.m, g.lo, g.hi]), [], ["chi2", "df", "p", "cramers_v", "permutation_p", "reshuffles"], [cs.X, cs.df, cs.p, cs.V, pm.p, pm.B], [], ...pw.csv];
        paras = [sent(`The share of countries that ${phr} ranges from ${pct(srt[srt.length - 1].m)} in <b>${esc(srt[srt.length - 1].name)}</b> to ${pct(srt[0].m)} in <b>${esc(srt[0].name)}</b>.`,
            `Persentase negara yang ${phr} berkisar dari ${pct(srt[srt.length - 1].m)} pada <b>${esc(srt[srt.length - 1].name)}</b> sampai ${pct(srt[0].m)} pada <b>${esc(srt[0].name)}</b>.`),
          sent(`${evS(p, "a difference between the groups", "perbedaan antarkelompok")} (${tname("chi-square test", "uji chi-kuadrat")}, ${P(p)}; Cramér's V = ${fn(cs.V)}).`, `${evS(p, "a difference between the groups", "perbedaan antarkelompok")} (${tname("chi-square test", "uji chi-kuadrat")}, ${P(p)}; V Cramér = ${fn(cs.V)}).`), pmLine(pm, "the group labels", "label kelompok"), pw.say];
        meth = `<p class="st-note">Pearson chi-square = ${fn(cs.X)}, df = ${cs.df}${cs.minE < 5 ? "; some expected counts are below 5, so treat the p-value with caution" : ""}. Wilson score intervals for each share. Pairwise comparisons use ${permOn() ? `permutation tests (${fn(NPAIR, 0)} reshuffles per pair)` : "Fisher's exact test"}, with Holm's step-down correction for the ${pw.m} comparisons.</p>`;
      }
      return `<div class="st-chart">${chart}${tbl}${pw ? pw.tbl : ""}${tooSmall ? `<p class="st-note">${l.small}</p>` : ""}</div>${plain("", paras, N, dropped, methodBox(meth), hyp)}`;
    }

    /* ---- pairwise comparisons after a k-group test, Holm-corrected ---- */
    function pairwise(groups, test, delta, share) {
      const l = L(), pr = [];
      for (let i = 0; i < groups.length; i++) for (let j = i + 1; j < groups.length; j++) pr.push({ A: groups[i], B: groups[j], p: test(groups[i], groups[j]), d: delta(groups[i], groups[j]) });
      const adjp = holm(pr.map(x => x.p)); pr.forEach((x, i) => x.h = adjp[i]);
      const sig = pr.filter(x => x.h < st.alpha), dv = x => share ? fn(x.d * 100, 1) + sent(" pts", " poin") : fn(x.d);
      const nm = x => `${esc(x.d >= 0 ? x.A.name : x.B.name)} > ${esc(x.d >= 0 ? x.B.name : x.A.name)}`;
      const tbl = `<h4 style="margin:16px 0 0;font-size:14px">${l.pairs}</h4><div class="st-tw"><table class="st-tbl"><thead><tr><th>${l.pair}</th><th>${l.diff}</th><th>${l.praw}</th><th>${l.pholm}</th><th>${l.decision}</th></tr></thead><tbody>${pr.map(x => `<tr><td>${esc(x.A.name)} − ${esc(x.B.name)}</td><td class="n">${dv(x)}</td><td class="n">${fp(x.p)}</td><td class="n${x.h < st.alpha ? " st-sig" : ""}">${fp(x.h)}</td><td${x.h < st.alpha ? ' class="st-rej"' : ""}>${x.h < st.alpha ? l.rejS : l.keepS}</td></tr>`).join("")}</tbody></table></div>`;
      const say = sig.length ? sent(`After correcting for ${pr.length} comparisons (Holm), ${sig.length === 1 ? "one pair differs" : sig.length + " pairs differ"} at α = ${fn(st.alpha, 2)}: ${sig.map(nm).join("; ")}.`, `Setelah koreksi untuk ${pr.length} perbandingan (Holm), ${sig.length} pasangan berbeda pada α = ${fn(st.alpha, 2)}: ${sig.map(nm).join("; ")}.`)
        : sent(`After correcting for ${pr.length} comparisons (Holm), no single pair differs clearly at α = ${fn(st.alpha, 2)}.`, `Setelah koreksi untuk ${pr.length} perbandingan (Holm), tidak ada pasangan yang jelas berbeda pada α = ${fn(st.alpha, 2)}.`);
      return { tbl, say, m: pr.length, csv: [["pair_a", "pair_b", "difference", "p", "holm_p"], ...pr.map(x => [x.A.name, x.B.name, x.d, x.p, x.h])] };
    }

    /* ---- relationship ---- */
    function relate() {
      const l = L(), xv = byKey[st.x], yv = byKey[st.y2]; if (!xv || !yv) return `<p class="st-note">${l.fewer}</p>`;
      const ybin = yv.type === "bin", tx = v => st.logx ? Math.log10(v) : v, ty = v => st.logy && !ybin ? Math.log10(v) : v;
      const rs = cfg.rows.filter(r => val(r, st.x) != null && val(r, st.y2) != null && (!st.logx || r[st.x] > 0) && (!st.logy || ybin || r[st.y2] > 0)), dropped = cfg.rows.length - rs.length;
      if (rs.length < 8) return `<p class="st-note">${l.fewer}</p>`;
      const pts = rs.map(r => ({ id: r[cfg.idKey || "id"], x: tx(+r[st.x]), y: ybin ? (r[st.y2] ? 1 : 0) : ty(+r[st.y2]) }));
      const xs = pts.map(p => p.x), ys = pts.map(p => p.y), xl = lab(xv), yl = lab(yv);
      const unit = st.logx ? sent("a tenfold increase in", "kenaikan sepuluh kali lipat pada") : sent("each 1-unit increase in", "setiap kenaikan 1 unit pada");
      if (!ybin) {
        const pr = pearson(xs, ys), sp = spearman(xs, ys), m = ols(xs.map(x => [1, x]), ys), pm = permCor(xs, ys, st.alt), pa = pick(adj(pr.p, pr.r), pm);
        const line = x => { const f = m.b[0] + m.b[1] * x, se = Math.sqrt(m.V[0][0] * m.s2 + 2 * x * m.V[0][1] * m.s2 + x * x * m.V[1][1] * m.s2), tc = tCrit(m.df); return { f, lo: f - tc * se, hi: f + tc * se }; };
        lastRes = [["n", "pearson_r", "r_ci_low", "r_ci_high", "pearson_p", "spearman_rho", "spearman_p", "slope", "slope_ci_low", "slope_ci_high", "intercept", "r_squared", "log_x", "log_y", "permutation_p", "reshuffles", "alternative"], [pr.n, pr.r, pr.lo, pr.hi, pr.p, sp.r, sp.p, m.b[1], m.lo[1], m.hi[1], m.b[0], m.r2, st.logx, st.logy, pm.p, pm.B, st.alt]];
        const dir = pr.r > 0 ? l.higher : l.lower, str = Math.abs(pr.r) < 0.1 ? sent("almost no", "hampir tidak ada") : Math.abs(pr.r) < 0.3 ? sent("a weak", "hubungan lemah") : Math.abs(pr.r) < 0.5 ? sent("a moderate", "hubungan sedang") : sent("a strong", "hubungan kuat");
        const paras = [sent(`Countries with higher <b>${esc(xl)}</b> tend to have ${dir} <b>${esc(yl)}</b>: ${str} relationship (Pearson r = ${fn(pr.r)}, 95% interval ${fn(pr.lo)} to ${fn(pr.hi)}).`,
            `Negara dengan <b>${esc(xl)}</b> lebih tinggi cenderung memiliki <b>${esc(yl)}</b> ${dir}: ${str} (r Pearson = ${fn(pr.r)}, interval 95% ${fn(pr.lo)} sampai ${fn(pr.hi)}).`),
          sent(`On the fitted line, ${unit} ${esc(xl)} goes with a change of ${fn(m.b[1])}${st.logy ? " (log units)" : ""} in ${esc(yl)} (95% interval ${fn(m.lo[1])} to ${fn(m.hi[1])}). ${evS(pa, "a real association", "hubungan nyata")} (${P(pa)}). The rank-based Spearman test, less sensitive to outliers, gives ρ = ${fn(sp.r)}, ${P(adj(sp.p, sp.r))}. ${xl} accounts for ${fn(m.r2 * 100, 0)}% of the variation in ${yl}.`,
            `Pada garis taksiran, ${unit} ${esc(xl)} sejalan dengan perubahan ${fn(m.b[1])}${st.logy ? " (unit log)" : ""} pada ${esc(yl)} (interval 95% ${fn(m.lo[1])} sampai ${fn(m.hi[1])}). ${evS(pa, "a real association", "hubungan nyata")} (${P(pa)}). Uji Spearman berbasis peringkat, yang kurang peka terhadap pencilan, memberi ρ = ${fn(sp.r)}, ${P(adj(sp.p, sp.r))}. ${xl} menjelaskan ${fn(m.r2 * 100, 0)}% variasi ${yl}.`), pmLine(pm, `the values of ${esc(yl)} across countries`, `nilai ${esc(yl)} antarnegara`)];
        return `<div class="st-chart">${scatter(pts, xl, yl, line, st.logx, st.logy)}</div>${plain("", paras, pr.n, dropped, methodBox(`<p class="st-note">Ordinary least squares with a 95% confidence band for the fitted mean; Pearson correlation with a Fisher-z interval; Spearman correlation on ranks.${st.logx ? " Explanatory measure on a log10 scale." : ""}</p>`), { h0: sent(`There is no linear association between ${esc(xl)} and ${esc(yl)} (ρ = 0).`, `Tidak ada hubungan linear antara ${esc(xl)} dan ${esc(yl)} (ρ = 0).`), h1: sent(`The correlation is ${({two:"not zero",greater:"positive",less:"negative"})[st.alt]} (ρ ${sym()} 0).`, `Korelasinya ${({two:"tidak nol",greater:"positif",less:"negatif"})[st.alt]} (ρ ${sym()} 0).`), test: tname("t-test of Pearson's r", "Uji t untuk r Pearson", 1), stat: `r = ${fn(pr.r)}, t(${pr.n - 2}) = ${fn(pr.r * Math.sqrt((pr.n - 2) / (1 - pr.r * pr.r)))}`, p: pa, extra: `Spearman ${P(adj(sp.p, sp.r))}; ${pmExtra(adj(pr.p, pr.r), pm)}` })}`;
      }
      const m = logit(xs.map(x => [1, x]), ys); if (!m) return `<p class="st-note">${l.fewer}</p>`;
      const pr = (x, b) => 1 / (1 + Math.exp(-(b[0] + b[1] * x)));
      const line = x => { const eta = m.b[0] + m.b[1] * x, se = Math.sqrt(m.V[0][0] + 2 * x * m.V[0][1] + x * x * m.V[1][1]), s = v => 1 / (1 + Math.exp(-v)); return { f: s(eta), lo: s(eta - Z95 * se), hi: s(eta + Z95 * se) }; };
      const or = Math.exp(m.b[1]), olo = Math.exp(m.lo[1]), ohi = Math.exp(m.hi[1]), q1 = quantile(xs, 0.25), q3 = quantile(xs, 0.75), pm = permCor(xs, ys, st.alt), pa = pick(adj(m.p[1], m.b[1]), pm);
      const phr = esc((lang() === "id" && yv.phrase_id) || yv.phrase1 || sent("is “" + (yv.yes || yl) + "”", "termasuk “" + (yv.yes_id || yl) + "”"));
      lastRes = [["n", "odds_ratio_per_unit", "or_ci_low", "or_ci_high", "p", "prob_at_q1", "prob_at_q3", "mcfadden_r2", "log_x", "permutation_p", "reshuffles", "alternative"], [m.n, or, olo, ohi, m.p[1], pr(q1, m.b), pr(q3, m.b), m.r2, st.logx, pm.p, pm.B, st.alt]];
      const paras = [sent(`The chance that a country ${phr} ${or > 1 ? "rises" : "falls"} with <b>${esc(xl)}</b>: ${unit} it multiplies the odds by ${fn(or)} (95% interval ${fn(olo)} to ${fn(ohi)}).`,
          `Peluang suatu negara ${phr} ${or > 1 ? "naik" : "turun"} seiring <b>${esc(xl)}</b>: ${unit} itu mengalikan odds dengan ${fn(or)} (interval 95% ${fn(olo)} sampai ${fn(ohi)}).`),
        sent(`A country at the lower quartile of ${esc(xl)} has an estimated ${pct(pr(q1, m.b))} chance; one at the upper quartile, ${pct(pr(q3, m.b))}. ${evS(pa, "a real association", "hubungan nyata")} (${tname("logistic regression", "regresi logistik")}, ${P(pa)}).`,
          `Negara pada kuartil bawah ${esc(xl)} diperkirakan berpeluang ${pct(pr(q1, m.b))}; pada kuartil atas, ${pct(pr(q3, m.b))}. ${evS(pa, "a real association", "hubungan nyata")} (${tname("logistic regression", "regresi logistik")}, ${P(pa)}).`), pmLine(pm, "the outcome across countries", "hasil antarnegara")];
      return `<div class="st-chart">${scatter(pts, xl, yl, line, st.logx, false, true)}</div>${plain("", paras, m.n, dropped, (m.sep ? `<p class="st-note">${l.sepw}</p>` : "") + methodBox(`<p class="st-note">Logistic regression fitted by Newton-Raphson; Wald intervals; McFadden pseudo-R² = ${fn(m.r2)}.</p>`), { h0: sent(`${esc(xl)} makes no difference to the odds (β = 0, odds ratio = 1).`, `${esc(xl)} tidak memengaruhi odds (β = 0, rasio odds = 1).`), h1: sent(`The odds ratio is ${({two:"not 1",greater:"above 1",less:"below 1"})[st.alt]} (β ${sym()} 0).`, `Rasio odds ${({two:"tidak sama dengan 1",greater:"di atas 1",less:"di bawah 1"})[st.alt]} (β ${sym()} 0).`), test: tname("Wald test, logistic regression", "Uji Wald, regresi logistik", 1), stat: `z = ${fn(m.z[1])}`, p: pa, extra: pmExtra(adj(m.p[1], m.b[1]), pm) })}`;
    }

    /* ---- regression ---- */
    function regress() {
      const l = L(), yv = byKey[st.ry], preds = [...new Set(st.preds)].filter(k => byKey[k] && k !== st.ry);
      if (!yv || !preds.length) return `<p class="st-note">${l.fewer}</p>`;
      const ybin = yv.type === "bin";
      const rs = cfg.rows.filter(r => val(r, st.ry) != null && preds.every(k => val(r, k) != null && (!byKey[k].log || r[k] > 0))), dropped = cfg.rows.length - rs.length;
      // design matrix: numeric (log if flagged), binary 0/1, categorical as dummies against the largest group
      const cols = [];
      preds.forEach(k => {
        const v = byKey[k];
        if (v.type === "cat") {
          const cnt = {}; rs.forEach(r => cnt[r[k]] = (cnt[r[k]] || 0) + 1);
          const levels = Object.keys(cnt).sort((a, b) => cnt[b] - cnt[a]), ref = levels[0];
          levels.slice(1).forEach(lv => { if (cnt[lv] >= 2) cols.push({ name: `${groupName(v, lv)} (${l.ref} ${groupName(v, ref)})`, f: r => +(r[k] === lv), bin: true }); });
        } else if (v.type === "bin") cols.push({ name: lab(v), f: r => r[k] ? 1 : 0, bin: true });
        else cols.push({ name: lab(v) + (v.log ? " (log10)" : ""), f: r => v.log ? Math.log10(+r[k]) : +r[k], bin: false });
      });
      if (rs.length < cols.length + 10) return `<p class="st-note">${l.fewer}</p>`;
      const X = rs.map(r => [1, ...cols.map(c => c.f(r))]), y = rs.map(r => ybin ? (r[st.ry] ? 1 : 0) : +r[st.ry]);
      const m = ybin ? logit(X, y) : ols(X, y); if (!m) return `<p class="st-note">${sent("These factors overlap completely; remove one.", "Faktor-faktor ini tumpang tindih sepenuhnya; hapus salah satu.")}</p>`;
      const sds = cols.map((c, j) => c.bin ? 1 : sd(X.map(r => r[j + 1])));
      const rows = cols.map((c, j) => ({ name: c.name, est: m.b[j + 1], lo: m.lo[j + 1], hi: m.hi[j + 1], p: m.p[j + 1], s: sds[j] }));
      const frows = rows.map(r => ybin ? { name: r.name, est: r.est * r.s, lo: r.lo * r.s, hi: r.hi * r.s, p: r.p } : { name: r.name, est: r.est * r.s, lo: r.lo * r.s, hi: r.hi * r.s, p: r.p });
      lastRes = [["term", ybin ? "log_odds" : "coefficient", "ci_low", "ci_high", "p", ybin ? "odds_ratio" : "", "standardized"], ["(intercept)", m.b[0], m.lo[0], m.hi[0], m.p[0], "", ""], ...rows.map((r, j) => [r.name, r.est, r.lo, r.hi, r.p, ybin ? Math.exp(r.est) : "", frows[j].est]), [], ["n", m.n, ybin ? "mcfadden_r2" : "r_squared", m.r2, ybin ? "" : "adj_r_squared", ybin ? "" : m.adj]];
      const tbl = `<div class="st-tw"><table class="st-tbl"><thead><tr><th>${l.term}</th><th>${ybin ? l.or_ : l.coef}</th><th>${l.ci}</th><th>${l.pval}</th><th>H₀: β = 0</th></tr></thead><tbody>${rows.map(r => `<tr><td>${esc(r.name)}</td><td class="n${r.p < st.alpha ? " st-sig" : ""}">${fn(ybin ? Math.exp(r.est) : r.est)}</td><td class="n">${fn(ybin ? Math.exp(r.lo) : r.lo)} – ${fn(ybin ? Math.exp(r.hi) : r.hi)}</td><td class="n">${fp(r.p)}</td><td${r.p < st.alpha ? ' class="st-rej"' : ""}>${r.p < st.alpha ? l.rejS : l.keepS}</td></tr>`).join("")}</tbody></table></div>`;
      const sig = rows.filter(r => r.p < st.alpha), ns = rows.filter(r => r.p >= st.alpha);
      const lr = ybin ? 2 * (m.ll - m.ll0) : 0, pOver = ybin ? pChi(lr, m.k - 1) : m.pF;
      const hyp = { h0: sent(`None of the factors is associated with ${esc(lab(yv))} (all β = 0).`, `Tidak ada faktor yang berhubungan dengan ${esc(lab(yv))} (semua β = 0).`), h1: sent("At least one factor is (some β ≠ 0).", "Setidaknya satu faktor berhubungan (ada β ≠ 0)."), test: ybin ? sent("Likelihood-ratio test", "Uji rasio kemungkinan") : sent("F-test of the whole model", "Uji F model keseluruhan"), stat: ybin ? `χ²(${m.k - 1}) = ${fn(lr)}` : `F(${m.k - 1}, ${m.df}) = ${fn(m.F)}`, p: pOver, note: l.perfac };
      const say = r => ybin ? sent(`<b>${esc(r.name)}</b> ${r.est > 0 ? "raises" : "lowers"} the odds (×${fn(Math.exp(r.est))}, ${P(r.p)})`, `<b>${esc(r.name)}</b> ${r.est > 0 ? "menaikkan" : "menurunkan"} odds (×${fn(Math.exp(r.est))}, ${P(r.p)})`)
        : sent(`<b>${esc(r.name)}</b> goes with ${r.est > 0 ? "higher" : "lower"} ${esc(lab(yv))} (${fn(r.est)} per unit, ${P(r.p)})`, `<b>${esc(r.name)}</b> sejalan dengan ${esc(lab(yv))} ${r.est > 0 ? "lebih tinggi" : "lebih rendah"} (${fn(r.est)} per unit, ${P(r.p)})`);
      const paras = [
        sig.length ? sent(`Holding the other factors constant, ${sig.map(say).join("; ")}.`, `Dengan faktor lain dianggap tetap, ${sig.map(say).join("; ")}.`) : sent("Once the factors are considered together, none has a clear independent association with the outcome (all p ≥ " + fn(st.alpha, 2) + ").", "Setelah faktor-faktor dipertimbangkan bersama, tidak ada yang memiliki hubungan mandiri yang jelas dengan hasil (semua p ≥ " + fn(st.alpha, 2) + ")."),
        ns.length && sig.length ? sent(`No clear independent association for ${ns.map(r => esc(r.name)).join(", ")}.`, `Tidak ada hubungan mandiri yang jelas untuk ${ns.map(r => esc(r.name)).join(", ")}.`) : "",
        ybin ? sent(`Model fit: McFadden pseudo-R² = ${fn(m.r2)}.`, `Kecocokan model: pseudo-R² McFadden = ${fn(m.r2)}.`) : sent(`Together the factors account for ${fn(m.r2 * 100, 0)}% of the variation in ${esc(lab(yv))} (adjusted ${fn(m.adj * 100, 0)}%; F-test ${P(m.pF)}).`, `Bersama-sama faktor-faktor ini menjelaskan ${fn(m.r2 * 100, 0)}% variasi ${esc(lab(yv))} (disesuaikan ${fn(m.adj * 100, 0)}%; uji F ${P(m.pF)}).`)
      ].filter(Boolean);
      return `<div class="st-chart">${forest(frows)}<p class="st-note">${l.std}${ybin ? sent(", on the log-odds scale", ", pada skala log-odds") : ""}.</p>${tbl}</div>${plain("", paras, m.n, dropped, (ybin && m.sep ? `<p class="st-note">${l.sepw}</p>` : "") + methodBox(`<p class="st-note">${ybin ? "Logistic regression (Newton-Raphson), Wald 95% intervals; the table shows odds ratios." : "Ordinary least squares with classical standard errors; t-based 95% intervals."} Categorical factors enter as indicators against their largest group. Countries with missing values on any factor are left out.</p>`), hyp)}`;
    }

    /* ---- time to ratification ---- */
    function survival() {
      const l = L(), ev = SURV.events.find(e => e.key === st.ev) || SURV.events[0], evl = (lang() === "id" && ev.label_id) || ev.label;
      const gv = st.sg === "__all" ? null : byKey[st.sg];
      const rs = cfg.rows.filter(r => r["t_" + ev.key] != null && (!gv || val(r, st.sg) != null)), dropped = cfg.rows.length - rs.length;
      if (rs.length < 10) return `<p class="st-note">${l.fewer}</p>`;
      let groups = gv ? [...new Set(rs.map(r => r[st.sg]))].map(k => ({ key: k, name: groupName(gv, k), rows: rs.filter(r => r[st.sg] === k) })) : [{ key: "all", name: l.allc.replace(/ \(.*\)$/, ""), rows: rs }];
      const tooSmall = groups.some(g => g.rows.length < 3); groups = groups.filter(g => g.rows.length >= 3);
      if (!groups.length) return `<p class="st-note">${l.fewer}</p>`;
      if (gv && gv.type === "bin") groups.sort((a, b) => (b.key ? 1 : 0) - (a.key ? 1 : 0)); else if (gv && gv.order) groups.sort((a, b) => gv.order.indexOf(a.key) - gv.order.indexOf(b.key));
      groups.forEach(g => { g.t = g.rows.map(r => r["t_" + ev.key]); g.e = g.rows.map(r => r["e_" + ev.key] ? 1 : 0); g.km = km(g.t, g.e); g.med = kmMedian(g.km); g.r10 = 1 - kmAt(g.km, 10); g.r25 = 1 - kmAt(g.km, 25); g.k = sum(g.e); g.n = g.t.length; });
      const N = sum(groups.map(g => g.n)), maxT = Math.max(...groups.flatMap(g => g.t));
      const chart = kmChart(groups, maxT);
      const medS = g => g.med == null ? l.notr : fn(g.med, 1);
      const tbl = `<div class="st-tw"><table class="st-tbl"><thead><tr><th>${l.group_}</th><th>${l.nowr}</th><th>${l.by10}</th><th>${l.by25}</th><th>${l.med}</th></tr></thead><tbody>${groups.map(g => `<tr><td>${esc(g.name)}</td><td class="n">${g.k} / ${g.n}</td><td class="n">${pct(g.r10)}</td><td class="n">${pct(g.r25)}</td><td class="n">${medS(g)}</td></tr>`).join("")}</tbody></table></div>`;
      const yrs = v => sent(`${fn(v, 1)} years`, `${fn(v, 1)} tahun`);
      let paras = [], hyp = null, lr = null;
      const fast = [...groups].sort((a, b) => b.r10 - a.r10);
      if (groups.length === 1) {
        const g = groups[0];
        paras.push(sent(`Of ${g.n} countries, ${g.k} have ratified <b>${esc(evl)}</b>. An estimated ${pct(g.r10)} had ratified within 10 years of adoption and ${pct(g.r25)} within 25 years. ${g.med == null ? "Half of all countries have not yet ratified, so the median wait cannot be estimated." : `Half of all countries had ratified after ${yrs(g.med)}.`}`,
          `Dari ${g.n} negara, ${g.k} telah meratifikasi <b>${esc(evl)}</b>. Diperkirakan ${pct(g.r10)} meratifikasi dalam 10 tahun sejak diadopsi dan ${pct(g.r25)} dalam 25 tahun. ${g.med == null ? "Separuh negara belum meratifikasi, sehingga median waktu tunggu belum bisa diperkirakan." : `Separuh negara telah meratifikasi setelah ${yrs(g.med)}.`}`));
        lastRes = [["treaty", "group", "countries", "ratified", "share_by_10y", "share_by_25y", "median_years"], [ev.key, g.name, g.n, g.k, g.r10, g.r25, g.med == null ? "" : g.med]];
      } else {
        lr = logrank(groups.map(g => ({ t: g.t, e: g.e })));
        const f25 = [...groups].filter(g => Math.max(...g.t) >= 25).sort((a, b) => b.r25 - a.r25);
        paras.push(sent(`Within 10 years of adoption, <b>${esc(fast[0].name)}</b> had the highest share of ratifications (${pct(fast[0].r10)}) and <b>${esc(fast[fast.length - 1].name)}</b> the lowest (${pct(fast[fast.length - 1].r10)}).${f25.length > 1 ? ` Within 25 years, <b>${esc(f25[0].name)}</b> led (${pct(f25[0].r25)}) and <b>${esc(f25[f25.length - 1].name)}</b> trailed (${pct(f25[f25.length - 1].r25)}).` : ""}`,
          `Dalam 10 tahun sejak diadopsi, <b>${esc(fast[0].name)}</b> memiliki persentase ratifikasi tertinggi (${pct(fast[0].r10)}) dan <b>${esc(fast[fast.length - 1].name)}</b> terendah (${pct(fast[fast.length - 1].r10)}).${f25.length > 1 ? ` Dalam 25 tahun, <b>${esc(f25[0].name)}</b> memimpin (${pct(f25[0].r25)}) dan <b>${esc(f25[f25.length - 1].name)}</b> tertinggal (${pct(f25[f25.length - 1].r25)}).` : ""}`));
        if (lr) {
          paras.push(sent(`${evS(lr.p, "a difference in how fast the groups ratify", "perbedaan kecepatan ratifikasi antarkelompok")} (log-rank test, ${P(lr.p)}).`, `${evS(lr.p, "a difference in how fast the groups ratify", "perbedaan kecepatan ratifikasi antarkelompok")} (uji log-rank, ${P(lr.p)}).`));
          hyp = { h0: sent(`Countries in all ${groups.length} groups ratify ${esc(evl)} at the same pace (the curves are the same).`, `Negara di ke-${groups.length} kelompok meratifikasi ${esc(evl)} dengan kecepatan yang sama (kurvanya sama).`), h1: sent("At least one group ratifies faster or slower.", "Setidaknya satu kelompok meratifikasi lebih cepat atau lebih lambat."), test: sent("Log-rank test", "Uji log-rank"), stat: `χ²(${lr.df}) = ${fn(lr.X)}`, p: lr.p };
        }
        lastRes = [["treaty", "group", "countries", "ratified", "expected_if_equal", "share_by_10y", "share_by_25y", "median_years"], ...groups.map((g, i) => [ev.key, g.name, g.n, g.k, lr ? lr.E[i] : "", g.r10, g.r25, g.med == null ? "" : g.med]), [], ["logrank_chi2", "df", "p"], lr ? [lr.X, lr.df, lr.p] : []];
      }
      const meth = `<p class="st-note">Kaplan-Meier estimates of the share of countries that have ratified, by years since the treaty was adopted (${esc(String(ev.adopted))}). Countries that have not ratified are counted as "not yet" up to ${esc(SURV.asOf)}; ratifications by succession or before adoption count at year 0. Countries that became independent after adoption are counted from adoption, which makes them look slower. ${groups.length > 1 ? "Groups are compared with the log-rank test (χ², df = groups − 1)." : ""}</p>`;
      return `<div class="st-chart">${chart}${tbl}${tooSmall ? `<p class="st-note">${l.small}</p>` : ""}</div>${plain("", paras, N, dropped, methodBox(meth), hyp)}`;
    }
    function kmChart(groups, maxT) {
      const l = L(), lft = 52, r = 12, t = 10, b = 40, H = 320, cols = ["var(--st-fg)", "var(--st-acc)", "var(--st-blue)", "#7A6A2E", "#6C877A"], dash = ["", "", "", "6 3", "2 3"];
      const X = v => lft + v / maxT * (W - lft - r), Y = v => H - b - v * (H - t - b);
      let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(l.ratd)}">`;
      niceTicks(0, maxT, 6).forEach(v => { if (v > maxT) return; s += `<line x1="${X(v)}" x2="${X(v)}" y1="${t}" y2="${H - b}" stroke="var(--st-rule)"/><text x="${X(v)}" y="${H - b + 14}" text-anchor="middle">${fn(v, 0)}</text>`; });
      [0, 0.25, 0.5, 0.75, 1].forEach(v => { s += `<line x1="${lft}" x2="${W - r}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--st-rule)"/><text x="${lft - 6}" y="${Y(v) + 4}" text-anchor="end">${fn(v * 100, 0)}%</text>`; });
      groups.forEach((g, i) => {
        let pts = [], prev = 0; g.km.forEach(p => { pts.push(`${X(p.t)},${Y(prev)}`, `${X(p.t)},${Y(1 - p.s)}`); prev = 1 - p.s; }); pts.push(`${X(Math.max(...g.t))},${Y(prev)}`);
        s += `<polyline points="${pts.join(" ")}" fill="none" stroke="${cols[i % 5]}" stroke-width="2.5"${dash[i % 5] ? ` stroke-dasharray="${dash[i % 5]}"` : ""}><title>${esc(g.name)}</title></polyline>`;
      });
      s += `<text x="${(lft + W - r) / 2}" y="${H - 6}" text-anchor="middle">${esc(l.yrs)}</text><text transform="translate(12 ${(t + H - b) / 2}) rotate(-90)" text-anchor="middle">${esc(l.ratd)}</text></svg>`;
      if (groups.length > 1) s += `<div style="display:flex;flex-wrap:wrap;gap:6px 16px;font-size:13px;margin-top:6px">${groups.map((g, i) => `<span style="white-space:nowrap"><svg width="22" height="10" style="display:inline-block;width:22px;height:10px;vertical-align:middle"><line x1="0" x2="22" y1="5" y2="5" stroke="${cols[i % 5]}" stroke-width="3"${dash[i % 5] ? ` stroke-dasharray="${dash[i % 5]}"` : ""}/></svg> ${esc(g.name)} (${g.n})</span>`).join("")}</div>`;
      return s;
    }

    function download(which) {
      const cell = v => { const s = v == null ? "" : typeof v === "number" ? String(+v.toPrecision(10)) : String(v); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
      let rows;
      if (which === "data") { rows = [[cfg.idLabel || "country", ...V.map(v => v.key)], ...cfg.rows.map(r => [r[cfg.idKey || "id"], ...V.map(v => v.type === "bin" ? (r[v.key] == null ? "" : r[v.key] ? 1 : 0) : r[v.key])])]; rows.push([], ["variable", "label", "type", "source"], ...V.map(v => [v.key, v.label, v.type, v.src || ""])); }
      else rows = lastRes;
      const csv = "﻿" + rows.map(r => r.map(cell).join(",")).join("\r\n"), name = `${cfg.filename || "imr"}-${which === "data" ? "statistics-data" : "statistics-result"}.csv`;
      if (cfg.save) return cfg.save(name, csv);
      const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" })), a = document.createElement("a"); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 2000);
    }

    render();
    new MutationObserver(render).observe(document.documentElement, { attributes: true, attributeFilter: ["lang"] });
    return { render, state: st };
  }

  window.IMRStats = { mount, tests: { holm, km, logrank, permDiff, permGroups, permCor, permSign, welch, mannWhitney, anova, kruskal, chisq, fisher, pearson, spearman, ols, logit, oneSample, signedRank, wilson, pT, pF, pChi, tCrit } };
})();
