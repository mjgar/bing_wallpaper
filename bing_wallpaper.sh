#!/usr/bin/env bash

# create our directory tree
mkdir -p ~/Pictures/Bing/Archive

# change to our destination directory
cd ~/Pictures/Bing

# today's image
URL=$(curl -s http://feeds.feedburner.com/bingimages | grep url | sed -e "s/.*url=\"\([^\"]*\).*/\1/" | head -1)
URLSIG=$(/sbin/md5 -q -s ${URL})
TODAY="$(date +%Y-%m-%d)_${URLSIG}.jpg"

# exit if we already have today's image
if [[ $(find . -type f -name "*${URLSIG}*") ]];
then
    exit 0
fi

# archive old images
mv ./*.jpg Archive/

# download latest image
curl ${URL} -s -o ${TODAY}

# the next time OS X changes the wallpaper it should find the the new file and update the wallpaper
# assumes OS X is configured to rotate the wallpaper from ~/Pictures/Bing at some interval
# i run this script on the 59th minute of every hour and configured OS X to change the wallpaper every hour
