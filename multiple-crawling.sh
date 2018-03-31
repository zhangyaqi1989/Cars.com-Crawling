#!/bin/bash
##################################
# University of Wisconsin-Madison
# Author: Yaqi Zhang, Jieru Hu
##################################
# crawl models listed in search-models.txt
# within 100 miles from zip code 53715 
##################################

python src/multiple_craw_test.py search-models.txt 53715 100 new src/cars_com_make_model.json data/
