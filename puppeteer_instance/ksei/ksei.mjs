// fetch-ksei.mjs
import fetch from 'node-fetch';
import { writeFile } from 'fs/promises';
import { mkdir } from 'fs/promises';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config();

const BASE_URL = 'https://akses.ksei.co.id/service/myportofolio/summary-detail';
const DATE = process.env.DATE || new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
const AUTH_TOKEN = process.env.AUTH_TOKEN;
const PORTFOLIO_DATA_PATH = process.env.PORTFOLIO_DATA_PATH || './data';

if (!AUTH_TOKEN) {
  console.error('❌ AUTH_TOKEN is not defined in environment variables.');
  process.exit(1);
}

const HEADERS = () => ({
  "accept": "*/*",
  "accept-language": "en-US,en-GB;q=0.9,en;q=0.8,id;q=0.7,eo;q=0.6",
  "authorization": AUTH_TOKEN,
  "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
  "sec-ch-ua-mobile": "?0",
  "sec-ch-ua-platform": "\"Linux\"",
  "sec-fetch-dest": "empty",
  "sec-fetch-mode": "cors",
  "sec-fetch-site": "same-origin",
  "Referer": "https://akses.ksei.co.id/myportofolio/saldo"
});

const PORTFOLIO_TYPES = [
  'ekuitas',
  'reksadana',
  'obligasi',
  'kas',
  'lainnya'
];

async function fetchPortfolio(type) {
  const url = `${BASE_URL}/${type}?tanggal=${DATE}`;
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: HEADERS(),
      credentials: 'include',
      mode: 'cors'
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status} (${response.statusText})`);
    }

    const data = await response.json();
    const filename = path.join(PORTFOLIO_DATA_PATH, `${type}.json`);
    await mkdir(PORTFOLIO_DATA_PATH, { recursive: true });
    await writeFile(filename, JSON.stringify(data, null, 2));
    console.log(`✅ [${type}] saved to ${filename}`);
  } catch (err) {
    console.error(`❌ [${type}] fetch failed: ${err.message}`);
  }
}

async function main() {
  await Promise.all(PORTFOLIO_TYPES.map(fetchPortfolio));
}

main();
