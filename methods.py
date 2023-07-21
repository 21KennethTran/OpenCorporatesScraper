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
import creds
import mechanicalsoup

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47',
          }


def get_soup(content):
  return BeautifulSoup(content, 'html.parser')



def extractcomp(url, session):
  response = requests.get(url, headers=header, cookies=session)
  soup = get_soup(response.content)

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
    'Dissolution Date': [soup.find('dd', class_='dissolution date').text] if soup.find('dd', class_='dissolution date') else [''],
    'Company Type': [soup.find('dd', class_='company_type').text] if soup.find('dd', class_='company_type') else [''],
    'Jurisdiction': [soup.find('dd', class_='jurisdiction').text] if soup.find('dd', class_='jurisdiction') else [''],
    'Business Number': [soup.find('dd', class_='business_number').text.strip()] if soup.find('dd', class_='business_number') else [''],
    'Registry Page': [soup.find('dd', class_='registry_page').find('a')['href']] if soup.find('dd', class_='registry_page') and soup.find('dd', class_='registry_page').find('a') else [''],
    'Recent filings (data and link)': filings,
    'Source': [soup.find('span', class_='publisher').text] if soup.find('span', class_='publisher') else [''],
    'Latest Events (date and description)': latestevents,
  }
  return data



def extractthem(url, browser):
  response = browser.open(url)
  soup = get_soup(response.content)

  #TODO: need to find name title and date, not name and link
  others = []
  if soup.find('small'):
    url2 = 'https://opencorporates.com' + soup.find('small').find('a')['href']

    while url2 is not None:
        resp = browser.open(url2)
        soup2 = get_soup(resp.content)
        for off in soup2.find('ul', id='officers').find_all('li'):
            name = off.find('a').text if off.find('a') else ''
            title = off.contents[1].strip().rstrip(',') if off.contents[1] else ''
            date = off.find('span', class_='start_date').text.strip() if off.find('span', class_='start_date') else ''
            other = name + title +  ', ' + date
            others.append(other)
        if soup2.find_all('a', rel='next nofollow') is None:
          break
        url2 = 'https://opencorporates.com' + soup2.find_all('a', rel='next nofollow')[-1]['href']
        print(url2)
  else:
    for off in soup.find('ul', class_='officers').find_all('li'):
        other = off.find('a').text + off.contents[1].strip().rstrip(',') +  ', ' + off.find('span', class_='start_date').text.strip()
        others.append(other)
    
  response = browser.open(url)
  # removed 'person's name' bc redundant
  data = {
    'Name': [soup.find('dd', class_='name').text] if soup.find('dd', class_='name') else [''],
    'Company name and link': [soup.find('dd', class_='company').find('a').text + ', https://opencorporates.com' + soup.find('dd', class_='company').find('a')['href']] if soup.find('dd', class_='company') and soup.find('dd', class_='company').find('a') else [''],
    'Address': [soup.find('dd', class_='address').text] if soup.find('dd', class_='address') else [''],
    'Position': [soup.find('dd', class_='position').text] if soup.find('dd', class_='position') else [''],
    'Start date': [soup.find('dd', class_='start_date').text] if soup.find('dd', class_='start_date') else [''],
    'Other officers in company (name, title, date)': others,
  }
  return data



def getCompanyInfo(company="Crixus Capital", type="companies"):
  company = company.replace(" ","+")
  url = f"https://opencorporates.com/{type}?q={company}&jurisdiction_code=&type={type}"
  
  with requests.get(url, headers=header) as r:
    # find function that generates cookie with regex (newline inclusive)
    match = re.search('(function le.*\");', r.text, re.DOTALL)

    # run the new js function to return cookie id
    cookie = js2py.eval_js(match.group(0).replace('{ document.cookie=', 'return ') +"}; go()")
    cookies = {'KEY': cookie.split('=', 1)[1]}

    new_r = requests.get(r.url, headers=header, cookies=cookies)
    soup = get_soup(new_r.content)
    
    company = soup.find_all('a', class_=['company_search_result inactive deregistered', 'company_search_result'])[0]['href']
    data = extractcomp('https://opencorporates.com' + company, cookies)
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



# attempt at asynchronous functions (wrong)
async def company(company="Crixus Capital", type="companies"):
  browser = await launch()
  page = await browser.newPage()
  await page.goto(f"https://opencorporates.com/{type}?q={company}&jurisdiction_code=&type={type}")
  await page.waitForSelector('title', {'visible': True})
  await page.screenshot({'path': 'ss2.png'})
  await browser.close()
  element = await page.querySelector('h1')



# wronge implementation
def login():
  login = 'https://opencorporates.com/users/sign_in'
  
  with requests.Session() as session:
    r = session.get(login, headers=header)
    # print(r.text)

    # find function that generates cookie with regex (newline inclusive)
    match = re.search('(function le.*\");', r.text, re.DOTALL)

    # run the new js function to return cookie id
    cookie = js2py.eval_js(match.group(0).replace('{ document.cookie=', 'return ') +"}; go()")
    cookies = cookie.split('=', 1)[1]

    session.cookies.set('KEY', cookies)

    new_r = session.get(r.url, headers=header)
    # print(new_r.text)

    # I am not sure how to get authenticity_token...
    form = {
    'utf8': '✓',
    'authenticity_token': 'vmmlsh1wYnByoD/Zp8CSsEN7VSi7iJDSkmqw4VHIzsI=',
    'user[email]': creds.un,
    'user[password]': creds.pw,
    'redirect_to': '',
    'submit': '',
  }
    login_r = session.post(new_r.url, data=form)
    print(login_r.text)



# stateful login is necessary as login POST payload requires authenticity_token which is generated in the backend
def login_stateful(browser):
  login_url = 'https://opencorporates.com/users/sign_in'

  jspage = browser.open(login_url).content.decode()
  # find function that generates cookie with regex (newline inclusive)
  match = re.search('(function le.*\");', jspage, re.DOTALL)

  # run the new js function to return cookie id
  cookie = js2py.eval_js(match.group(0).replace('{ document.cookie=', 'return ') +"}; go()")
  cookies = cookie.split('=', 1)[1]
  

  browser.session.cookies.set('KEY', cookies)
  browser.open(login_url)

  form = browser.select_form('form[id="new_user"]')

  browser['user[email]'] = creds.un
  browser['user[password]'] = creds.pw
  browser.submit_selected()
  


def getOfficerInfo(officer="Jack McKay"):
  browser = mechanicalsoup.StatefulBrowser()
  login_stateful(browser)

  officer = officer.replace(" ","+")
  url = f"https://opencorporates.com/officers?q={officer}&jurisdiction_code=&type=officers"

  response = browser.open(url)
  soup = get_soup(response.content)

  officer = soup.find_all('a', class_=['officer', 'officer inactive'])[0]['href']
  data = extractthem('https://opencorporates.com' + officer, browser)
  dlength = max(len(values) for values in data.values())
  for key, values in data.items():
    # remove \n from text we want
    newval = []
    for value in values:
      val = re.sub(r'\n', '', value)
    #   val = re.sub(r'\"', '', val)
      newval.append(val)
    data[key] = newval + ['']*(dlength - len(values))

  # transposed dataframe more intuitive for reading single company info?
  # maybe json format is better
  dataframe = pd.DataFrame(data)
  print(dataframe)
  dataframe.to_csv('officers_data.csv', index=False)
  
# getCompanyInfo()
getOfficerInfo('Jack A Mckay')