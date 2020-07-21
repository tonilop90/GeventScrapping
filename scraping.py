import json
import math
import sys
import time
from typing import List
import psycopg2
import requests
from bs4 import BeautifulSoup

from classes import Hotel

from utils import (chunks, city_parser,
                   get_comments_by_country, build_data_insert)


class BookingHotelPageScraper(object):

    def __init__(self, urls: List[str]):
        self.urls = urls
        self.urls_chunks = chunks(self.urls, 5)

    @staticmethod
    def extract_data(soup, hotel, country):
        """ Extract data of soup """

        """Hotel name"""
        name = soup.find(class_="bh-photo-modal-name")

        """ Total user comments """
        total_comments = soup.find(class_='bui-review-score__text')

        if total_comments:
            parse_comment = total_comments.text.strip().split()[0].replace('.',
                                                                           '')

            """ Number of comment pages"""
            pages = math.ceil((int(parse_comment) / 20))

            """ Get all the comments grouped by country """
            comm_by_country = get_comments_by_country(pages=pages,
                                                      hotel=hotel,
                                                      country=country)
        else:
            comm_by_country = get_comments_by_country(pages=1,
                                                      hotel=hotel,
                                                      country=country)
            parse_comment = sum(comm_by_country.values())

        """ Hotel city """
        city = soup.find(class_='hp_address_subtitle')
        parse_city = city_parser(city)

        lat = None
        lng = None
        coords = soup.find(id='hotel_surroundings').attrs.get(
            'data-atlas-latlng')
        lat, lng = coords.split(',')
        kwargs = {
            'name': name.text.strip() if name else '',
            'lat': float(lat),
            'lng': float(lng),
            'total_comments': int(parse_comment),
            'city': parse_city,
            'comments_by_country': comm_by_country
        }
        return Hotel(**kwargs).to_dict()

    def start(self):
        """ To Scrap data and Insert data of hotel in our PSQL DB"""
        time_start = time.time()
        hotel_list_data = []
        conn = psycopg2.connect(user='toni', password='antoniojls',
                                host='localhost', port='5432',
                                database='gevent')
        cursor = conn.cursor()
        try:
            insert_query = """ INSERT INTO test_gevent(NAME,LAT,LONG,TOTAL_COMMENTS,CITY,COM_BY_COUNTRY,LAST_MOD) VALUES (%s, %s, %s, %s, %s, %s, %s)"""  # NOQA
            for index, url in enumerate(self.urls):
                try:
                    url = url
                    url_splitted = url.split('/')
                    country = url_splitted[4]
                    hotel_name = url_splitted[5].split('.')[0]
                    response = requests.get(url)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    hotel_data = self.extract_data(soup=soup,
                                                   hotel=hotel_name,
                                                   country=country)
                    insert_data = build_data_insert(hotel_data)
                    hotel_list_data.append(insert_data)
                    if len(hotel_list_data) == 50 or \
                            (index + 1) == len(self.urls):
                        cursor.executemany(insert_query, hotel_list_data)
                        conn.commit()
                        hotel_list_data = []
                        print('Hotel:', hotel_name, '--- Scrap: OK')
                except Exception as e:
                    print('Hotel:', hotel_name, ' --- Error:', e)
        except (Exception, psycopg2.Error) as error:
            if conn:
                print("Failed to insert record into table", error)
        finally:
            """ Close database connection """
            if conn:
                cursor.close()
                conn.close()
                print("Scrapping finished.")
                print("PostgreSQL connection is closed")
                end_time = time.time()
                print('time:', end_time - time_start)
                sys.exit()
