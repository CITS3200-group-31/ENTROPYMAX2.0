"""
Data pipeline for processing CLI output.
Handles CSV to Parquet conversion and data extraction.
"""

import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import logging

# Use teammate's refactored extractor for parquet parsing
from .parquet_extractor import ParquetDataExtractor

logger = logging.getLogger(__name__)


class DataPipeline:
    """Process CSV to Parquet and extract analysis data"""
    
    @staticmethod
    def csv_to_parquet(csv_path: str, parquet_path: str) -> bool:
        """
        Convert CSV to Parquet format
        
        Args:
            csv_path: Path to input CSV
            parquet_path: Path for output Parquet
            
        Returns:
            Success status
        """
        try:
            df = pd.read_csv(csv_path, low_memory=False)
            df.to_parquet(
                parquet_path, 
                index=False, 
                engine='pyarrow',
                compression='snappy'
            )
            logger.info(f"Converted CSV to Parquet: {parquet_path}")
            return True
        except Exception as e:
            logger.error(f"CSV to Parquet conversion failed: {e}")
            return False
            
    @staticmethod
    def extract_analysis_data(parquet_path: str) -> Optional[Dict]:
        """
        Extract analysis summary and grouping data from Parquet file using
        the refactored teammate extractor.
        
        Args:
            parquet_path: Path to Parquet file
            
        Returns:
            Dictionary with k_values, ch_values, rs_values, groupings, optimal_k
        """
        try:
            # Use teammate's extractor for robust column handling
            extractor = ParquetDataExtractor(parquet_path)
            extractor.validate_data()
            
            # Load parquet as dataframe only for metrics (CH, Rs)
            table = pq.read_table(parquet_path)
            df = table.to_pandas()
            
            k_values = sorted(extractor.get_all_k_values())
            analysis_data = {
                'k_values': [],
                'ch_values': [],
                'rs_values': [],
                'groupings': {},
                'optimal_k': None,
                'gps_data': {}
            }
            
            for k in k_values:
                # Append K value
                analysis_data['k_values'].append(int(k))
                
                # Metrics from dataframe (column names expected)
                k_data = df[df['K'] == k]
                first_row = k_data.iloc[0]
                analysis_data['ch_values'].append(float(first_row['Calinski-Harabasz pseudo-F statistic']))
                analysis_data['rs_values'].append(float(first_row['% explained']))
                
                # Groupings and GPS from extractor
                groups: Dict[int, List[str]] = {}
                gps_info = extractor.get_gps_data_for_k(int(k))
                for sample_id, info in gps_info.items():
                    gid = info['group']
                    groups.setdefault(gid, []).append(sample_id)
                
                analysis_data['groupings'][int(k)] = groups
                analysis_data['gps_data'][int(k)] = gps_info
            
            # Determine optimal K by maximum CH
            if analysis_data['ch_values']:
                ch_array = np.array(analysis_data['ch_values'])
                optimal_idx = np.argmax(ch_array)
                analysis_data['optimal_k'] = analysis_data['k_values'][optimal_idx]
                logger.info(f"Optimal K determined: {analysis_data['optimal_k']}")
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            return None
            
    @staticmethod
    def extract_group_details(parquet_path: str, k_value: int) -> Optional[Dict]:
        """
        Extract detailed group data for a specific K value using teammate's
        refactored ParquetDataExtractor, which handles variable grain size columns.
        
        Args:
            parquet_path: Path to Parquet file
            k_value: K value to extract
            
        Returns:
            Dictionary with sample data grouped by group ID
        """
        try:
            extractor = ParquetDataExtractor(parquet_path)
            extractor.validate_data()
            
            group_ids = extractor.get_group_ids_for_k(k_value)
            if not group_ids:
                logger.warning(f"No data found for K={k_value}")
                return None
            
            # Build group details structure
            group_details: Dict[int, Dict] = {}
            
            # Use dataframe to get column names and match with extractor's data
            table = pq.read_table(parquet_path)
            df = table.to_pandas()
            
            # Get grain size columns using same logic as extractor:
            # From column 3 (after K, Group, Sample) to column_no - 8 (before statistics and GPS)
            total_cols = len(df.columns)
            grain_start = 3
            val_max = total_cols - 8
            grain_size_cols = list(df.columns[grain_start:val_max])
            
            logger.debug(f"Total columns: {total_cols}, Grain size columns: {len(grain_size_cols)}")
            
            for gid in group_ids:
                samples = []
                for sample in extractor.get_samples_by_group(k_value, gid):
                    samples.append({
                        'name': sample['sample_id'],
                        'values': [float(v.as_py()) if hasattr(v, 'as_py') else float(v) for v in sample['x']]
                    })
                group_details[int(gid)] = {
                    'samples': samples,
                    'x_labels': grain_size_cols,
                    'count': len(samples)
                }
            
            logger.info(f"Extracted group details for K={k_value}: {len(group_details)} groups")
            return group_details
            
        except Exception as e:
            logger.error(f"Group details extraction failed: {e}")
            return None
