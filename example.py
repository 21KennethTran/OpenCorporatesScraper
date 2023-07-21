# NOT MINE; inspiration snippet taken from stack overflow
import httpx
import trio
from selectolax.lexbor import LexborHTMLParser
import re
import js2py
from pprint import pp

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
}


async def get_soup(content):
    return LexborHTMLParser(content)


async def get_company(channel):
    async with channel:
        async for client, url in channel:
            r = await client.get(url)
            soup = await get_soup(r.content)
            pp({
                'Name': soup.css_first('title').text(strip=True).split(':', 1)[0],
                'Address': soup.css_first('ul.address_lines').text(separator=', '),
                'Status': soup.css_first('dd.status').text(strip=True)
            })


async def main():
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, base_url='https://opencorporates.com') as client, trio.open_nursery() as nurse:
        params = {
            "action": "search_companies",
            "commit": "Go",
            "controller": "searches",
            "jurisdiction_code": "",
            "order": "",
            "q": "RI DUDDING LIMITED",
            "utf8": "✓"
        }
        r = await client.get('/companies', params=params)
        match = re.search('(function le.*\");', r.text,
                          re.DOTALL).group(1).replace('{ document.cookie=', 'return ') + "};go()"
        cookies = js2py.eval_js(match)
        client.cookies.update({
            'KEY': cookies.split('=', 1)[1]
        })
        r = await client.get(r.url)
        soup = await get_soup(r.content)
        comanies = soup.css('a.company_search_result')
        sender, receiver = trio.open_memory_channel(0)
        async with receiver:
            for _ in range(3):
                nurse.start_soon(get_company, receiver.clone())

            async with sender:
                for co in comanies:
                    await sender.send([client, co.attrs['href']])


if __name__ == "__main__":
    trio.run(main)