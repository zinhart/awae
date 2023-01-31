const puppeteer = require('puppeteer');
const arg = process.argv.slice(2);
const url = String(arg[0]);
const cookie = {
  'name': String(arg[1]),
  'value': String(arg[2]),
  'domain': 'answers',
};
(async () => {
  // Puppeteer stuff 
  const browser = await puppeteer.launch({ headless: false });        
  try {
	const page = await browser.newPage();
	await page.setCookie(cookie);
	// navigate to a page
	await page.goto(url)
 } finally {
  //console.log('Closing the browser...')
  //await browser.close();
 }
})();
