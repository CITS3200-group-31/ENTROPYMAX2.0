"""
CSV export utility for analysis results.
"""

import csv
import os
from datetime import datetime


def export_analysis_results(file_path, analysis_data):
    """
    Export analysis results to CSV file.
    
    TODO: Integrate with backend API to fetch complete analysis results
    Backend should provide:
    - Full clustering results for each k value
    - Detailed metrics beyond CH and Rs
    - Sample-to-cluster assignments
    
    Args:
        file_path: Path to save the CSV file
        analysis_data: Dictionary containing analysis results
    
    Returns:
        Path to saved file
    """
    # Ensure .csv extension
    if not file_path.endswith('.csv'):
        file_path += '.csv'
    
    # Create the CSV content
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header information
        writer.writerow(['EntropyMax 2.0 Analysis Results'])
        writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Write analysis parameters
        writer.writerow(['Analysis Parameters'])
        writer.writerow(['Parameter', 'Value'])
        writer.writerow(['Input File', analysis_data.get('input_file', 'N/A')])
        writer.writerow(['Min Groups', analysis_data.get('min_groups', 2)])
        writer.writerow(['Max Groups', analysis_data.get('max_groups', 20)])
        writer.writerow(['Permutations', 'Yes' if analysis_data.get('do_permutations', True) else 'No'])
        writer.writerow(['Row Proportions', 'Yes' if analysis_data.get('take_proportions', False) else 'No'])
        writer.writerow(['Selected Samples', analysis_data.get('num_samples', 0)])
        writer.writerow([])
        
        # Write selected samples
        if 'selected_samples' in analysis_data:
            writer.writerow(['Selected Samples'])
            writer.writerow(['Sample Name', 'Group', 'Latitude', 'Longitude'])
            for sample in analysis_data['selected_samples']:
                writer.writerow([
                    sample.get('name', ''),
                    sample.get('group', ''),
                    sample.get('lat', ''),
                    sample.get('lon', '')
                ])
            writer.writerow([])
        
        # Write CH and Rs results
        writer.writerow(['Analysis Results'])
        writer.writerow(['k', 'CH Index', 'Rs %'])
        
        k_values = analysis_data.get('k_values', [])
        ch_values = analysis_data.get('ch_values', [])
        rs_values = analysis_data.get('rs_values', [])
        optimal_k = analysis_data.get('optimal_k', None)
        
        for k, ch, rs in zip(k_values, ch_values, rs_values):
            row = [int(k), f"{ch:.4f}", f"{rs:.2f}"]
            if k == optimal_k:
                row.append('← Optimal')
            writer.writerow(row)
        
        writer.writerow([])
        
        # Write summary statistics
        writer.writerow(['Summary Statistics'])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Optimal k', optimal_k])
        if optimal_k and len(ch_values) > 0:
            idx = list(k_values).index(optimal_k)
            writer.writerow(['Maximum CH Index', f"{ch_values[idx]:.4f}"])
            writer.writerow(['Rs % at Optimal k', f"{rs_values[idx]:.2f}"])
        
        writer.writerow(['Total Inequality', analysis_data.get('total_inequality', 'N/A')])
        writer.writerow(['Between Group Inequality', analysis_data.get('between_inequality', 'N/A')])
        
    return file_path


def generate_sample_input_csv(file_path):
    """
    Generate a sample input CSV file for testing.
    
    Args:
        file_path: Path where to save the sample CSV
    """
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write headers
        writer.writerow(['name', 'lat', 'lon', 'group', 'value1', 'value2', 'value3'])
        
        # Write sample data
        samples = [
            ['Parakeelya Beach', -31.9523, 115.8613, 1, 0.5, 0.3, 0.2],
            ['Rockingham', -32.1234, 115.9876, 1, 0.4, 0.4, 0.2],
            ['Esperance', -33.8610, 121.8891, 2, 0.3, 0.5, 0.2],
            ['Albany', -35.0270, 117.8840, 2, 0.2, 0.6, 0.2],
            ['Denmark', -34.5678, 118.1234, 3, 0.1, 0.7, 0.2],
            ['Fremantle', -31.7890, 115.7890, 1, 0.6, 0.2, 0.2],
            ['Armadale', -32.3456, 116.3456, 2, 0.3, 0.4, 0.3],
            ['Geraldton', -28.7674, 114.6089, 3, 0.2, 0.5, 0.3],
            ['Carnarvon', -24.8843, 113.6594, 1, 0.4, 0.3, 0.3],
            ['Shark Bay', -26.6103, 113.1046, 2, 0.5, 0.2, 0.3],
        ]
        
        for sample in samples:
            writer.writerow(sample)
    
    return file_path
