from os import getenv
from pathlib import Path

import requests

import scrapy
from scrapy.http import Response, HtmlResponse
from scrapy.selector import Selector

from dataclasses import dataclass

from selenium import webdriver


class DrugsSpider(scrapy.Spider):
    name = 'drugs'

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.url = getenv('URL')

    def set_user(self, user):
        self.user = user

    def start_requests(self):

        yield scrapy.Request(url=self.url, callback=self.parse)

    async def build_url(self) -> str:
        options: SearchOption = self.user.search_options
        self.options = options

        return (
            f"{self.url}?",
            f"filter={options.drug_name}",
            f"&ost{options.type_of_privilege}=true"
        )

    async def click_auth_button(self, response):
        link = await self.build_url()
        response = requests.get(link)

        if response.status_code == 200:
            # Кликнуть кнопку «Продолжить без авторизации», чтобы получить ответ страницы
            self.driver.get(response.url)
            auth_button = self.driver.find_element_by_xpath(
                '//*[@id="common-popup"]/div/div[1]/div/div[3]/div/div[1]/button'
            ).get()

            if auth_button is not None:
                auth_button.click()

    async def get_drug_forms(self, response):
        response = HtmlResponse(url=self.build_url(), body=body, encoding="utf-8")

        drug_forms = Selector(response=response).xpath(
            "//*[@id="medicament-search-result"]/div/div/button/span"
        ).getall()

        if drug_form is None:
            return 'Препарата нет в наличии.'
        else:
            # Вернуть список для выбора формы препарата
            return enumerate(drug_forms)

@dataclass
class SearchOption:
    """Параметры поиска для препаратов."""
    def __init__(
            self, drug_name: str,
            type_of_privilege: int,
            drug_form: int,
    ):
        self.drug_name = drug_name
        self.type_of_privilege = type_of_privilege
        self.drug_form = drug_form


class DrugsUser:
    """Пользователь бота."""

    def __init__(
            self, drug_name: str,
            type_of_privilege: int,
            drug_form: int,
    ) -> None:
        self.search_options = SearchOption(
            drug_name, type_of_privilege, drug_form
        )
