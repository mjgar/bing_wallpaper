bing.py
==============

Script to download current background from [https://bing.com](bing.com) to be used as a wallpaper.

Running the script
==========

## First we create our environment
Either with conda
```
conda create -n bing -c defaults -c conda-forge python=3.7 requests beautifulsoup4 funcy
```

Or with pip
```
pip install funcy requests beautifulsoup4
```

We can now run the script from the conda environment or venv/python environment _eg._ `python bing.py --dest ~/Desktop`

More details
========

The next time MacOS changes the wallpaper it should find the the new file and update the wallpaper, assuming it is configured to rotate the wallpaper using the script's destination directory as the source. I run this script every 5 minutes and have MacOS configured to rotate the wallpaper every 15.

Also on my blog, _tbd_
