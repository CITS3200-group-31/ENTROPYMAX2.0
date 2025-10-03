"""
Parquet Data Extractor Module
Original design by teammate - refactored for production use

Creating Structure from the "entropy-ed" data to be put into the graphs and use on map

Structure Setup:
┌────────────────┐      ┌────────────────────────────────────────────────────────────┐
│                │      │                                                            │
│ No. Groups     │ ────►│Group, x_values[], y_values[] (%), sample_id, lat, long     │
│                │      │                                                            │
└────────────────┘      └────────────────────────────────────────────────────────────┘

Input Parquet Format: 
    K, Group, Sample, [grain_size_columns...], 
    % explained, Total inequality, Between region inequality, 
    Total sum of squares, Within group sum of squares, 
    Calinski-Harabasz pseudo-F statistic, Latitude, Longitude
"""

import pyarrow.parquet as pq
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ParquetDataExtractor:
    """
    Extract and organize data from Parquet files.
    
    Uses column position-based access for flexibility with variable grain size columns.
    Original algorithm by teammate, refactored for production use.
    """
    
    def __init__(self, parquet_file_path: str):
        """
        Initialize extractor and load data from Parquet file.
        
        Args:
            parquet_file_path: Path to the Parquet file
        """
        self.parquet_path = parquet_file_path
        self.group_data_dict: Dict[int, List[Dict]] = {}
        self._column_positions = {}
        self._load_data()
    
    def _detect_column_positions(self, parquet_file: pq.ParquetFile) -> None:
        """
        Detect column positions based on Parquet schema.
        Uses relative positioning to handle variable number of grain size columns.
        
        Args:
            parquet_file: PyArrow ParquetFile object
        """
        column_no = parquet_file.metadata.num_columns
        
        # Fixed positions based on actual CLI output format:
        # K, Group, Sample, [grain_sizes...], % explained, Total inequality, 
        # Between region inequality, Total sum of squares, Within group sum of squares, 
        # Calinski-Harabasz pseudo-F statistic, latitude, longitude
        self._column_positions = {
            'k_value': 0,  # K column
            'group_id': 1,  # Group column
            'sample_id': 2,  # Sample column
            'grain_start': 3,  # Grain size data starts at column 3
            'latitude': column_no - 2,  # Second to last column
            'longitude': column_no - 1,  # Last column
            'val_max': column_no - 8  # Last grain size column (before 8 statistics columns)
        }
        
        logger.debug(f"Detected column positions: {self._column_positions}")
    
    def _load_data(self) -> None:
        """
        Load and parse data from Parquet file.
        Populates self.group_data_dict with organized data.
        """
        try:
            reader = pq.read_table(self.parquet_path)
            parquet_file = pq.ParquetFile(self.parquet_path)
            
            # Detect column positions
            self._detect_column_positions(parquet_file)
            
            logger.info(f"Loading data from {self.parquet_path}")
            logger.info(f"Total rows: {reader.num_rows}, Total columns: {parquet_file.metadata.num_columns}")
            
            # Extract data for each row
            pos = self._column_positions
            for row in range(reader.num_rows):
                # Extract K value (group count)
                k_value = reader[pos['k_value']][row].as_py()
                
                # Extract group index
                group_index = reader[pos['group_id']][row].as_py()
                
                # Extract grain size percentage data for this sample
                # x_values contains the percentage values for each grain size bin
                x_values = [reader[i][row] for i in range(pos['grain_start'], pos['val_max'])]
                
                # Extract sample ID
                sample_id = reader[pos['sample_id']][row].as_py()
                
                # Extract GPS coordinates
                latitude = reader[pos['latitude']][row].as_py()
                longitude = reader[pos['longitude']][row].as_py()
                
                # Add to data structure
                self._add_group_data(
                    k_value, group_index, x_values,
                    sample_id, latitude, longitude
                )
            
            logger.info(f"Successfully loaded data for K values: {sorted(self.group_data_dict.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to load data from Parquet: {e}")
            raise
    
    def _add_group_data(self, group_count: int, group_index: int, 
                       x: List, sample_id: str,
                       latitude: float, longitude: float) -> None:
        """
        Add sample data to the group data dictionary.
        
        Args:
            group_count: K value (number of groups)
            group_index: Group ID this sample belongs to
            x: Grain size percentage values (the actual data to plot)
            sample_id: Sample identifier
            latitude: GPS latitude
            longitude: GPS longitude
        """
        entry = {
            "group": group_index,
            "x": x,  # This contains the percentage values for each grain size
            "sample_id": sample_id,
            "latitude": latitude,
            "longitude": longitude
        }
        
        # Initialize list for this K value if it doesn't exist
        if group_count not in self.group_data_dict:
            self.group_data_dict[group_count] = []
        
        # Add sample data
        self.group_data_dict[group_count].append(entry)
    
    def get_data_for_k(self, k_value: int) -> List[Dict]:
        """
        Get all sample data for a specific K value.
        
        Args:
            k_value: K value (number of groups)
            
        Returns:
            List of sample data dictionaries
        """
        return self.group_data_dict.get(k_value, [])
    
    def get_all_k_values(self) -> List[int]:
        """
        Get all available K values.
        
        Returns:
            Sorted list of K values
        """
        return sorted(self.group_data_dict.keys())
    
    def get_samples_by_group(self, k_value: int, group_id: int) -> List[Dict]:
        """
        Get all samples belonging to a specific group within a K value.
        
        Args:
            k_value: K value (number of groups)
            group_id: Group ID
            
        Returns:
            List of sample data for the specified group
        """
        all_data = self.get_data_for_k(k_value)
        return [sample for sample in all_data if sample['group'] == group_id]
    
    def get_group_ids_for_k(self, k_value: int) -> List[int]:
        """
        Get all unique group IDs for a specific K value.
        
        Args:
            k_value: K value (number of groups)
            
        Returns:
            Sorted list of unique group IDs
        """
        all_data = self.get_data_for_k(k_value)
        if not all_data:
            return []
        return sorted(set(sample['group'] for sample in all_data))
    
    def get_gps_data_for_k(self, k_value: int) -> Dict[str, Dict]:
        """
        Get GPS coordinates for all samples at a specific K value.
        
        Args:
            k_value: K value (number of groups)
            
        Returns:
            Dictionary mapping sample_id to GPS and group info:
            {
                'sample_id': {
                    'lat': float,
                    'lon': float,
                    'group': int
                }
            }
        """
        all_data = self.get_data_for_k(k_value)
        gps_data = {}
        
        for sample in all_data:
            gps_data[sample['sample_id']] = {
                'lat': sample['latitude'],
                'lon': sample['longitude'],
                'group': sample['group']
            }
        
        return gps_data
    
    def get_statistics(self, k_value: int) -> Dict:
        """
        Get statistics for a specific K value.
        
        Args:
            k_value: K value (number of groups)
            
        Returns:
            Dictionary with statistics
        """
        all_data = self.get_data_for_k(k_value)
        
        if not all_data:
            return {
                'num_groups': 0,
                'num_samples': 0,
                'samples_per_group': {}
            }
        
        group_ids = self.get_group_ids_for_k(k_value)
        samples_per_group = {}
        
        for group_id in group_ids:
            group_samples = self.get_samples_by_group(k_value, group_id)
            samples_per_group[group_id] = len(group_samples)
        
        return {
            'num_groups': len(group_ids),
            'num_samples': len(all_data),
            'samples_per_group': samples_per_group
        }
    
    def validate_data(self) -> bool:
        """
        Validate that data was loaded correctly.
        
        Returns:
            True if data is valid
            
        Raises:
            ValueError: If data is invalid
        """
        if not self.group_data_dict:
            raise ValueError("No data loaded from Parquet file")
        
        # Check each K value has data
        for k_value, data in self.group_data_dict.items():
            if not data:
                raise ValueError(f"K value {k_value} has no data")
            
            # Check each sample has required fields
            for sample in data:
                required_fields = ['group', 'x', 'sample_id', 'latitude', 'longitude']
                for field in required_fields:
                    if field not in sample:
                        raise ValueError(f"Sample missing required field: {field}")
        
        logger.info("Data validation passed")
        return True


# Convenience function for backward compatibility
def create_data(input_file: str) -> Dict[int, List[Dict]]:
    """
    Legacy function for backward compatibility.
    
    Args:
        input_file: Path to Parquet file
        
    Returns:
        Group data dictionary
    """
    extractor = ParquetDataExtractor(input_file)
    return extractor.group_data_dict
