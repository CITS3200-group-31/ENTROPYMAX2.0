"""
Creating Structure from the "entropy-ed" data to be put into the graphs and use on map

Structure Setup:
┌────────────────┐      ┌─────────────────────────────────────────────┐
│                │      │                                             │
│ No. Groups     │ ────►│Group, x_values[], y_values[] (%), sample_id │
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
        #print(reader[74][row])
        add_group_data(reader[74][row].as_py(), reader[0][row].as_py(), [reader[i][row] for i in range(2,69)], [reader[i][0] for i in range(2,69)], reader[1][row].as_py())

            

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
    

create_data("frontend/utils/test2.parquet") 
print(group_data_dict[16])