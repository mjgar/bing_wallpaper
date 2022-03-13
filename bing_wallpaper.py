"""Bing wallpaper downloader."""
import argparse
import datetime
import hashlib
import logging
import pathlib
import re
import shutil

import bs4
import funcy
import requests

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] - %(levelname)s - %(message)s"
)

_BING_URL = "https://bing.com"
LOG = logging.getLogger()


@funcy.retry(tries=3, errors=requests.RequestException, timeout=lambda a: 2**a)
def download_wallpaper(
    destination_directory: pathlib.Path, archive_directory: pathlib.Path
) -> None:
    """Download today's Bing wallpaper to a directory as needed."""
    LOG.info(f"Connecting to {_BING_URL}")
    r = requests.get(_BING_URL, timeout=10)
    try:
        r.raise_for_status()
    except requests.RequestException:
        LOG.exception(f"Failed to connect to {_BING_URL}")
        return
    img_container = bs4.BeautifulSoup(r.content, "html.parser").find_all(
        "div", class_="img_cont"
    )
    if not img_container:
        raise RuntimeError(f"Failed to parse html from {_BING_URL}.")
    url_for_today = _BING_URL + re.search(r"\((.+)\)", str(img_container)).group(1)
    LOG.info(f"Found today's image URL {url_for_today}")
    md5 = hashlib.md5(url_for_today.encode("utf-8")).hexdigest()
    file_name = destination_directory.joinpath(
        f"{datetime.date.today().isoformat()}_{md5}.jpg"
    )
    LOG.info(f"Hash for today's image URL {md5}")
    if file_name.is_file():
        LOG.info(f"Found {file_name} in {destination_directory}. No-op.")
        return
    try:
        LOG.info(f"Downloading {url_for_today} to {file_name}")
        with requests.get(url_for_today, stream=True) as r:
            r.raise_for_status()
            with open(file_name, "w+b") as f:
                f.write(r.content)
    except requests.RequestException:
        LOG.exception(f"Failed to download {url_for_today}.")
        return
    if archive_directory.is_dir():
        for f in destination_directory.glob("*.jpg"):
            if f == file_name:
                continue
            LOG.info(f"Archiving {f} to {archive_directory}")
            shutil.move(f, archive_directory)
    LOG.info("Done!")


def _parse_args() -> argparse.Namespace:
    """Parse the script's arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dest", help="Destination directory", type=pathlib.Path, required=True
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    if not args.dest.is_dir():
        LOG.error(f"{args.dest} is not a directory.")
        exit(1)
    download_wallpaper(args.dest, args.dest.joinpath("Archive"))
