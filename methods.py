from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import datetime

def getCompanyInfo(company="Crixus Capital", type="companies"):
  company = company.replace(" ","+")
  url = f"https://opencorporates.com/{type}?q={company}&jurisdiction_code=&type={type}"
  
  header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47'}
  response = requests.get(url, headers=header)
  # print(response.text)
  
  soup = BeautifulSoup(response.content, 'html.parser')
  print(soup.prettify())
getCompanyInfo()