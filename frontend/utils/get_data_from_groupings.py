"""
Creating dictionary from the "entropy-ed" data to be put into the graphs and use on map

Dictionary Setup:
┌────────────────┐      ┌─────────────────────────────────────────────┐
│                │      │                                             │
│Key: No. Groups │ ────►│Group, x_values[], y_values[] (%), sample_id │
│                │      │                                             │
└────────────────┘      └─────────────────────────────────────────────┘
"""

# import csv
import pyarrow.parquet as pq

group_data_dict = {}

def create_data(input_file):
    reader = pq.read_table(input_file)
    # print(reader)
    i = 1
    # need to figure out how to get group heading
    print(reader.num_rows)
    for row in range(reader.num_rows):
        i = 0
        # currently making all in the grouping number of 2
        add_group_data(2, reader[0][row], [reader[i][row] for i in range(2,70)], [reader[i][0] for i in range(2,70)], reader[1][row])
            

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
    # print(group_data_dict[2][-1])
    

create_data("frontend/utils/data2.parquet")
#print(group_data_dict.keys())