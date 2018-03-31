#!/usr/bin/env python3
##################################
# University of Wisconsin-Madison
# Author: Yaqi Zhang, Jieru Hu
##################################
# This module contains some utility functions
#############################################

import os
import sys
import csv
import string
import random
import json
from collections import OrderedDict, defaultdict


def user_input():
    """parse command line args"""
    if len(sys.argv) != 8:
        print("Usage: >> python {} <maker> <model> <zip> <radius> <used or new> <json or keyfile> <output_dir>".format(sys.argv[0]))
        print("e.g. python {} Honda Accord 53715 25 used <json or keyfile> ./data/".format(sys.argv[0]))
        sys.exit(1)
    # need to add validation check
    maker = sys.argv[1]
    model = sys.argv[2]
    zipcode = int(sys.argv[3])
    radius = int(sys.argv[4])
    condition = sys.argv[5]
    extra_file = sys.argv[6]
    output_dir = sys.argv[7]
    os.makedirs(output_dir, exist_ok=True) # if the output_dir does not exist, create it
    return (maker, model, zipcode, radius, condition, extra_file, output_dir)


def write_cars_to_csv(csv_name, csv_header, csv_rows):
    """create csv file and write rows to the csv file"""
    # delete previous csv file with the same name
    if os.path.exists(csv_name):
        try:
            os.remove(csv_name)
            print("delete previous {}".format(csv_name))
        except OSError:
            print("error in deleting {}".format(csv_name))
            sys.exit(1)
    with open(csv_name, 'w') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=csv_header)
        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)
    print("Writing {:d} cars information to {:s}".format(len(csv_rows), csv_name))


def guess_car_brand(data_file='model_codes_carscom.csv'):
    """A terminal game which lets user guess car brand"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_file = os.path.join(dir_path, 'model_codes_carscom.csv')
    if not os.path.exists(data_file):
        extract_maker_model_codes(data_file)
    num_questions = 10
    num_correct = 0
    num_choices = 4
    letters = string.ascii_uppercase[:num_choices]
    # load data
    brands = set()
    model_brand_pairs = {}
    with open(data_file, 'r') as f:
        reader = csv.DictReader(f)
        for line in reader:
            brands.add(line['maker'])
            model_brand_pairs[line['model']] = line['maker']
    count = num_questions
    question_num = 0
    while count > 0:
        count -= 1
        model, brand = random.choice(list(model_brand_pairs.items()))
        question_num += 1
        print("{:d}. What is the brand of {}? (choose one from {} to {})".\
                format(question_num, model, letters[0], letters[-1]))
        choices = random.sample(brands, num_choices - 1)
        choices.append(brand)
        random.shuffle(choices)
        d = OrderedDict(zip(letters, choices))
        for letter, choice in d.items():
            print("{}. {}  ".format(letter, choice), end="")
        print()
        while True:
            user_choice = input("> ")
            user_choice = user_choice.upper()
            if user_choice in letters:
                break
            else:
                print("please pick a valid choice")
        if user_choice in d and d[user_choice] == brand:
            print("correct!")
            num_correct += 1
        else:
            print("wrong!")
    print("Score {:d}/{:d}".format(num_correct, num_questions))


def extract_maker_model_codes(csv_name):
    """extract maker and model cars.com code and store in
       a csv file
    """
    csv_header = ['maker', 'model', 'maker code', 'model code']
    csv_rows = []
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data = json.load(open(os.path.join(dir_path, 'cars_com_make_model.json')))
    data = data['all']
    car_dict = {}
    for i, maker in enumerate(data, 1):
        car_dict['maker'] = maker['nm'].strip()
        car_dict['maker code'] = maker['id']
        for j, model in enumerate(maker['md'], 1):
            model_name = model['nm'].strip()
            if model_name[0] == '-':
                model_name = model_name[1:].strip()
            car_dict['model'] = model_name
            car_dict['model code'] = model['id']
            csv_rows.append(dict(car_dict))
    write_cars_to_csv(csv_name, csv_header, csv_rows)

if __name__ == "__main__":
    print("Hello World")
    guess_car_brand()
