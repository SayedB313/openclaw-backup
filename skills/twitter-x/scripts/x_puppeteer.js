#!/usr/bin/env node
/**
 * X/Twitter Puppeteer Scraper - DEFINITIVE VERSION (OG)
 * 
 * Features:
 * - Stealth plugin to evade bot detection
 * - Residential Proxy (ProxyEmpire) with per-request session rotation
 * - Authenticated Cookie Support (including HttpOnly auth_token)
 * - Resilient Selectors for modern X layout
 * - Debug Screenshotting on failure
 * 
 * Usage:
 *   node x_puppeteer.js profile <username>
 *   node x_puppeteer.js tweet <tweet_id>
 *   node x_puppeteer.js search <query>
 */

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');
const path = require('path');

puppeteer.use(StealthPlugin());

const SECRETS = '/home/openclaw/.secrets';
const COOKIES_PATH = path.join(SECRETS, 'x_browser_cookies.json');
const PROXY_CREDS = JSON.parse(fs.readFileSync(path.join(SECRETS, 'proxy.json'), 'utf8'));

const PROXY_HOST = `${PROXY_CREDS.host}:${PROXY_CREDS.port}`;
const PROXY_BASE_USER = PROXY_CREDS.username.replace(/-sid-.*$/, '');

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function launch(sessionTag) {
  const sid = sessionTag || `s${Date.now()}`;
  const proxyUser = `${PROXY_BASE_USER}-sid-${sid}`;
  
  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      `--proxy-server=http://${PROXY_HOST}`,
      '--no-sandbox', '--disable-setuid-sandbox',
      '--disable-dev-shm-usage', '--disable-gpu',
      '--window-size=1920,1080',
    ],
  });
  const page = await browser.newPage();
  await page.authenticate({ username: proxyUser, password: PROXY_CREDS.password });
  await page.setViewport({ width: 1920, height: 1080 });
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36');
  
  if (fs.existsSync(COOKIES_PATH)) {
    try {
      const cookies = JSON.parse(fs.readFileSync(COOKIES_PATH, 'utf8'));
      if (cookies.length) await page.setCookie(...cookies);
    } catch(e) { console.error('Cookie load error:', e.message); }
  }
  
  return { browser, page };
}

async function saveCookies(page) {
  const cookies = await page.cookies();
  fs.writeFileSync(COOKIES_PATH, JSON.stringify(cookies, null, 2));
}

async function scrapeProfile(username) {
  const { browser, page } = await launch(`profile_${username}`);
  try {
    console.log(`Scraping @${username}...`);
    await page.goto(`https://x.com/${username}`, { waitUntil: 'networkidle2', timeout: 60000 });
    await sleep(5000);

    // Check if we are on a login redirect or error page
    const title = await page.title();
    if (title.includes('Log in') || title.includes('Something went wrong')) {
      console.error(`Blocked by X. Title: ${title}`);
      await page.screenshot({ path: '/tmp/x_blocked.png' });
      return null;
    }

    const data = await page.evaluate(() => {
      const getText = (sel) => {
        const el = document.querySelector(sel);
        return el ? el.textContent.trim() : null;
      };
      
      const name = getText('[data-testid="UserName"] span');
      const bio = getText('[data-testid="UserDescription"]');
      const location = getText('[data-testid="UserLocation"]');
      
      const tweets = [];
      document.querySelectorAll('article[data-testid="tweet"]').forEach((el, i) => {
        if (i >= 15) return;
        const textEl = el.querySelector('[data-testid="tweetText"]');
        const timeEl = el.querySelector('time');
        const authorEl = el.querySelector('[data-testid="User-Name"]');
        const metrics = Array.from(el.querySelectorAll('[data-testid="app-text-transition-container"]')).map(m => m.textContent.trim());
        
        tweets.push({
          author: authorEl ? authorEl.textContent.trim() : '',
          text: textEl ? textEl.textContent.trim() : '',
          time: timeEl ? timeEl.getAttribute('datetime') : null,
          metrics: metrics
        });
      });

      return { name, bio, location, tweets };
    });

    console.log(JSON.stringify(data, null, 2));
    await saveCookies(page);
  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: '/tmp/x_error.png' });
  } finally {
    await browser.close();
  }
}

async function scrapeTweet(tweetId) {
  const { browser, page } = await launch(`tweet_${tweetId}`);
  try {
    console.log(`Scraping tweet ${tweetId}...`);
    await page.goto(`https://x.com/i/status/${tweetId}`, { waitUntil: 'networkidle2', timeout: 60000 });
    await sleep(5000);

    const data = await page.evaluate(() => {
      const article = document.querySelector('article[data-testid="tweet"]');
      if (!article) return null;
      
      const textEl = article.querySelector('[data-testid="tweetText"]');
      const timeEl = article.querySelector('time');
      const authorEl = article.querySelector('[data-testid="User-Name"]');
      const metrics = Array.from(article.querySelectorAll('[data-testid="app-text-transition-container"]')).map(m => m.textContent.trim());
      
      return {
        author: authorEl ? authorEl.textContent.trim() : '',
        text: textEl ? textEl.textContent.trim() : '',
        time: timeEl ? timeEl.getAttribute('datetime') : null,
        metrics: metrics
      };
    });

    console.log(JSON.stringify(data, null, 2));
    await saveCookies(page);
  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: '/tmp/x_tweet_error.png' });
  } finally {
    await browser.close();
  }
}

async function searchX(query) {
  const { browser, page } = await launch(`search_${Date.now()}`);
  try {
    const encoded = encodeURIComponent(query);
    console.log(`Searching X for: ${query}`);
    await page.goto(`https://x.com/search?q=${encoded}&src=typed_query&f=live`, { waitUntil: 'networkidle2', timeout: 60000 });
    await sleep(5000);

    const tweets = await page.evaluate(() => {
      const results = [];
      document.querySelectorAll('article[data-testid="tweet"]').forEach((el, i) => {
        if (i >= 15) return;
        const textEl = el.querySelector('[data-testid="tweetText"]');
        const timeEl = el.querySelector('time');
        const authorEl = el.querySelector('[data-testid="User-Name"]');
        results.push({
          author: authorEl ? authorEl.textContent.trim() : '',
          text: textEl ? textEl.textContent.trim() : '',
          time: timeEl ? timeEl.getAttribute('datetime') : null
        });
      });
      return results;
    });

    console.log(JSON.stringify(tweets, null, 2));
    await saveCookies(page);
  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: '/tmp/x_search_error.png' });
  } finally {
    await browser.close();
  }
}

const [,, cmd, ...args] = process.argv;
switch (cmd) {
  case 'profile': scrapeProfile(args[0]); break;
  case 'tweet': scrapeTweet(args[0]); break;
  case 'search': searchX(args.join(' ')); break;
  default: console.log('Usage: node x_puppeteer.js <profile|tweet|search> [args]');
}
