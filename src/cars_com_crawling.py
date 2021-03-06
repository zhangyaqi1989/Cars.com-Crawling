#!/usr/bin/env python3
##################################
# University of Wisconsin-Madison
# Author: Yaqi Zhang, Jieru Hu
##################################
"""
This module contains function which can crawl cars information
from cars.com
"""

# standard library
import os
import sys
import re
import csv
import json
import math
import urllib.request as urllib2

# third party library
from bs4 import BeautifulSoup as bs

# local library
from handle_search_carscom import generate_url
from utility import user_input, write_cars_to_csv, extract_info_from_csvfilename
from data_analysis import load_csvfile, analyze_price, print_price_info, plot_price_info


def get_more_info(car_detail):
    """
    extract more car infomation from a bs4.element.Tag object into
    a python dictionary

    Args:
        car_detail: bs4.element.Tag object

    Returns:
        car_detail_dict
    """
    # get mileage
    car_miles = car_detail.find('span', class_='listing-row__mileage')
    if car_miles is not None:
        car_miles = (int)(car_miles.text.split()[0].replace(",", ""))
    # distance away
    # 06/01/18 YZ
    distance = (int)(car_detail.find('div',
                                     class_='listing-row__distance listing-row__distance-mobile').text.split()[0])

    car_detail_dict = {"miles": car_miles, "distance_from_Madison": distance}
    # car meta data
    car_metadata = car_detail.find(
        'ul', class_='listing-row__meta').find_all('li')

    for i in car_metadata:
        [attri, value] = i.text.split(":  ")
        car_detail_dict[attri] = value
    return car_detail_dict


def populate_urls(start_url):
    """
    populate urls according to the start_url

    Args:
        start_url

    Returns:
        url list
    """
    cars_per_page = 100
    url_template = re.sub(
        r'page=[0-9]+&perPage=[0-9]+',
        r'page=%d&perPage=%d',
        start_url)
    url_list = []
    # get number of searched cars
    first_url = url_template % (1, cars_per_page)
    with urllib2.urlopen(first_url) as uopen:
        car_url = uopen.read()
        soup = bs(car_url, 'lxml')
        total_cars = (int)(
            soup.find_all(
                "div",
                class_="matchcount")[0].find_all(
                "span",
                "count")[0].getText().replace(
                ",",
                ""))
    # num_of_urls = (int)(total_cars/cars_per_page) + 1 if total_cars%cars_per_page else (int)(total_cars/cars_per_page)
    num_of_urls = math.ceil(total_cars / cars_per_page)
    for i in range(num_of_urls):
        url_list.append(url_template % (i + 1, cars_per_page))
    return url_list


def read_and_crawl():
    """
    crawl multiple models, crawl and compare
    """
    if len(sys.argv) != 7:
        print(
            "Usage: >> python {} <maker_model_file> <zip> <radius> <used or new> <json or keyfile> <output_dir>".format(
                sys.argv[0]))
        print(
            "e.g. python {} <maker_model_file> 53715 25 used <json or keyfile> ./data/".format(sys.argv[0]))
        sys.exit(1)
    with open(sys.argv[1], 'r') as mmfile:
        maker_models = (tuple(line.split(":")) for line in mmfile.readlines())
    # print(maker_models)
    zipcode = int(sys.argv[2])
    radius = int(sys.argv[3])
    condition = sys.argv[4]
    car_json_file = sys.argv[5]
    output_dir = sys.argv[6]
    # if the output_dir does not exist, create it
    os.makedirs(output_dir, exist_ok=True)
    car_infos = []
    price_infos = []
    for maker, model in maker_models:
        maker = maker.strip()
        model = model.strip()
        page_num = 1
        num_per_page = 100
        start_url = generate_url(
            maker,
            model,
            zipcode,
            radius,
            car_json_file,
            condition,
            page_num,
            num_per_page)
        csv_name = "{}-{}-{:d}-{:d}-{:s}.csv".format(
            maker, model, zipcode, radius, condition)
        csv_name = os.path.join(output_dir, csv_name)
        print("crawling {} {} {}...".format(condition, maker, model))
        craw_from_url(start_url, csv_name)
        print("finish crawling...")
        df = load_csvfile(csv_name)
        car_info = extract_info_from_csvfilename(csv_name)
        price_info = analyze_price(df)
        car_infos.append(car_info)
        price_infos.append(price_info)
    plot_price_info(car_infos, price_infos)


