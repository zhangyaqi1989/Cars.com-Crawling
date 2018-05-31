#!/usr/bin/env python3
##################################
# University of Wisconsin-Madison
# Author: Yaqi Zhang, Jieru Hu
##################################
"""
This module contains functions that generates url on cars.com
according to user's query
"""

# standard library
import sys
import re
import json
import csv
from difflib import SequenceMatcher

# local library
from utility import write_cars_to_csv
# from pprint import pprint


def construct_maker_model_dict(data_file='model_codes_carscom.csv'):
    """
    construct a dict d[maker][model] = (maker_id, model_id) from
    csv file

    Args:
        data_file: model codes csv file
    """
    d = defaultdict(dict)
    with open(data_file, 'r') as f:
        reader = csv.DictReader(f)
        for line in reader:
            d[line['maker']][line['model']] = (line['maker code'],
                                               line['model code'])
    return d


def string_similar(sa, sb):
    """
    compute similarity ratio of two strings
    """
    return SequenceMatcher(None, sa, sb).ratio()


def print_maker_model_id():
    """
    print id information for different makers and models
    """
    data = json.load(open('cars_com_make_model.json'))
    data = data['all']
    for i, maker in enumerate(data, 1):
        print("{:2d}. {:s}\t{:d}".format(i, maker['nm'], maker['id']))
        for j, model in enumerate(maker['md'], 1):
            print("\t{:2d}.{:d} {:s}\t{}".format
                  (i, j, model['nm'], model['id']))


def search_makerID_and_modelID(mk, md, car_json_file):
    """
    search maker id and model id

    Args:
        mk: maker string
        md: model string
        car_json_file: cars.com mk-md json file

    Returns:
        (mkid, mdid): maker id, model id
    """
    data = json.load(open(car_json_file))
    data = data['all']
    mk = mk.lower()
    md = md.lower()
    # add some rules
    # 1. Mercedes Benz
    if mk == "mb" or mk == "benz" or mk == "mercedes":
        mk = "mercedes-benz"
    if mk == "mercedes-benz":
        if md in ['c', 'e', 'cla', 'cls', 'e', 'g', 'gl',
                  'gla', 'gle', 'glc', 'gls', 'm', 's']:
            md += "-class"
    # 2. BMW
    if mk == "bmw":
        if md in ['2', '3', '4', '5', '6', '7']:
            md += '-Series'
    # 3. Honda
    if mk == "honda":
        if md == "crv":
            md = "cr-v"
        if md == "crz":
            md = "cr-z"
        if md == "hrv":
            md = "hr-v"
    mkid, mdid = None, None
    for i, maker in enumerate(data, 1):
        if maker['nm'].lower() == mk:
            mkid = maker['id']
            for j, model in enumerate(maker['md'], 1):
                model_name = model['nm'].strip().lower()
                if model_name.startswith('-'):
                    # model_name = model_name.replace('-', '')
                    model_name = model_name[1:]
                    model_name = model_name.strip()
                if model_name == md.lower():
                    mdid = model['id']
                    return mkid, mdid
    if not mkid:
        print("invalid maker name {}".format(mk))
        sys.exit(1)
    elif not mdid:
        print("invalid model name {}".format(md))
        sys.exit(1)
    return None, None


def generate_url(maker, model, zipcode, radius, car_json_file,
                 condition="new", page_num=1, num_per_page=100):
    """
    generate url according to search query

    Args:
        maker: maker string
        model: model string
        zipcode: zipcode (int)
        radius: radius (int)
        cat_json_file: cars.com mk-md json file
        condition: condition

    Returns:
        url
    """
    if condition.lower() == "used" or condition.lower() == "old":
        choose_all = False
        new_used_code = 28881
    elif condition.lower() == "new":
        choose_all = False
        new_used_code = 28880
    else:
        choose_all = True
    if choose_all:
        template_url = "https://www.cars.com/for-sale/searchresults.action/?mkId=%s&mdId=%s&page=%d&perPage=%d&rd=%d&zc=%d&searchSource=QUICK_FORM"
    else:
        template_url = "https://www.cars.com/for-sale/searchresults.action/?mkId=%s&mdId=%s&page=%d&perPage=%d&rd=%d&zc=%d&stkTypId=%d&searchSource=QUICK_FORM"
    mkid, mdid = search_makerID_and_modelID(maker, model, car_json_file)
    if mkid and mdid:
        if choose_all:
            url = template_url % (mkid, mdid, page_num,
                                  num_per_page, int(radius), zipcode)
        else:
            url = template_url % (mkid,
                                  mdid,
                                  page_num,
                                  num_per_page,
                                  int(radius),
                                  zipcode,
                                  new_used_code)
    return url


def test():
    """test generate_url"""
    maker = 'Audi'
    model = 'Q7'
    zipcode = 53705
    radius = 200  # miles
    used = False
    page_num = 1
    num_per_page = 100
    url = generate_url(
        maker,
        model,
        zipcode,
        radius,
        used,
        page_num,
        num_per_page)
    print(url)
    # url = re.sub(r'page=[0-9]+&perPage=[0-9]+', r'page=%d&perPage=%d', url)
    # print(url)


if __name__ == "__main__":
    print("Hello World")
    print_maker_model_id()
    # test()
