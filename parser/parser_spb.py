# https://eservice.gu.spb.ru/portalFront/resources/portal.html#medicament

import requests
from bs4 import BeautifulSoup


class DrugsParser:

    def __init__(self) -> None:
        self.page = page
        self.user = None
        self.site_url = URL

    async def send_request(self):
        link = await self.build_link()
        response = requests.get(link)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            available = soup.find_all()


class DrugsUser:

    def __init__(self) -> None:
        pass