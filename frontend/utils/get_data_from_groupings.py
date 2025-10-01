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
    # Read table
    table = pq.read_table(input_file)
    cols = table.column_names

    # Resolve column indices by name (schema can vary by input)
    def find_idx(name: str) -> int:
        try:
            return cols.index(name)
        except ValueError:
            return -1

    idx_group = find_idx("Group")
    idx_sample = find_idx("Sample")
    idx_k = find_idx("K")
    idx_lat = find_idx("latitude")
    idx_lon = find_idx("longitude")

    # Metrics start at the first known metric column; bins are between Sample and metrics
    metric_candidates = [
        "% explained",
        "Total inequality",
        "Between region inequality",
        "Total sum of squares",
        "Within group sum of squares",
        "Calinski-Harabasz pseudo-F statistic",
    ]
    metric_indices = [find_idx(m) for m in metric_candidates if find_idx(m) >= 0]
    idx_metrics_start = min(metric_indices) if metric_indices else idx_k if idx_k >= 0 else len(cols)

    # Bin columns follow Sample and precede metrics
    if idx_sample < 0 or idx_metrics_start <= idx_sample + 1:
        bin_indices = []
    else:
        bin_indices = list(range(idx_sample + 1, idx_metrics_start))

    # X values are the bin headers; convert to float where possible
    x_values = []
    for bi in bin_indices:
        name = cols[bi]
        try:
            x_values.append(float(name))
        except Exception:
            x_values.append(name)

    num_rows = table.num_rows
    # Access columns once for speed
    col_group = table.column(idx_group) if idx_group >= 0 else None
    col_sample = table.column(idx_sample) if idx_sample >= 0 else None
    col_k = table.column(idx_k) if idx_k >= 0 else None
    col_lat = table.column(idx_lat) if idx_lat >= 0 else None
    col_lon = table.column(idx_lon) if idx_lon >= 0 else None

    for row in range(num_rows):
        group_count = col_k[row].as_py() if col_k is not None else None
        group_index = col_group[row].as_py() if col_group is not None else None
        sample_id = col_sample[row].as_py() if col_sample is not None else None
        lat_val = col_lat[row].as_py() if col_lat is not None else None
        lon_val = col_lon[row].as_py() if col_lon is not None else None

        # Y values are the row's data across bin columns
        y_values = [table.column(bi)[row].as_py() for bi in bin_indices]

        add_group_data(group_count, group_index, x_values, y_values, sample_id, lat_val, lon_val)



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
