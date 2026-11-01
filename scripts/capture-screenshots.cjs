const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function main() {
  const screenshotsDir = path.join(__dirname, '..', 'docs', 'screenshots');
  fs.mkdirSync(screenshotsDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
    colorScheme: 'dark'
  });

  const page = await context.newPage();

  // 1. Capture 01_hero_download.png
  console.log('Capturing 01_hero_download.png...');
  await page.goto('http://127.0.0.1:8000/', { waitUntil: 'domcontentloaded' });
  await page.fill('#url', 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4');
  
  // Populate simulated analysis result in the DOM
  await page.evaluate(() => {
    const res = document.querySelector('#result');
    res.className = 'result';
    res.replaceChildren();
    const text = document.createElement('p');
    text.textContent = 'commondatastorage.googleapis.com · video/mp4 · 158.0 MiB';
    const link = document.createElement('a');
    link.href = '#';
    link.textContent = 'Open direct media';
    res.append(text, link);
  });
  await page.waitForTimeout(600);

  const out1 = path.join(screenshotsDir, '01_hero_download.png');
  await page.screenshot({ path: out1 });
  console.log(`Saved: ${out1} (${fs.statSync(out1).size} bytes)`);

  // 2. Capture 02_media_converter.png
  console.log('Capturing 02_media_converter.png...');
  await page.locator('#convert').scrollIntoViewIfNeeded();
  await page.evaluate(() => {
    document.querySelector('#file-name').textContent = 'cinematic_recording_session.mov (142.5 MiB)';
    document.querySelector('#format').value = 'mp3';
    const status = document.querySelector('#convert-status');
    status.className = 'result';
    status.textContent = 'Done. Your converted file has been downloaded.';
  });
  await page.waitForTimeout(600);

  const out2 = path.join(screenshotsDir, '02_media_converter.png');
  await page.screenshot({ path: out2 });
  console.log(`Saved: ${out2} (${fs.statSync(out2).size} bytes)`);

  // 3. Capture 03_features_workflow.png
  console.log('Capturing 03_features_workflow.png...');
  await page.locator('#how').scrollIntoViewIfNeeded();
  await page.waitForTimeout(600);

  const out3 = path.join(screenshotsDir, '03_features_workflow.png');
  await page.screenshot({ path: out3 });
  console.log(`Saved: ${out3} (${fs.statSync(out3).size} bytes)`);

  // 4. Capture 04_security_privacy.png
  console.log('Capturing 04_security_privacy.png...');
  await page.locator('#privacy').scrollIntoViewIfNeeded();
  await page.waitForTimeout(600);

  const out4 = path.join(screenshotsDir, '04_security_privacy.png');
  await page.screenshot({ path: out4 });
  console.log(`Saved: ${out4} (${fs.statSync(out4).size} bytes)`);

  await browser.close();
  console.log('All 4 MediaFlow screenshots captured successfully.');
}

main().catch(err => {
  console.error('Capture failed:', err);
  process.exit(1);
});
