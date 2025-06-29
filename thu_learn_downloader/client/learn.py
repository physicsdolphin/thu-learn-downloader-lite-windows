import functools
import re
from collections.abc import Sequence

from bs4 import BeautifulSoup, Tag
from playwright.sync_api import sync_playwright
from requests import Response
from requests.cookies import RequestsCookieJar

from thu_learn_downloader.common.typing import cast
from . import url
from .client import Client, Language
from .semester import Semester


class Learn:
    client: Client

    def __init__(self, language: Language = Language.ENGLISH, *args, **kwargs) -> None:
        self.client = Client(language, *args, **kwargs)

    def login(self, username: str, password: str) -> None:
        response: Response = self.client.get(url=url.make_url(), verify=False)
        soup: BeautifulSoup = BeautifulSoup(
            markup=response.text, features="html.parser"
        )
        login_button: Tag = cast(Tag, soup.select_one(selector="#loginButtonId"))
        onclick: str = cast(str, login_button["onclick"])
        login_url: str = cast(str, re.search(r"'(https?://[^']+)'", onclick).group(1))

        jar = RequestsCookieJar()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto(login_url)
            page.fill("#i_user", username)
            page.fill("#i_pass", password)
            page.evaluate("doLogin()")

            page.wait_for_url(re.compile(r"learn\.tsinghua\.edu\.cn/.*"), timeout=300_000)

            cookies = context.cookies()
            for cookie in cookies:
                jar.set(
                    name=cookie['name'],
                    value=cookie['value'],
                    domain=cookie.get('domain'),
                    path=cookie.get('path', '/'),
                )

            browser.close()

        self.client.cookies.update(jar)

    @functools.cached_property
    # def semesters(self) -> Sequence[Semester]:
    #     return [
    #         Semester(client=self.client, id=result)
    #         for result in self.client.get_with_token(
    #             url=url.make_url(path="/b/wlxt/kc/v_wlkc_xs_xktjb_coassb/queryxnxq")
    #         ).json()
    #     ]
    def semesters(self) -> Sequence[Semester]:
        response = self.client.get_with_token(
            url=url.make_url(path="/b/wlxt/kc/v_wlkc_xs_xktjb_coassb/queryxnxq")
        )

        if response.status_code != 200:
            print("Request failed with status:", response.status_code)
            return []

        try:
            data = response.json()
            print("Parsed JSON:", data)  # Debugging output

            # Filter out None values
            filtered_data = [item for item in data if item is not None]
        except Exception as e:
            print("JSON decoding error:", e)
            return []

        return [Semester(client=self.client, id=result) for result in filtered_data]

