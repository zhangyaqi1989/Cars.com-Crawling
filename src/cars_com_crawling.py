#!/usr/bin/env python3
##################################
# University of Wisconsin-Madison
# Author: Yaqi Zhang, Jieru Hu
##################################
# This module contains function which can
# crawl cars information from cars.com
#########################################

import os
import sys
import re
import csv
import json
import urllib.request as urllib2
from bs4 import BeautifulSoup as bs
from handle_search_carscom import generate_url
from utility import user_input, write_cars_to_csv
from data_analysis import load_csvfile, analyze_price


def get_more_info(car_detail):
    """extract more car infomation from a bs4.element.Tag object into
       a python dictionary
    """
    # get mileage
    car_miles = car_detail.find('span', class_='listing-row__mileage')
    if car_miles != None:
        car_miles = (int)(car_miles.text.split()[0].replace(",",""))
    # distance away
    distance = (int)(car_detail.find('div', \
            class_='listing-row__distance listing-row__distance-mobile').text.split()[1])

    car_detail_dict = {"miles": car_miles, "distance_from_Madison" : distance }
    # car meta data
    car_metadata = car_detail.find('ul', class_='listing-row__meta').find_all('li')

    for i in car_metadata:
        [attri, value] = i.text.split(":  ")
        car_detail_dict[attri] = value
    return car_detail_dict


def populate_urls(start_url):
    """populate urls according to the start_url"""
    cars_per_page = 100
    url_template = re.sub(r'page=[0-9]+&perPage=[0-9]+', r'page=%d&perPage=%d', start_url)
    url_list = []
    # get number of searched cars
    first_url = url_template%(1, cars_per_page)
    with urllib2.urlopen(first_url) as uopen:
        car_url = uopen.read()
        soup = bs(car_url, 'lxml')
        total_cars = (int)(soup.find_all("div", class_="matchcount")[0].find_all("span", "count")[0].getText().replace(",", ""))
    num_of_urls = (int)(total_cars/cars_per_page) + 1 if total_cars%cars_per_page else (int)(total_cars/cars_per_page)
    for i in range(num_of_urls):
        url_list.append(url_template%(i+1, cars_per_page))
    return url_list


def pipeline_carscom(directory='./'):
    """crawling pipeline for cars.com"""
    maker, model, zipcode, radius, condition, car_json_file, directory = user_input()
    page_num = 1
    num_per_page = 100
    start_url = generate_url(maker, model, zipcode, radius, car_json_file, condition, page_num, num_per_page)
    csv_name = "{}-{}-{:d}-{:d}-{:s}.csv".format(maker, model, zipcode, radius, condition)
    csv_name = os.path.join(directory, csv_name)
    print("crawling...")
    craw_from_url(start_url, csv_name)
    print("finish crawling...")
    df = load_csvfile(csv_name)
    if '/' in csv_name:
        csv_name = csv_name[csv_name.rfind('/') + 1 : ]
    maker, model = csv_name.split('-')[:2]
    maker = maker.upper()
    model = model.upper()
    analyze_price(df, maker, model)


def craw_from_url(start_url, csv_name):
    """craw data and write data to csv file"""
    url_lst = populate_urls(start_url)
    csv_rows = []
    # start crawling given a list of cars.com urls
    count = 0
    for url in url_lst:
        with urllib2.urlopen(url) as uopen:
            oururl = uopen.read()
        soup = bs(oururl, 'lxml')
        # get car general information from json script
        cars_info = json.loads(soup.find('script', type='application/ld+json').text)

        # get more detailed car information from HTML tags
        cars_detail_list = soup.find_all('div', class_='shop-srp-listings__listing')

        if (len(cars_info) != len(cars_detail_list)):
            print ("Error the size of car json information and size of car html information does not match")
            continue

        # for each car, extract and insert information into csv table
        for ind, car_data in enumerate(cars_info):
            count += 1
            # print (count, ": ", car_data['name'])
            car_info = {"name": car_data['name'], "brand": car_data['brand']['name'], "color":
                    car_data['color'], "price": car_data['offers']['price'], "seller_name":
                    car_data['offers']['seller']['name'], "VIN": car_data['vehicleIdentificationNumber']}
            # need to check for telephone because some sellers does not have telephone
            if 'telephone' in car_data['offers']['seller']:
                car_info['seller_phone'] = car_data['offers']['seller']['telephone']

            # need to check for aggregateRating because some seller does not have rating
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
  pipeline_carscom()
