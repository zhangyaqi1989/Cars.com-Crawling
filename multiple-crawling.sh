#!/bin/bash
##################################
# University of Wisconsin-Madison
# Author: Yaqi Zhang, Jieru Hu
##################################
# crawl models listed in search-models.txt
# within 100 miles from zip code 53715 
##################################

python src/multiple_crawling_test.py search-models-japan-sedan.txt 53715 100 new src/cars_com_make_model.json data/
# python src/multiple_crawling_test.py search-models-germany-suv.txt 53715 100 new src/cars_com_make_model.json data/
