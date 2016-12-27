#!/Users/username/anaconda/bin/python

import os
import stat
import hashlib
import sys
import datetime
import requests
import bs4

# define destination root directory
root_dir = "/Users/username/Pictures/Bing"
arch_dir = os.path.join(root_dir, "Archive")

# create our archive directory
if not os.path.exists(arch_dir):
    os.mkdir(arch_dir, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)

# find today's image url
feed_url = "https://www.iorise.com/?feed=rss2"
feed = bs4.BeautifulSoup(requests.get(feed_url).content, "lxml")
for item in feed.channel:
    if "Worldwide, %s" % str(datetime.date.today()) in str(item.title):
        image_url = item.find("content:encoded").a.get("href")

# calculate md5 signature and confirm we don't already have this file downloaded
url_sig = hashlib.md5(image_url).hexdigest()
if any(url_sig in fn for fn in os.listdir(root_dir)):
    sys.exit(0)

# archive existing .jpg files
for f in os.listdir(root_dir):
    if os.path.isfile(os.path.join(root_dir, f)) and os.path.splitext(f)[1] == '.jpg':
        os.rename(os.path.join(root_dir, f), os.path.join(root_dir, arch_dir, f))

# download the file
image_fn = os.path.join(root_dir, "%s_%s.jpg" % (str(datetime.date.today()), url_sig))
r = requests.get(image_url, stream=True)
if r.status_code == 200:
    with open(image_fn, 'wb') as f:
        for chunk in r:
            f.write(chunk)
