"""
Creating Structure from the "entropy-ed" data to be put into the graphs and use on map

Structure Setup:
┌────────────────┐      ┌────────────────────────────────────────────────────────────┐
│                │      │                                                            │
│ No. Groups     │ ────►│Group, x_values[], y_values[] (%), sample_id, lat, long     │
│                │      │                                                            │
└────────────────┘      └────────────────────────────────────────────────────────────┘
Input Parquet Format: group, sample_id, data, total ineq., between region ineq., total sum of squares, within group S.O.S., CH stat, % explained,
                    # samples, k-value (group count), latitude, longitude
"""

import sys
import pyarrow.parquet as pq

# initialise dict
group_data_dict = {}

def create_data(input_file):
    # read in file
    reader = pq.read_table(input_file)
    parquet_file = pq.ParquetFile(input_file)
    print(parquet_file.metadata.num_columns)
    # get locations of columns, adds ability to have a variable amount of x-values
    column_no = parquet_file.metadata.num_columns
    lat_loc = column_no - 2
    long_loc = column_no - 1
    val_max = column_no - 11
    group_loc =  column_no - 3
    # call add_group_data() for each row, inputting the correct column into each item
    for row in range(reader.num_rows):
        add_group_data(reader[group_loc][row].as_py(), reader[0][row].as_py(), [reader[i][row] for i in range(2,val_max)],
                        [reader[i][0] for i in range(2,val_max)], reader[1][row].as_py(), reader[lat_loc][row].as_py(),
                        reader[long_loc][row].as_py())



def add_group_data(group_count, group_index, x, y, sample_id, latitude, longitude):
    # set up structure
    entry = {
        "group": group_index,
        "x": x,
        "y": y,
        "sample_id": sample_id,
        "latitude": latitude,
        "longitude": longitude
    }
    # add new group count (k value) if it doesn't exist yet
    if group_count not in group_data_dict:
        group_data_dict[group_count] = []
    # add sample data
    group_data_dict[group_count].append(entry)


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "frontend/utils/test2.parquet"
    create_data(input_path)
    print({k: len(v) for k, v in group_data_dict.items()})
