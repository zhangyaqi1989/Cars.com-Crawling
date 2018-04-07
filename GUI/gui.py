#!/usr/bin/env python3
##################################
# University of Wisconsin-Madison
# Author: Yaqi Zhang, Jieru Hu
##################################
# implement a simple GUI for car
# search using TKinter
##################################

import os
import sys
abspath = os.path.abspath(__file__)
dirname = os.path.dirname(abspath)
os.chdir(dirname)
sys.path.insert(0, "../src/")
import csv
from collections import defaultdict
from tkinter import Tk, Label, Button, Message, OptionMenu, StringVar, END, \
        ttk, Entry, IntVar, END, W, E, Radiobutton
from cars_com_crawling import craw_from_url
from handle_search_carscom import generate_url
from utility import user_input, write_cars_to_csv, extract_info_from_csvfilename
from data_analysis import load_csvfile, analyze_price, print_price_info, plot_price_info


class SearchGUI:
    def __init__(self, master):
        self.master = master
        master.title("Cars.com")
        # 1. prepare data
        data_file = "model_codes_carscom.csv"
        self.maker_model_dic = defaultdict(list)
        with open(data_file, 'r') as f:
            reader = csv.DictReader(f)
            for line in reader:
                # brands.add(line['maker'])
                self.maker_model_dic[line['maker']].append(line['model'])
        makers = list(self.maker_model_dic.keys())
        # 2. add widgets
        ## 2.1 maker
        self.maker_label = Label(master, text="Choose Maker: ")
        self.maker_box = ttk.Combobox(master)
        self.maker_box['values'] = (*makers, "Text")
        self.maker_box.current(0)
        self.maker_box.bind("<<ComboboxSelected>>", self.update_model_list)
        # self.maker_box.pack()
        ## 2.2 model
        self.model_label = Label(master, text="Choose Model: ")
        self.models = self.maker_model_dic[self.maker_box.get()]
        # print(self.models)
        self.model_box = ttk.Combobox(master)
        self.model_box['values'] = (*self.models, "Text")
        self.model_box.current(0)
        # self.model_box.pack()
        ## 2.3 Zipcode
        self.zip_label = Label(master, text="Enter Zip: ")
        vcmd = master.register(self.validate)
        self.zip_entry = Entry(master, validate="key", validatecommand=(vcmd, '%P'))
        self.zip_entry.delete(0, END)
        self.zip_entry.insert(0, "53705")
        ## 2.4 radius
        self.radius_label = Label(master, text="Radius (miles): ")
        self.radius_var = IntVar(master)
        self.default_radius = 50
        self.radius_var.set(self.default_radius)
        radius_lst = [25, 50, 100, 200, 250, 500]
        self.radius_menu = OptionMenu(master, self.radius_var, *radius_lst)
        ## 2.5 new and old
        self.condition_var = StringVar()
        self.condition_var.set("new")
        self.new_button = Radiobutton(master, text="New", variable=self.condition_var, value="new")
        self.used_button = Radiobutton(master, text="Used", variable=self.condition_var, value="used")
        self.all_button = Radiobutton(master, text="All", variable=self.condition_var, value="all")
        ## 2.5 output
        ### 2.5.1 mean
        self.mean_label_text = IntVar()
        self.mean = 0
        self.mean_label_text.set(self.mean)
        self.mean_label = Label(master, textvariable=self.mean_label_text)
        self.mean_name_label = Label(master, text="Mean Price ($): ")
        ### 2.5.2 min
        self.min_label_text = IntVar()
        self.min = 0
        self.min_label_text.set(self.min)
        self.min_label = Label(master, textvariable=self.min_label_text)
        self.min_name_label = Label(master, text="Min Price ($): ")
        ### 2.5.3 max
        self.max_label_text = IntVar()
        self.max = 0
        self.max_label_text.set(self.max)
        self.max_label = Label(master, textvariable=self.max_label_text)
        self.max_name_label = Label(master, text="Max Price ($): ")

        self.search_button = Button(master, text="Search", command=self.search)
        self.close_button = Button(master, text="Close", command=master.quit)
        # self.close_button.pack()
        # 3. Layout
        self.maker_label.grid(row=0, column=0, sticky=W)
        self.maker_box.grid(row=0, column=1, columnspan=2)
        self.model_label.grid(row=1, column=0, sticky=W)
        self.model_box.grid(row=1, column=1, columnspan=2)
        self.zip_label.grid(row=2, column=0, sticky=W)
        self.zip_entry.grid(row=2, column=1, columnspan=2, sticky=W+E)
        self.radius_label.grid(row=3, column=0, sticky=W)
        self.radius_menu.grid(row=3, column=1, columnspan=2)
        self.new_button.grid(row=4, column=0, sticky=W+E)
        self.used_button.grid(row=4, column=1, sticky=W+E)
        self.all_button.grid(row=4, column=2, sticky=W+E)
        self.min_name_label.grid(row=5, column=0, sticky=W)
        self.min_label.grid(row=5, column=1, columnspan=2, sticky=W+E)
        self.mean_name_label.grid(row=6, column=0, sticky=W)
        self.mean_label.grid(row=6, column=1, columnspan=2, sticky=W+E)
        self.max_name_label.grid(row=7, column=0, sticky=W)
        self.max_label.grid(row=7, column=1, columnspan=2, sticky=W+E)
        self.search_button.grid(row=8, column=1)
        self.close_button.grid(row=8, column=2)


    def search(self):
        maker = self.maker_box.get()
        model = self.model_box.get()
        zipcode = int(self.zip_entry.get())
        radius = int(self.radius_var.get())
        condition = self.condition_var.get()
        car_json_file = "cars_com_make_model.json"
        directory = "../data/"
        page_num = 1
        num_per_page = 100
        start_url = generate_url(maker, model, zipcode, radius, car_json_file, condition, page_num, num_per_page)
        csv_name = "{}-{}-{:d}-{:d}-{:s}.csv".format(maker, model, zipcode, radius, condition)
        csv_name = os.path.join(directory, csv_name)
        print("crawling {} {} {}...".format(condition, maker, model))
        craw_from_url(start_url, csv_name)
        print("finish crawling...")
        df = load_csvfile(csv_name)
        car_info = extract_info_from_csvfilename(csv_name)
        price_info = analyze_price(df)
        # print_price_info(price_info, car_info)
        self.mean = int(price_info['mean'])
        self.min = int(price_info['min'])
        self.max = int(price_info['max'])
        self.min_label_text.set(self.min)
        self.mean_label_text.set(self.mean)
        self.max_label_text.set(self.max)


    def validate(self, new_text):
        """check whether the input zip code is valid or not"""
        if not new_text:
            self.zipcode = 53705
            return True
        try:
            self.zipcode = int(new_text)
            return True
        except ValueError:
            return False


    def update_model_list(self, *args):
        """update model list according to picked maker"""
        self.models = self.maker_model_dic[self.maker_box.get()]
        self.model_box['values'] = self.models
        self.model_box.current(0)


if __name__ == "__main__":
    root = Tk()
    search_gui = SearchGUI(root)
    root.mainloop()
