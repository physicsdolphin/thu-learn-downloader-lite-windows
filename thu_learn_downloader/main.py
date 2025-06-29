import os
# Determine the path for openssl.conf based on whether it's running from the executable or source code
config_path = os.path.join(os.path.dirname(__file__), 'openssl.conf')

# Now you can use config_path to load the openssl.conf file
print(f"Config file path: {config_path}")
os.environ['OPENSSL_CONF'] = config_path
# this patch only works when directly run the project as module
# for using pyinstaller-built release exe, refer to hook.py

import urllib3
urllib3.disable_warnings()

import logging
from pathlib import Path
from typing import Annotated

import typer
from typer import Option, Typer

from thu_learn_downloader.client.client import Language
from thu_learn_downloader.client.learn import Learn
from thu_learn_downloader.common.logging import LogLevel
from thu_learn_downloader.download.downloader import Downloader
from thu_learn_downloader.download.selector import Selector
from thu_learn_downloader.login import auto as login

app: Typer = Typer(name="tld")

@app.command()
def main(
    username: Annotated[str, Option("-u", "--username")] = "",
    password: Annotated[str, Option("-p", "--password")] = "",
    *,
    prefix: Annotated[Path, Option(file_okay=False, writable=True)] = Path.home()  # noqa: B008
    / "thu-learn",
    semesters: Annotated[list[str], Option("-s", "--semester")] = [],
    courses: Annotated[list[str], Option("-c", "--course")] = [],  # noqa: B006
    document: Annotated[bool, Option()] = True,
    homework: Annotated[bool, Option()] = True,
    jobs: Annotated[int, Option("-j", "--jobs")] = 8,
    language: Annotated[Language, Option("-l", "--language")] = Language.ENGLISH,
    log_level: Annotated[LogLevel, Option(envvar="LOG_LEVEL")] = LogLevel.INFO,
) -> None:
    logging.getLogger().setLevel(log_level)

    username = username or login.username() or typer.prompt(text="Username")
    password = (
            password or login.password() or typer.prompt(text="Password", hide_input=True)
    )
    if not semesters:
        input_sem = typer.prompt(text="Semester (comma-separated)")
        semesters = [s.strip() for s in input_sem.split(",")]
    learn: Learn = Learn(language=language)
    learn.login(username=username, password=password)
    with Downloader(
        prefix=prefix,
        selector=Selector(
            semesters=semesters,
            courses=courses,
            document=document,
            homework=homework,
        ),
        jobs=jobs,
    ) as downloader:
        downloader.sync_semesters(semesters=learn.semesters)


if __name__ == "__main__":
    app()
