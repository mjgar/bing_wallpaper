import argparse
import datetime
import hashlib
import logging
import os
import re
import shutil

import bs4
import funcy
import requests


logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] - %(levelname)s - %(message)s')
log = logging.getLogger()


@funcy.retry(3, timeout=lambda a: 2 ** a)
def main(dest: str):
    """
    @param: dest Destination for downloaded image
    Find the URL of today's wallpaper, download it if the URL's md5sum doesn't exist.
    Destination filename will be YYYY-mm-dd_{md5dum}.jpg
    """
    bing_url = 'https://bing.com'
    archive_dir = os.path.join(dest, 'Archive')

    try:
        log.info(f"Connecting to {bing_url}")
        r = requests.get(bing_url)
        if not r.ok:
            raise f"{r.reason}"
    except:
        log.error(f"Could not get data from {bing_url}. Exiting.")
        return

    img_cont = bs4.BeautifulSoup(
        r.content, 'html.parser').find_all('div', class_='img_cont')
    if len(img_cont) < 0:
        log.error(f"Could not parse html from {bing_url}. Exiting.")
        return
    url = bing_url + re.search(r'\((.+)\)', str(img_cont)).group(1)
    log.info(f"Image url parsed from html as {url}")
    md5sum = hashlib.md5(url.encode('utf-8')).hexdigest()
    log.info(f"Hash of {url} calculated as {md5sum}")

    # Stop if we have this checksum in dest
    existing_files = os.listdir(dest)
    log.debug(f"Existing files in {dest} are {existing_files}")
    if any(md5sum in f for f in existing_files):
        log.info(f"Hash {md5sum} found in {dest}. Exiting.")
        return

    # Build the filename
    image_file = f"{datetime.date.today().isoformat()}_{md5sum}.jpg"
    image_fullname = os.path.join(dest, image_file)

    # Download the file
    try:
        log.info(f"Downloading {url} to {image_fullname}")
        r = requests.get(url, allow_redirects=True)
        if r.ok:
            with open(image_fullname, 'wb') as f:
                log.debug(f"Writing to disk as {image_fullname}")
                f.write(r.content)
        else:
            log.error(f"Could not download {url}, reason: {r.reason}")
    except:
        log.error(f"Could not download {url} to {image_fullname}")
        return

    # Archive the existing file
    if os.path.isdir(archive_dir):
        for f in existing_files:
            if f.endswith('.jpg'):
                log.info(f"Archiving {f} to {archive_dir}")
                shutil.move(os.path.join(dest, f), archive_dir)

    # Done
    log.info('Done')


if __name__ == '__main__':
    """ Initialize a (very basic) argument parser with destination directory
        and download the image there archiving any existing .jpgs to {dest}/Archive
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--dest', type=str, required=True)
    args = parser.parse_args()
    if not os.path.isdir(args.dest):
        log.error(f"{args.dest} is not a directory. Exiting.")
    else:
        main(args.dest)
