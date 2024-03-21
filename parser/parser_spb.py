# https://eservice.gu.spb.ru/portalFront/resources/portal.html#medicament
"""<div class="col-temp col-12-w540">
  <button type="submit" 
  class="button-reset _block-w540 button-base _size-common 
  button_theme-brand_fill common-popup-confirm-button text-button">
  Продолжить без авторизации
  </button>
</div>"""
# Нажать на кнопку перед поиском?

from os import getenv

import requests
from bs4 import BeautifulSoup

from dataclasses import dataclass

URL = getenv('URL')

class DrugsParser:

    def __init__(self) -> None:
        self.page = requests.get(URL)
        self.user = None

    def set_user(self, user):
         self.user = user

    def has_number(tag):
        head_tag = 
        for child in head_tag.descendants:
            return None
         

    async def send_request(self):
        link = await self.build_link()
        response = requests.get(link)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            drug_form = soup.find_all(
                'span', class_="droppanel__head-title"
            )
            for drug in drug_form:
                dct = {}
                adress = soup.find_all(
                    'span', class_="droppanel__head-title paragraph-extra"
                )
                time = soup.find(

                )



    async def build_link(self):
        options: SearchOption = self.user.search_options
        self.options = options
        self.site_url = URL
        return (
            f'{self.site_url}?filter={options.drug_name}'
            f'&ost{}=True'  # True выбран, ost1 федеральная, ost2 региональная
        )


"""<div class="line-base result-line cols"> 
  <div class="col-7">Остаток по Региональной льготе</div> 
  <div class="col-5 text-right">19</div>
</div>       """    


@dataclass
class SearchOption:
    def __init__(
            self, drug_name: str,
            presentation: str,
            reduce_type: str,
        ):
        self.drug_name = drug_name
        self.presentation = presentation
        self.reduce_type = reduce_type

class DrugsUser:

    def __init__(
            self, drug_name: str,
            presentation: str,
            reduce_type: str,
        ) -> None:
        self.search_options = SearchOption