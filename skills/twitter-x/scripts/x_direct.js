#!/usr/bin/env node
/**
 * X/Twitter scraper using cookies (no proxy) — for when you have valid session cookies.
 * Usage:
 *   node x_direct.js profile <username>
 *   node x_direct.js tweet <tweet_id>
 *   node x_direct.js search <query>
 *   node x_direct.js test              # just loads x.com and reports status
 */

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');
const path = require('path');

puppeteer.use(StealthPlugin());

const SECRETS = '/home/openclaw/.secrets';
const COOKIES_PATH = path.join(SECRETS, 'x_browser_cookies.json');

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function launch() {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--window-size=1920,1080'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36');
  
  if (fs.existsSync(COOKIES_PATH)) {
    const cookies = JSON.parse(fs.readFileSync(COOKIES_PATH, 'utf8'));
    if (cookies.length) await page.setCookie(...cookies);
  }
  return { browser, page };
}

async function saveCookies(page) {
  const cookies = await page.cookies();
  fs.writeFileSync(COOKIES_PATH, JSON.stringify(cookies, null, 2));
}

async function test() {
  const { browser, page } = await launch();
  try {
    await page.goto('https://x.com/home', { waitUntil: 'networkidle2', timeout: 60000 });
    await sleep(3000);
    console.log('URL:', page.url());
    console.log('Title:', await page.title());
    const loggedIn = await page.evaluate(() => {
      return !!document.querySelector('[data-testid="primaryColumn"]');
    });
    console.log('Logged in:', loggedIn);
    await saveCookies(page);
  } finally {
    await browser.close();
  }
}

async function scrapeProfile(username) {
  const { browser, page } = await launch();
  try {
    await page.goto(`https://x.com/${username}`, { waitUntil: 'networkidle2', timeout: 60000 });
    await sleep(4000);
    const data = await page.evaluate(() => {
      const getText = (sel) => { const el = document.querySelector(sel); return el ? el.textContent.trim() : null; };
      const name = getText('[data-testid="UserName"] span');
      const bio = getText('[data-testid="UserDescription"]');
      const location = getText('[data-testid="UserLocation"]');
      const stats = {};
      document.querySelectorAll('a[href*="/followers"], a[href*="/following"]').forEach(link => {
        const text = link.textContent.trim();
        if (link.href.includes('/followers') && !link.href.includes('verified')) stats.followers = text;
        if (link.href.includes('/following')) stats.following = text;
      });
      const tweets = [];
      document.querySelectorAll('article[data-testid="tweet"]').forEach((el, i) => {
        if (i >= 10) return;
        const t = el.querySelector('[data-testid="tweetText"]');
        const time = el.querySelector('time');
        const metrics = el.querySelectorAll('[data-testid="app-text-transition-container"]');
        tweets.push({
          text: t ? t.textContent.trim() : '',
          time: time ? time.getAttribute('datetime') : null,
          metrics: Array.from(metrics).map(m => m.textContent.trim()),
        });
      });
      return { name, bio, location, stats, tweets };
    });
    console.log(JSON.stringify(data, null, 2));
    await saveCookies(page);
  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: '/tmp/x_debug.png' }).catch(()=>{});
    console.log('Debug screenshot: /tmp/x_debug.png');
  } finally {
    await browser.close();
  }
}

async function scrapeTweet(tweetId) {
  const { browser, page } = await launch();
  try {
    await page.goto(`https://x.com/i/status/${tweetId}`, { waitUntil: 'networkidle2', timeout: 60000 });
    await sleep(4000);
    const data = await page.evaluate(() => {
      const article = document.querySelector('article[data-testid="tweet"]');
      if (!article) return null;
      const text = article.querySelector('[data-testid="tweetText"]');
      const time = article.querySelector('time');
      const metrics = article.querySelectorAll('[data-testid="app-text-transition-container"]');
      const author = article.querySelector('[data-testid="User-Name"]');
      return {
        text: text ? text.textContent.trim() : '',
        time: time ? time.getAttribute('datetime') : null,
        author: author ? author.textContent.trim() : '',
        metrics: Array.from(metrics).map(m => m.textContent.trim()),
      };
    });
    console.log(JSON.stringify(data, null, 2));
    await saveCookies(page);
  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: '/tmp/x_debug.png' }).catch(()=>{});
  } finally {
    await browser.close();
  }
}

async function searchX(query) {
  const { browser, page } = await launch();
  try {
    await page.goto(`https://x.com/search?q=${encodeURIComponent(query)}&src=typed_query&f=live`, { waitUntil: 'networkidle2', timeout: 60000 });
    await sleep(5000);
    const tweets = await page.evaluate(() => {
      const results = [];
      document.querySelectorAll('article[data-testid="tweet"]').forEach((el, i) => {
        if (i >= 15) return;
        const text = el.querySelector('[data-testid="tweetText"]');
        const time = el.querySelector('time');
        const author = el.querySelector('[data-testid="User-Name"]');
        const metrics = el.querySelectorAll('[data-testid="app-text-transition-container"]');
        results.push({
          author: author ? author.textContent.trim() : '',
          text: text ? text.textContent.trim() : '',
          time: time ? time.getAttribute('datetime') : null,
          metrics: Array.from(metrics).map(m => m.textContent.trim()),
        });
      });
      return results;
    });
    console.log(JSON.stringify(tweets, null, 2));
    await saveCookies(page);
  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: '/tmp/x_debug.png' }).catch(()=>{});
  } finally {
    await browser.close();
  }
}

const [,, cmd, ...args] = process.argv;
switch (cmd) {
  case 'test': test(); break;
  case 'profile': scrapeProfile(args[0]); break;
  case 'tweet': scrapeTweet(args[0]); break;
  case 'search': searchX(args.join(' ')); break;
  default: console.log('Usage: x_direct.js <test|profile|tweet|search> [args]');
}
