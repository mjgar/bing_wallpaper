#!/Users/username/anaconda/bin/python

import os
import stat
import hashlib
import sys
import datetime
import requests
import bs4

# define destination root directory
root_dir = '/Users/username/Pictures/Bing'
arch_dir = os.path.join(root_dir, 'Archive')
today = str(datetime.date.today())

# create our archive directory
if not os.path.exists(arch_dir):
    os.mkdir(arch_dir, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)

# find today's image url
feed_url = 'https://www.iorise.com/?feed=rss2'
feed = bs4.BeautifulSoup(requests.get(feed_url).content, 'lxml')
for item in feed.channel:
    if 'Worldwide, %s' % today in str(item.title):
        image_url = item.find('content:encoded').a.get('href')
        break

# get files in root_dir
root_dir_files = os.listdir(root_dir)

# calculate md5 signature and confirm we don't already have this file downloaded
url_sig = hashlib.md5(image_url).hexdigest()
if any(url_sig in f for f in root_dir_files):
    sys.exit(0)

# archive existing .jpg files
for f in root_dir_files:
    if os.path.isfile(os.path.join(root_dir, f)) and os.path.splitext(f)[1] == '.jpg':
        os.rename(os.path.join(root_dir, f), os.path.join(root_dir, arch_dir, f))

# download the file
image_file = os.path.join(root_dir, '%s_%s.jpg' % (today, url_sig))
r = requests.get(image_url, stream=True)
if r.status_code == 200:
    with open(image_file, 'wb') as f:
        for chunk in r:
            f.write(chunk)

# The next time macOS changes the wallpaper it should find the the new file and update the wallpaper
# assuming macOS is configured to rotate the wallpaper from /Users/username/Pictures/Bing at some interval
# I run this script every 5 minutes and configure macOS to update the wallpaper every 15