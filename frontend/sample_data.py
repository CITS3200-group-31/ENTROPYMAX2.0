"""
Sample data module for testing the EntropyMax frontend.
Contains pre-loaded test data as Python data structures, simulating data already read from CSV files.
"""

import numpy as np

# Sample input data
SAMPLE_INPUT_DATA = {
    'headers': ['Sample Name'] + [str(x) for x in [
        0.02, 0.023520823, 0.027661457, 0.032531013, 0.038257812, 0.044992763,
        0.052913343, 0.062228271, 0.07318301, 0.086066235, 0.101217438, 0.119035877,
        0.139991095, 0.164635295, 0.193617889, 0.227702614, 0.267787655, 0.314929314,
        0.370369847, 0.435570198, 0.512248497, 0.602425336, 0.708477013, 0.833198154,
        0.979875354, 1.152373784, 1.355239044, 1.593816947, 1.87439439, 2.204365021
    ]],
    'samples': [
        {
            'name': 'Parakeelya_white beach',
            'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        {
            'name': 'A41325G_Q',
            'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        {
            'name': 'A71054_Q',
            'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        {
            'name': 'A11642G_Q',
            'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        {
            'name': 'A71459G_Q',
            'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        {
            'name': 'A50727G_Q',
            'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        {
            'name': 'A80947G_Q',
            'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        {
            'name': 'A71103G_Q',
            'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        {
            'name': 'A51615G_Q',
            'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        {
            'name': 'A71102G_Q',
            'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
    ]
}

# Sample GPS coordinate data
# Simulating data with lat, lon, name, and group assignments
SAMPLE_GPS_DATA = [
    {'lat': -31.9523, 'lon': 115.8613, 'name': 'Parakeelya_white beach', 'group': 1},
    {'lat': -32.1234, 'lon': 115.9876, 'name': 'A41325G_Q', 'group': 1},
    {'lat': -32.4567, 'lon': 116.2345, 'name': 'A71054_Q', 'group': 2},
    {'lat': -33.8610, 'lon': 121.8891, 'name': 'A11642G_Q', 'group': 2},
    {'lat': -35.0270, 'lon': 117.8840, 'name': 'A71459G_Q', 'group': 3},
    {'lat': -34.5678, 'lon': 118.1234, 'name': 'A50727G_Q', 'group': 3},
    {'lat': -31.7890, 'lon': 115.7890, 'name': 'A80947G_Q', 'group': 1},
    {'lat': -32.3456, 'lon': 116.3456, 'name': 'A71103G_Q', 'group': 2},
    {'lat': -33.2345, 'lon': 117.2345, 'name': 'A51615G_Q', 'group': 2},
    {'lat': -34.1234, 'lon': 118.5678, 'name': 'A71102G_Q', 'group': 3},
    {'lat': -28.5234, 'lon': 153.5678, 'name': 'A51523G_Q', 'group': 1},
    {'lat': -27.4718, 'lon': 153.0251, 'name': 'A70715G_Q', 'group': 2},
    {'lat': -33.8688, 'lon': 151.2093, 'name': 'A40817G_Q', 'group': 3},
    {'lat': -37.8136, 'lon': 144.9631, 'name': 'A51607G_Q', 'group': 1},
    {'lat': -31.9505, 'lon': 115.8605, 'name': 'A21107G_Q', 'group': 2},
]

# Sample results data from EntropyMax analysis
# Simulating "GP Result 20240910.csv" format
SAMPLE_RESULTS_DATA = {
    'k2': {  # Results for 2 groups
        'groups': {
            1: ['Parakeelya_white beach', 'A41325G_Q', 'A80947G_Q', 'A51523G_Q', 'A51607G_Q', 'A21107G_Q'],
            2: ['A71054_Q', 'A11642G_Q', 'A71459G_Q', 'A50727G_Q', 'A71103G_Q', 'A51615G_Q', 'A71102G_Q', 'A70715G_Q', 'A40817G_Q']
        },
        'percent_explained': 35.49796,
        'total_inequality': 54.19109,
        'between_inequality': 19.23673,
        'calinski_harabasz': 43.46565
    },
    'k3': {  # Results for 3 groups
        'groups': {
            1: ['A71459G_Q', 'A70715G_Q', 'A31031G_Q', 'A41055G_Q'],
            2: ['A51615G_Q', 'A51523G_Q', 'A31238G_Q', 'A40705G_Q'],
            3: ['Parakeelya_white beach', 'A41325G_Q', 'A71054_Q', 'A11642G_Q']
        },
        'percent_explained': 42.30,
        'total_inequality': 54.19109,
        'between_inequality': 22.92,
        'calinski_harabasz': 52.31
    }
}

# Sample Calinski-Harabasz and Rs data for all k values (2-20)
SAMPLE_CH_RS_DATA = {
    'k_values': np.array(range(2, 21)),
    'ch_values': np.array([
        43.47, 52.31, 48.92, 45.67, 41.23, 38.45, 35.89, 33.12,
        31.45, 29.87, 28.34, 26.91, 25.53, 24.21, 22.95, 21.74,
        20.58, 19.46, 18.39
    ]),
    'rs_values': np.array([
        35.50, 42.30, 46.80, 49.20, 51.10, 52.60, 53.80, 54.70,
        55.40, 56.00, 56.50, 56.90, 57.20, 57.50, 57.70, 57.90,
        58.00, 58.10, 58.20
    ])
}

# Extended GPS data for more realistic map visualization
EXTENDED_GPS_DATA = [
    # Western Australia samples
    {'lat': -31.9523, 'lon': 115.8613, 'name': 'Parakeelya Beach', 'group': 1, 'selected': False},
    {'lat': -32.1234, 'lon': 115.9876, 'name': 'Rockingham', 'group': 1, 'selected': False},
    {'lat': -33.8610, 'lon': 121.8891, 'name': 'Esperance', 'group': 2, 'selected': False},
    {'lat': -35.0270, 'lon': 117.8840, 'name': 'Albany', 'group': 2, 'selected': False},
    {'lat': -34.5678, 'lon': 118.1234, 'name': 'Denmark', 'group': 3, 'selected': False},
    {'lat': -31.7890, 'lon': 115.7890, 'name': 'Fremantle', 'group': 1, 'selected': False},
    {'lat': -32.3456, 'lon': 116.3456, 'name': 'Armadale', 'group': 2, 'selected': False},
    {'lat': -28.7674, 'lon': 114.6089, 'name': 'Geraldton', 'group': 3, 'selected': False},
    {'lat': -24.8843, 'lon': 113.6594, 'name': 'Carnarvon', 'group': 1, 'selected': False},
    {'lat': -26.6103, 'lon': 113.1046, 'name': 'Shark Bay', 'group': 2, 'selected': False},
    # Eastern Australia samples  
    {'lat': -27.4718, 'lon': 153.0251, 'name': 'Brisbane', 'group': 2, 'selected': False},
    {'lat': -28.0167, 'lon': 153.4000, 'name': 'Gold Coast', 'group': 3, 'selected': False},
    {'lat': -33.8688, 'lon': 151.2093, 'name': 'Sydney', 'group': 3, 'selected': False},
    {'lat': -37.8136, 'lon': 144.9631, 'name': 'Melbourne', 'group': 1, 'selected': False},
    {'lat': -34.9285, 'lon': 138.6007, 'name': 'Adelaide', 'group': 2, 'selected': False},
    {'lat': -42.8821, 'lon': 147.3272, 'name': 'Hobart', 'group': 1, 'selected': False},
    {'lat': -41.4545, 'lon': 145.9707, 'name': 'Burnie', 'group': 3, 'selected': False},
    {'lat': -19.2590, 'lon': 146.8169, 'name': 'Townsville', 'group': 2, 'selected': False},
    {'lat': -16.9203, 'lon': 145.7710, 'name': 'Cairns', 'group': 1, 'selected': False},
    {'lat': -12.4634, 'lon': 130.8456, 'name': 'Darwin', 'group': 3, 'selected': False},
]

def get_sample_input_matrix():
    """
    Returns the input data as a NumPy array for analysis.
    """
    matrix = []
    for sample in SAMPLE_INPUT_DATA['samples']:
        matrix.append(sample['data'])
    return np.array(matrix)

def get_sample_names():
    """
    Returns list of sample names.
    """
    return [sample['name'] for sample in SAMPLE_INPUT_DATA['samples']]

def get_selected_samples(indices=None):
    """
    Returns data for selected samples by indices.
    If indices is None, returns all samples.
    """
    if indices is None:
        return SAMPLE_INPUT_DATA['samples']
    return [SAMPLE_INPUT_DATA['samples'][i] for i in indices if i < len(SAMPLE_INPUT_DATA['samples'])]

def get_optimal_k():
    """
    Returns the optimal number of groups based on maximum CH value.
    """
    ch_values = SAMPLE_CH_RS_DATA['ch_values']
    k_values = SAMPLE_CH_RS_DATA['k_values']
    optimal_idx = np.argmax(ch_values)
    return int(k_values[optimal_idx])

if __name__ == "__main__":
    # Test the module
    print("Sample data module loaded successfully")
    print(f"Number of samples: {len(SAMPLE_INPUT_DATA['samples'])}")
    print(f"Number of GPS points: {len(EXTENDED_GPS_DATA)}")
    print(f"Optimal k value: {get_optimal_k()}")
    print(f"Sample names: {get_sample_names()[:5]}...")
