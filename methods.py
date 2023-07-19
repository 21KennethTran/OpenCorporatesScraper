from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import datetime
from pyppeteer import launch
import asyncio

def getCompanyInfo(company="Crixus Capital", type="companies"):
  company = company.replace(" ","+")
#   url = f"https://opencorporates.com/{type}?q={company}&jurisdiction_code=&type={type}"
  url = 'https://httpbin.org/headers'
  header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Referer': 'https://google.com',
            'DNT': '1'}
  
  response = requests.get(url, headers=header)
  print(response.text)
  
  soup = BeautifulSoup(response.content, 'html.parser')
  print(soup.prettify())

async def company(company="Crixus Capital", type="companies"):
  browser = await launch()
  page = await browser.newPage()
  await page.goto(f"https://opencorporates.com/{type}?q={company}&jurisdiction_code=&type={type}")
  await page.waitForSelector('title', {'visible': True})
  await page.screenshot({'path': 'ss2.png'})
  await browser.close()

  element = await page.querySelector('h1')

getCompanyInfo()
# asyncio.get_event_loop().run_until_complete(company())