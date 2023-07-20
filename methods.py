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

def extract(url, session):
  response = requests.get(url, headers=header, cookies=session)
  soup = get_soup(response.content)
#   print(soup.prettify())

#   print(soup.find('dd', class_='registry_page').text)
#   bleh = soup.find('dd', class_='registry_page').find('a')['href']
#   print(bleh)


  filings = []
  for file in soup.find_all('a', class_='filing'):
    filing = file.text + ', ' + 'https://opencorporates.com' + file['href']
    filings.append(filing)
  
  latestevents = []
  for event in soup.find_all('div', class_='event-timeline-row'):
    latestevent = event.find('dd').find('a').text + ' on ' + event.find('dt').text
    latestevents.append(latestevent)

  data = {
    'Company Name': [soup.find('title').text.split(' :')[0]],
    'Company Number': [soup.find('dd', class_='company_number').text] if soup.find('dd', class_='company_number') else [''],
    'Status': [soup.find('dd', class_='status').text] if soup.find('dd', class_='status') else [''],
    'Incorporation Date': [soup.find('dd', class_='incorporation_date').text] if soup.find('dd', class_='incorporation_date') else [''],
    'Dissolution Date': [soup.find('dd', class_='dissolution date').text] if soup.find('dd', class_='dissolution data') else [''],
    'Company Type': [soup.find('dd', class_='company_type').text] if soup.find('dd', class_='company_type') else [''],
    'Jurisdiction': [soup.find('dd', class_='jurisdiction').text] if soup.find('dd', class_='jurisdiction') else [''],
    'Business Number': [soup.find('dd', class_='business_number').text.strip()] if soup.find('dd', class_='business_number') else [''],
    'Registry Page': [soup.find('dd', class_='registry_page').find('a')['href']] if soup.find('dd', class_='registry_page') and soup.find('dd', class_='registry_page').find('a') else [''],
    'Recent filings (data and link)': filings,
    'Source': [soup.find('span', class_='publisher').text] if soup.find('span', class_='publisher') else [''],
    'Latest Events (date and description)': latestevents,
  }
  return data

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
    data = extract('https://opencorporates.com' + company, cookies)
    dlength = max(len(values) for values in data.values())
    for key, values in data.items():
      # remove \n from text we want
      newval = []
      for value in values:
        val = re.sub(r'\n', '', value)
        newval.append(val)
      data[key] = newval + ['']*(dlength - len(values))

    # transposed dataframe more intuitive for reading single company info?
    # maybe json format is better
    dataframe = pd.DataFrame(data)
    print(dataframe)

    dataframe.to_csv('companies_data.csv', index=False)


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