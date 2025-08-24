"""
Creating dictionary from the "entropy-ed" data to be put into the graphs and use on map

Dictionary Setup:
┌────────────────┐      ┌─────────────────────────────────────────────┐
│                │      │                                             │
│Key: No. Groups │ ────►│Group, x_values[], y_values[] (%), sample_id │
│                │      │                                             │
└────────────────┘      └─────────────────────────────────────────────┘
"""

import csv

group_data_dict = {}

def create_data(input_file):
    with open(input_file, newline = '', encoding = 'utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        next(reader)
        next(reader)
        next(reader)
        next(reader)
        headers = next(reader)
        i = 1
        # need to figure out how to get group headings
        for row in reader:
            if len(row) < 74: continue
            i = 0
            add_group_data(2, row[0], row[1:73], headers[1:73], row[1])
            

def add_group_data(group_count, group_index, x, y, sample_id):
    entry = {
        "group": group_index,
        "x": x,
        "y": y,
        "sample_id": sample_id
    }
    if group_count not in group_data_dict:
        group_data_dict[group_count] = []
    group_data_dict[group_count].append(entry)
    

create_data("example_data.csv.csv")
print(group_data_dict.keys())