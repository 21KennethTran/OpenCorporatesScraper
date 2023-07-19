from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import datetime
from pyppeteer import launch
import asyncio
import re
import js2py

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47',
          }

def get_soup(content):
  return BeautifulSoup(content, 'html.parser')

def extract(url):
  response = requests.get(url, headers=header)
  soup = get_soup(response.content)
  # TODO: how to parse this

def getCompanyInfo(company="Crixus Capital", type="companies"):
  company = company.replace(" ","+")
  url = f"https://opencorporates.com/{type}?q={company}&jurisdiction_code=&type={type}"
  
  with requests.get(url, headers=header) as r:
    # find function that generates cookie with regex (newline inclusive)
    match = re.search('(function le.*\");', r.text, re.DOTALL)

    # print(match.group(0))
    # print(match.group(0).replace('{ document.cookie=', 'return ') +"}; go()")

    # run the new js function to return cookie id
    cookie = js2py.eval_js(match.group(0).replace('{ document.cookie=', 'return ') +"}; go()")
    cookies = {'KEY': cookie.split('=', 1)[1]}

    new_r = requests.get(r.url, headers=header, cookies=cookies)
    soup = get_soup(new_r.content)
    
    company = soup.find_all('a', class_=['company_search_result inactive deregistered', 'company_search_result'])[0]['href']
    # print(company)
    extract('https://opencorporates.com' + company)


# async def company(company="Crixus Capital", type="companies"):
#   browser = await launch()
#   page = await browser.newPage()
#   await page.goto(f"https://opencorporates.com/{type}?q={company}&jurisdiction_code=&type={type}")
#   await page.waitForSelector('title', {'visible': True})
#   await page.screenshot({'path': 'ss2.png'})
#   await browser.close()
#   element = await page.querySelector('h1')


getCompanyInfo()
# asyncio.get_event_loop().run_until_complete(company())