import json
import requests
from bs4 import BeautifulSoup
from datetime import date


def chunks(l, n):
    def retrieve_yield(i, n):
        yield l[i:i + n]
    """Yield successive n-sized chunks from l."""
    [retrieve_yield(i, n)for i in range(0, len(l), n)]


def build_data_insert(hotel_data):
    hotel_name = hotel_data.get('name')
    hotel_lng = hotel_data.get('lng')
    hotel_lat = hotel_data.get('lat')
    hotel_city = hotel_data.get('city')
    total_comments = hotel_data.get('total_comments')
    comments_by_country = hotel_data.get('comments_by_country')
    today = date.today()
    insert_data = (hotel_name, hotel_lat,
                   hotel_lng, total_comments,
                   hotel_city, json.dumps(comments_by_country),
                   today)
    return insert_data


def city_parser(city: str = None):
    """ Parser for booking hotels cities"""
    return city.text.strip().split(',')[1]


def get_comments_by_country(pages, hotel, country):

    """ Generate all the requests for get all the users comments """
    url = "http://www.booking.com/reviewlist.es.html"
    headers = {
        'User-Agent': "PostmanRuntime/7.20.1",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Postman-Token': "4b4e2c78-12c0-42a7-807a-29f5f7378ae5,e75b58fb-25dd-4fdd-b97a-47650ed52d41",  # NOQA
        'Host': "www.booking.com",
        'Accept-Encoding': "gzip, deflate",
        'Cookie': "bkng=11UmFuZG9tSVYkc2RlIyh9Yaa29%2F3xUOLbca8KLfxLPeck0I1eO54zQUW2YGGgHUJ6NVSV%2BmLwJzaS5ibHX0J%2BdueF6GNDCq1X0NvEJAU9t%2FoaAC2%2FMBm39Gz0lTSWuf6zuBVIiNGAI88YDjaj4w5H8Lrv7T0Yug9jg%2FpPsONkdMVLMiYifIslIsLvFl07K%2BTKGRykCAxOsgE%3D",  # NOQA
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    params = {
        'cc1': country,
        'pagename': hotel,
        'type': 'total',
        'dist': str(1),
        'rows': str(20)
    }

    def build_soup_comment_request(page: int, list_of_countries):
        if page == 0:
            params['offset'] = str(page)
        else:
            params['offset'] = str(page * 20)

        response = requests.get(url=url, params=params, headers=headers)
        comments_soup = BeautifulSoup(response.content, 'html.parser')
        span = comments_soup.select('.bui-avatar-block__flag img')
        [get_flags(item, list_of_countries) for item in span]

    countries_list = {}
    [build_soup_comment_request(page, countries_list) for page in range(pages)]
    return countries_list


def get_flags(item, list_of_countries: dict):
    item_splitted = item['src'].split('/')
    flag_index = item_splitted.index('flags')
    country_code = item_splitted[
        flag_index + 2] if flag_index != -1 else ''
    if country_code in list_of_countries:
        list_of_countries[country_code] += 1
    else:
        list_of_countries[country_code] = 1
