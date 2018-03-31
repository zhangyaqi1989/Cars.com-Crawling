#!/bin/bash
##################################
# University of Wisconsin-Madison
# Author: Yaqi Zhang, Jieru Hu
##################################
# crawl Audi Q3 within 100 miles 
# from zip code 53715 
##################################

python src/cars_com_crawling.py Audi Q3 53715 100 new src/cars_com_make_model.json data/
