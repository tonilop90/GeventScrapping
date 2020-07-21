from multiprocessing.context import Process
import settings
import os
import xml.etree.ElementTree as ET
import numpy as np
from scraping import BookingHotelPageScraper


def get_all_sitemaps_paths():
    """ Get all de xml files of our project with the urls """
    sitemaps_paths = []
    [
        [sitemaps_paths.append(os.path.join(r, file)) for file in f
         if '.xml' in file]
        for r, d, f in os.walk(settings.SITEMAPS_DIR)
    ]
    return sitemaps_paths


def get_sitemap_urls(sitemaps_path: str, country: str):
    """ Get all the urls from de xml file """
    tree = ET.parse(sitemaps_path)
    root = tree.getroot()
    sitemaps_paths = []
    [generate_sitemaps_path(sitemap, sitemaps_paths, country)
     for sitemap in root.findall('url')]
    return sitemaps_paths


def generate_sitemaps_path(sitemap, sitemaps_paths, country):
    sitemap_loc = sitemap.find('loc')
    if sitemap_loc is not None:
        if country in sitemap_loc.text:
            sitemaps_paths.append(sitemap_loc.text)


def do_scraping_from_sitemaps(country: str):
    """ Launch scrapping for each of the hotels """
    sitemaps_paths = get_all_sitemaps_paths()
    l = len(sitemaps_paths)
    for i, sitemaps_path in enumerate(sitemaps_paths):
        sitemap_urls = get_sitemap_urls(sitemaps_path=sitemaps_path,
                                        country=country)
        if sitemap_urls:
            numpy = np.array(sitemap_urls)
            urls_splitted = np.array_split(numpy, 2)
            p = Process(target=init_scrap, args=(tuple([urls_splitted[0]])))
            p.start()
            p2 = Process(target=init_scrap,
                         args=(tuple([urls_splitted[1]])))
            p2.start()
            p.join()
            p2.join()


def init_scrap(sitemap_urls: []):
    scraper = BookingHotelPageScraper(urls=sitemap_urls)
    data = scraper.start()


menu = {
    "1": (
        'Do scraping from sitemaps', do_scraping_from_sitemaps
    )
}


def display_menu():
    app_logo = '''
      _                 _    _                  
     | |__   ___   ___ | | _(_)_ __   __ _  
     | '_ \ / _ \ / _ \| |/ / | '_ \ / _` | 
     | |_) | (_) | (_) |   <| | | | | (_| |
     |_.__/ \___/ \___/|_|\_\_|_| |_|\__, |
                                     |___/                   
    '''
    print(chr(27) + "[2J")
    print(app_logo)
    print("Hotels scrapping of all booking.com hotels")
    for key, configuration in menu.items():
        name, handler = configuration
        print("{}) {}".format(key, name))

    print("Select a country for scrap: ", end='')
    return input()


while True:
    option = display_menu()
    option = '/%s/' % option
    do_scraping_from_sitemaps(country=option)

