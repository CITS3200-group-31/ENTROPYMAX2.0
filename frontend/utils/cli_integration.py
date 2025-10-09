"""
CLI integration for run_entropymax binary.
Handles command construction and execution.
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

from .cache_paths import ensure_cache_root


class CLIIntegration:
    """Handle interaction with run_entropymax CLI"""
    
    def __init__(self, cli_path: Optional[Path] = None):
        """Initialize CLI integration.
        
        Args:
            cli_path: Optional explicit path to CLI binary. If not provided,
                     will look in entro_cache/binary/ directory.
        """
        if cli_path:
            self.cli_path = cli_path
        else:
            # Use binary from cross-platform cache directory
            self.cli_path = ensure_cache_root() / "binary" / "run_entropymax"
        
        if not self.cli_path.exists():
            raise FileNotFoundError(
                f"CLI not found at {self.cli_path}. "
                f"Make sure to call TempFileManager.setup_binary_from_bundle() first."
            )
            
    def run_analysis(self, 
                    input_csv: str, 
                    gps_csv: str,
                    output_csv: str,
                    params: Dict,
                    working_dir: Optional[str] = None) -> Tuple[bool, str]:
        """
        Run CLI analysis
        
        Args:
            input_csv: Path to raw data CSV
            gps_csv: Path to GPS coordinates CSV
            output_csv: Path for output CSV (where to move the CLI output)
            params: Analysis parameters dict
            working_dir: Working directory where CLI will run and create output.csv
                        If None, uses the directory of output_csv
            
        Returns:
            (success: bool, message/error: str)
        """
        # Build command (CLI only accepts input files, not output path)
        # CLI will write to 'output.csv' in working directory
        cmd = [
            str(self.cli_path),
            input_csv,
            gps_csv
        ]
        
        # Add K range parameters
        cmd.extend(['--EM_K_MIN', str(params.get('min_groups', 2))])
        cmd.extend(['--EM_K_MAX', str(params.get('max_groups', 20))])
        
        # Add permutations parameter (CLI expects count, 0 = disabled)
        if 'do_permutations' in params and params['do_permutations']:
            perms = params.get('permutation_count', 100)
        else:
            perms = 0
        cmd.extend(['--permutations', str(perms)])
        
        # Add row proportions (1=enable, 0=disable)
        row_props = '1' if params.get('take_proportions', True) else '0'
        cmd.extend(['--row_proportions', row_props])
        
        # Determine working directory
        if working_dir is None:
            working_dir = str(Path(output_csv).parent)
        
        logger.info(f"Running CLI: {' '.join(cmd)}")
        logger.info(f"Working directory: {working_dir}")
        
        # CLI will write output.csv to working directory
        default_output = Path(working_dir) / "output.csv"
        
        try:
            # Execute CLI with specified working directory
            result = subprocess.run(
                cmd,
                cwd=working_dir,  # Run in writable cache directory
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                # CLI succeeded, now move output.csv to desired location
                if default_output.exists():
                    import shutil
                    shutil.move(str(default_output), output_csv)
                    logger.info(f"CLI analysis completed, output moved to {output_csv}")
                    return True, "Analysis completed successfully"
                else:
                    logger.error(f"CLI succeeded but output file not found at {default_output}")
                    return False, f"CLI output file not found at expected location: {default_output}"
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                logger.error(f"CLI failed with code {result.returncode}: {error_msg}")
                return False, f"CLI error (code {result.returncode}): {error_msg}"
                
        except subprocess.TimeoutExpired:
            logger.error("CLI execution timeout")
            return False, "Analysis timeout (>5 minutes)"
        except Exception as e:
            logger.error(f"CLI execution exception: {e}")
            return False, str(e)
            
