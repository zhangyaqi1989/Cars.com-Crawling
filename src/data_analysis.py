#!/usr/bin/env python3
##################################
# University of Wisconsin-Madison
# Author: Yaqi Zhang, Jieru Hu
##################################
# This module contains some functions
# that analyze car data in csv file
##################################

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utility import extract_info_from_csvfilename

def add_year_column(df):
    """extract year info from name column and create a new column called year"""
    names = df['name']
    years = []
    for name in names:
        year_str = name.split()[0]
        try:
            year = int(year_str)
        except ValueError:
            year = 2018 # 0
        years.append(year)
    df['year'] = years


def extract_cars(df, requirement):
    """filter all the cars satisfy the requirement
       requirement: ('price', (50000, 60000))
                    ('distance', (0, 100))
    """
    attribute = requirement[0]
    if attribute == 'price':
        low, high = requirement[1]
    elif attribute == 'distance':
        for item in df.columns:
            if item.startswith('distance_from'):
                attribute = item
                break
        low, high = requirement[1]
    else:
        print("unsupport attribute {}".format(attribute))
        sys.exit(1)
    new_df = df[(df[attribute] >= low) & (df[attribute] <= high)]
    return new_df


def print_df(df):
    """only print the most important info of cars"""
    if df.empty:
        print("Data frame is empty!")
    else:
        print(df[['name', 'price', 'color']].sort_values('price'))


def load_csvfile(csvfile):
    """load csv file to pandas data frame"""
    if not os.path.exists(csvfile):
        print("{} does not exist".format(csvfile))
        sys.exit(1)
    df = pd.read_csv(csvfile)
    return df


def analyze_price(df, plot=False):
    """analyze car price and give a rough idea how expensive the car is"""
    df = df[np.isfinite(df['price'])]
    df = df[df['price'] > 0]
    if plot:
        plt.hist(df['price'].values)
        plt.xlabel('price')
        plt.ylabel('number')
    price_info = df['price'].describe()
    price_info['median'] = df['price'].median()
    return price_info


def print_price_info(price_info, car_info):
    """print price info"""
    maker, model, condition = car_info
    print("Some Price Information ({}-{}-{}):".format(maker, model, condition))
    n = len('median price')
    print("{:s} = $ {:,.2f}".format('min price'.ljust(n), price_info['min']))
    print("{:s} = $ {:,.2f}".format('mean price'.ljust(n), price_info['mean']))
    print("{:s} = $ {:,.2f}".format('median price'.ljust(n), price_info['median']))
    print("{:s} = $ {:,.2f}".format('max price'.ljust(n), price_info['max']))
    print("{:s} = $ {:,.2f}".format('std price'.ljust(n), price_info['std']))


def main():
    """show how to use analyze_price()"""
    if len(sys.argv) != 4:
        print("Usage: >> python {} <csvfile> <min_price> <max_price>".format(sys.argv[0]))
        sys.exit(1)
    csvfile = sys.argv[1]
    min_price, max_price = float(sys.argv[2]), float(sys.argv[3])
    df = load_csvfile(csvfile)
    car_info = extract_info_from_csvfilename(csvfile)
    price_info = analyze_price(df, plot=False)
    print_price_info(price_info, car_info)
    new_df = extract_cars(df, ('price', (min_price, max_price)))
    print_df(new_df)
    add_year_column(df)
    plt.show()

if __name__ == "__main__":
    main()
