import os
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from fake_useragent import UserAgent

load_dotenv()
ua = UserAgent()

BASE_URL = 'https://akses.ksei.co.id/service/myportofolio/summary-detail'
DATE = os.getenv('DATE') or (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
PORTFOLIO_DATA_PATH = Path(os.getenv('PORTFOLIO_DATA_PATH', './data'))

if not AUTH_TOKEN:
    print('❌ AUTH_TOKEN is not defined in environment variables.')
    exit(1)

HEADERS = {
    "authorization": AUTH_TOKEN,
    "Referer": "https://akses.ksei.co.id/myportofolio/saldo",
    "User-Agent": ua.random,
    "Content-Type": "application/json"
    
}

PORTFOLIO_TYPES = ['ekuitas', 'reksadana', 'obligasi', 'kas', 'lainnya']

async def fetch_portfolio(session, type_):
    url = f"{BASE_URL}/{type_}?tanggal={DATE}"
    try:
        async with session.get(url, headers=HEADERS) as response:
            if not response.ok:
                raise Exception(f"HTTP {response.status} ({response.reason})")
            
            data = await response.json()
            filename = PORTFOLIO_DATA_PATH / f"{type_}.json"
            PORTFOLIO_DATA_PATH.mkdir(parents=True, exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ [{type_}] saved to {filename}")
    except Exception as e:
        print(f"❌ [{type_}] fetch failed: {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[fetch_portfolio(session, t) for t in PORTFOLIO_TYPES])

if __name__ == "__main__":
    asyncio.run(main())