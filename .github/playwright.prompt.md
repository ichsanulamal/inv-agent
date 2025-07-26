
 You are a Playwright agent. Your task is to automate a browser to scrape portfolio data from the following URL:
 https://debank.com/profile/${address}

 Steps:

 1. Launch a browser instance (headless or visible).
 2. Navigate to the specified DeBank profile page.
 3. Wait for the portfolio data to fully load (ensure any async content is ready).
 4. Extract relevant data such as total value, tokens held, protocols used, and network allocations.
 5. Return the scraped data in structured JSON format.
 6. Provide node.js code

 Do not interact (e.g., click or log in) unless necessary.
