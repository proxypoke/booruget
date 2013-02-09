#!/usr/bin/env python3
# booruget - download images from safebooru (or other *boorus)
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is free software under the non-terms
# of the Anti-License. Do whatever the fuck you want.
#
# Github: https://www.github.com/proxypoke/booruget
#
# Format options for vim. Please adhere to them.
# vim: set et ts=4 sw=4 tw=80:

import os
import requests
import argparse
from urllib.parse import urlparse
from bs4 import BeautifulSoup as bs


def get_all_image_links(page, root=''):
    '''Get all image links from a given soup object.'''
    links = page.find_all('a')
    # Get all links which contain an <img> tag.
    return [root + link.get('href') for link in links if not
            link.find('img') is None]


def get_image_from_page(url):
    '''Get the image as a requests object from a booru image page.'''
    page = requests.get(url)
    soup = bs(page.text)
    img = soup.find('img')
    if img is None:
        return None
    else:
        return img.get('src')


def get_orginal_size(urls):
    '''Reform the given urls so that they don't link to resized images.'''
    return  [url.replace("sample_", "")
             .replace("sample", "image")
             for url in urls]


def save_image(url, dir='.'):
    '''Save the image at url to the given dir (default: current dir).'''
    img = requests.get(url)
    ext = img.headers['content-type'].split('/')[-1]
    name = dir + "/" + url.split('?')[-1] + "." + ext
    # don't do anything if the file exists
    if os.access(name, os.F_OK):
        return
    file = open(name, 'wb')
    file.write(img.content)
    file.close()


def next_page(page, root):
    '''Get the next page, or return None if there isn't one.'''
    soup = page.find('a', alt='next')
    if soup is None:
        return
    else:
        url = root + soup.get('href')
    return bs(requests.get(url).text)


def main():
    parser = argparse.ArgumentParser(description="Download images from " +
                                     "safebooru and compatible sites.")
    parser.add_argument('url', help='a safebooru page from which to start scraping')
    parser.add_argument('-o', '--output', default=".",
                        help='directory to save the images to')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help="report what's going on")

    args = parser.parse_args()

    req = requests.get(args.url)
    page = bs(req.text)
    root = '://'.join(urlparse(args.url)[0:2]) + '/'

    i = 1
    while True:
        if args.verbose:
            print("Processing page {0}...".format(i))
        links = get_all_image_links(page, root)
        imgs = [get_image_from_page(link) for link in links]
        # Remove entries that pointed to images which have been deleted.
        for i in range(imgs.count(None)):
            imgs.remove(None)
        imgs = get_orginal_size(imgs)
        for img in imgs:
            if args.verbose:
                print("Downloading {0}...".format(img))
            save_image(img, args.output)
        page = next_page(page, root)
        i += 1
        if page is None:
            print("No more pages. I'm done.")
            break


if __name__ == "__main__":
    main()
