const puppeteer = require('/tmp/node_modules/puppeteer-core');
const fs = require('fs');
const OUT = '/tmp/shots';
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/tmp/chromium', headless: 'shell',
    args: [...require('/tmp/node_modules/@sparticuz/chromium').args],
    env: { ...process.env, LD_LIBRARY_PATH: '/tmp/chr/lib' },
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 1350, deviceScaleFactor: 2 });
  const log = [];
  page.on('pageerror', e => log.push('pageerror: ' + e.message));

  await page.goto('http://127.0.0.1:5173/', { waitUntil: 'networkidle2' });
  await sleep(1500);
  await page.evaluate(() => { const b=[...document.querySelectorAll('button')].find(x=>/sign in|log in/i.test(x.textContent)); if(b)b.click(); });
  await sleep(1200);
  await page.type('#login-username', 'admin', {delay: 12});
  await page.type('#login-password', 'Admin@27001!', {delay: 12});
  await page.click('button[type=submit]');
  await sleep(4500);

  const nav = async l => {
    const ok = await page.evaluate(x => {
      const b=[...document.querySelectorAll('nav button')].find(b=>b.textContent.trim()===x);
      if(b){b.click();return true;} return false;
    }, l);
    await sleep(2800); return ok;
  };

  // open the completed ISO 27001 audit
  await nav('Audit Projects');
  const opened = await page.evaluate(() => {
    const card = [...document.querySelectorAll('div,article,button')]
      .filter(e => /ISO 27001 Annual Security Audit/.test(e.textContent) && e.children.length < 12)
      .pop();
    if (card) { card.click(); return true; }
    return false;
  });
  await sleep(3500);
  await page.screenshot({ path: `${OUT}/11-audit-detail.png` });
  log.push('audit detail: ' + opened);

  // checklist tab (control tests workpapers)
  const tab = await page.evaluate(() => {
    const t=[...document.querySelectorAll('button')].find(b=>/^Checklist/.test(b.textContent.trim()));
    if(t){t.click();return true;} return false;
  });
  await sleep(2500);
  await page.screenshot({ path: `${OUT}/12-audit-checklist.png` });
  log.push('checklist: ' + tab);

  await nav('Settings & Logs');
  await page.screenshot({ path: `${OUT}/13-settings.png` });
  await nav('User Management');
  await page.screenshot({ path: `${OUT}/14-users.png` });
  await nav('Dashboard');

  fs.writeFileSync(`${OUT}/log3.txt`, log.join('\n'));
  await browser.close();
})().catch(e => { fs.writeFileSync(`${OUT}/log3.txt`, 'FATAL ' + e.stack); process.exit(1); });