def pipeline_carscom():
    """
    crawling pipeline for cars.com
    """
    maker, model, zipcode, radius, condition, car_json_file, directory = user_input()
    page_num = 1
    num_per_page = 100
    start_url = generate_url(
        maker,
        model,
        zipcode,
        radius,
        car_json_file,
        condition,
        page_num,
        num_per_page)
    csv_name = "{}-{}-{:d}-{:d}-{:s}.csv".format(
        maker, model, zipcode, radius, condition)
    directory = os.path.dirname(os.path.realpath(__file__))
    csv_name = os.path.join(directory, csv_name)
    print("crawling {} {} {}...".format(condition, maker, model))
    craw_from_url(start_url, csv_name)
    print("finish crawling...")
    df = load_csvfile(csv_name)
    car_info = extract_info_from_csvfilename(csv_name)
    price_info = analyze_price(df)
    print_price_info(price_info, car_info)


def craw_from_url(start_url, csv_name):
    """
    crawl data from url and write data to csv file

    Args:
        start_url: start url
        csv_name: csv filename for saving
    """
    url_lst = populate_urls(start_url)
    csv_rows = []
    # start crawling given a list of cars.com urls
    count = 0
    for url in url_lst:
        with urllib2.urlopen(url) as uopen:
            oururl = uopen.read()
        soup = bs(oururl, 'lxml')
        # get car general information from json script
        # 04/29/18 YZ use findAll and pick the last
        contents = soup.findAll('script', type='application/ld+json')[-1].text
        cars_info = json.loads(contents)
        # cars_info = json.loads(soup.findall('script', type='application/ld+json').text)

        # get more detailed car information from HTML tags
        cars_detail_list = soup.find_all(
            'div', class_='shop-srp-listings__listing')
        # print(cars_detail_list)
        if (len(cars_info) != len(cars_detail_list)):
            print(
                "Error the size of car json information and size of car html information does not match")
            sys.exit(1)
            continue

        # for each car, extract and insert information into csv table
        for ind, car_data in enumerate(cars_info):
            count += 1
            car_info = {"name": car_data['name'], "brand": car_data['brand']['name'], "color":
                        car_data['color'], "price": car_data['offers']['price'], "seller_name":
                        car_data['offers']['seller']['name'], "VIN": car_data['vehicleIdentificationNumber']}
            # need to check for telephone because some sellers does not have
            # telephone
            if 'telephone' in car_data['offers']['seller']:
                car_info['seller_phone'] = car_data['offers']['seller']['telephone']

            # need to check for aggregateRating because some seller does not
            # have rating
            if 'aggregateRating' in car_data['offers']['seller']:
                car_info['seller_average_rating'] = car_data['offers']['seller']['aggregateRating']['ratingValue']
                car_info['seller_review_count'] = car_data['offers']['seller']['aggregateRating']['reviewCount']

            car_details = get_more_info(cars_detail_list[ind])

            # combine two dicts
            car_dict = {**car_info, **car_details}
            csv_rows.append(dict(car_dict))

    csv_header = ["name", "brand", "color", "price", "seller_name", "seller_phone",
                  "seller_average_rating", "seller_review_count", "miles", "distance_from_Madison", "Exterior Color",
                  "Interior Color", "Transmission", "Drivetrain", "VIN"]
    write_cars_to_csv(csv_name, csv_header, csv_rows)


if __name__ == "__main__":
    read_and_crawl()
