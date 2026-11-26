const puppeteer = require('/tmp/node_modules/puppeteer-core');
const fs = require('fs');
const OUT = '/tmp/shots';
const sleep = ms => new Promise(r => setTimeout(r, ms));

const VIEWS = [
  ['Dashboard', 'dashboard'],
  ['Audit Projects', 'audit-projects'],
  ['Findings & CAPA', 'findings'],
  ['Annex A & SoA', 'soa'],
  ['Risk & Frameworks', 'risks'],
  ['Evidence Vault', 'evidence'],
  ['Reports', 'reports'],
  ['User Management', 'users'],
  ['Settings & Logs', 'settings'],
];

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/tmp/chromium', headless: 'shell',
    args: [...require('/tmp/node_modules/@sparticuz/chromium').args],
    env: { ...process.env, LD_LIBRARY_PATH: '/tmp/chr/lib' },
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });
  const log = [];
  page.on('pageerror', e => log.push('pageerror: ' + e.message));

  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle2' });
  await sleep(1500);
  await page.screenshot({ path: `${OUT}/00-landing.png` });

  await page.evaluate(() => { const b=[...document.querySelectorAll('button')].find(x=>/sign in|log in/i.test(x.textContent)); if(b)b.click(); });
  await sleep(1200);
  await page.screenshot({ path: `${OUT}/01-login.png` });
  await page.type('#login-username', 'admin', {delay: 15});
  await page.type('#login-password', 'Admin@27001!', {delay: 15});
  await page.click('button[type=submit]');
  await sleep(4500);

  const nav = async (label) => {
    const ok = await page.evaluate(l => {
      const btn = [...document.querySelectorAll('nav button')].find(b => b.textContent.trim() === l);
      if (btn) { btn.click(); return true; }
      return false;
    }, label);
    await sleep(3000);
    return ok;
  };

  for (const [label, name] of VIEWS) {
    const ok = await nav(label);
    await page.screenshot({ path: `${OUT}/10-${name}.png` });
    log.push(`${label}: ${ok}`);
  }

  // audit detail: open the first audit row
  await nav('Audit Projects');
  const opened = await page.evaluate(() => {
    const row = [...document.querySelectorAll('tr, [role=button], button')]
      .find(e => /AUD-2026-001/.test(e.textContent));
    if (row) { row.click(); return true; }
    return false;
  });
  await sleep(3500);
  await page.screenshot({ path: `${OUT}/11-audit-detail.png` });
  log.push(`audit detail: ${opened}`);

  fs.writeFileSync(`${OUT}/log.txt`, log.join('\n'));
  await browser.close();
})().catch(e => { fs.writeFileSync(`${OUT}/log.txt`, 'FATAL ' + e.stack); process.exit(1); });
