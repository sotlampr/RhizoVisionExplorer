#!/usr/bin/env python3
"""
Test script for RhizoVision CLI
Tests all argument combinations and validates output

Usage:
    # Test with conda-installed RVE
    python test_rve_cli.py ~/apps/miniforge3/envs/rve/bin/rv
    
    # Test with custom binary and images
    python test_rve_cli.py ./rv --test_images_dir /path/to/imageexamples
    
    # Filter specific tests
    python test_rve_cli.py ~/apps/miniforge3/envs/rve/bin/rv --filter "help"
    
    # Generate detailed report
    python test_rve_cli.py ~/apps/miniforge3/envs/rve/bin/rv --output test_report.json

Expected directory structure for test images:
    imageexamples/
        crowns/          # Whole root images (PNG format)
            crown1.png, crown2.png, crown3.png
        scans/           # Broken root images (JPG format)
            scan1.jpg, scan2.jpg, scan3.jpg
python test_rve_cli.py ./rve /path/to/test/images --output test_report.json

# Filter specific tests
python test_rve_cli.py ./rv /path/to/test/images --filter "help"

"""

import os
import sys
import subprocess
import itertools
import tempfile
import shutil
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import argparse

class RVECliTester:
    def __init__(self, rve_binary: str, test_images_dir: str):
        self.rve_binary = rve_binary
        self.test_images_dir = test_images_dir
        self.temp_dir = None
        self.test_results = []
        
        # Define argument mappings (short -> long)
        self.arg_mappings = {
            # Help and info
            '-h': '--help',
            # Output options
            '-na': '--noappend',
            '-op': '--output_path',
            '-o': '--output',
            # General options
            '-r': '--recursive',
            '-v': '--verbose',
            # Root analysis options
            '-rt': '--roottype',
            '-t': '--threshold',
            '-i': '--invert',
            # Filtering options
            '-kl': '--keeplargest',
            # Smoothing options
            '-s': '--smooth',
            '-st': '--smooththreshold',
            # Analysis options
            '-pt': '--prunethreshold',
            # Processed image options
            '-ch': '--convexhull',
            '-ho': '--holes',
            '-dm': '--distancemap',
            '-ma': '--medialaxis',
            '-mw': '--medialaxiswidth',
            '-to': '--topology',
            '-co': '--contours',
            '-cw': '--contourwidth'
        }
        
        # Define test scenarios
        self.test_scenarios = self._generate_test_scenarios()
    
    def _generate_test_scenarios(self) -> List[Dict[str, Any]]:
        """Generate comprehensive test scenarios"""
        scenarios = []
        
        # 1. Help and version tests
        scenarios.extend([
            {'name': 'help_short', 'args': ['-h'], 'expect_help': True},
            {'name': 'help_long', 'args': ['--help'], 'expect_help': True},
            {'name': 'version', 'args': ['--version'], 'expect_version': True},
            {'name': 'license', 'args': ['--license'], 'expect_license': True},
            {'name': 'credits', 'args': ['--credits'], 'expect_credits': True},
        ])
        
        # 2. Basic processing tests
        scenarios.extend([
            {'name': 'basic_single_crown', 'args': ['test_crown.png'], 'needs_image': True},
            {'name': 'basic_single_scan', 'args': ['test_scan.jpg'], 'needs_image': True},
            {'name': 'basic_crowns_directory', 'args': ['test_images/crowns/'], 'needs_dir': True},
            {'name': 'basic_scans_directory', 'args': ['test_images/scans/'], 'needs_dir': True},
            {'name': 'recursive_short', 'args': ['-r', 'test_images/'], 'needs_dir': True},
            {'name': 'recursive_long', 'args': ['--recursive', 'test_images/'], 'needs_dir': True},
        ])
        
        # 3. Output option tests
        scenarios.extend([
            {'name': 'output_file_short', 'args': ['-o', 'custom.csv', 'test_crown.png'], 'needs_image': True},
            {'name': 'output_file_long', 'args': ['--output', 'custom.csv', 'test_scan.jpg'], 'needs_image': True},
            {'name': 'output_path_short', 'args': ['-op', 'output_dir', 'test_crown.png'], 'needs_image': True, 'needs_output_dir': True},
            {'name': 'output_path_long', 'args': ['--output_path', 'output_dir', 'test_scan.jpg'], 'needs_image': True, 'needs_output_dir': True},
            {'name': 'noappend_short', 'args': ['-na', 'test_crown.png'], 'needs_image': True},
            {'name': 'noappend_long', 'args': ['--noappend', 'test_scan.jpg'], 'needs_image': True},
        ])
        
        # 4. Root analysis tests
        root_types = [('0', 'test_crown.png'), ('1', 'test_scan.jpg')]  # whole roots use crowns, broken roots use scans
        thresholds = ['100', '150', '200']
        for rt, image in root_types:
            for thresh in thresholds:
                scenarios.extend([
                    {'name': f'roottype_{rt}_thresh_{thresh}_short', 'args': ['-rt', rt, '-t', thresh, image], 'needs_image': True},
                    {'name': f'roottype_{rt}_thresh_{thresh}_long', 'args': ['--roottype', rt, '--threshold', thresh, image], 'needs_image': True},
                ])
        
        # 5. Filtering tests
        scenarios.extend([
            {'name': 'keeplargest_short', 'args': ['-kl', 'test_crown.png'], 'needs_image': True},
            {'name': 'keeplargest_long', 'args': ['--keeplargest', 'test_scan.jpg'], 'needs_image': True},
            {'name': 'bgnoise', 'args': ['--bgnoise', 'test_crown.png'], 'needs_image': True},
            {'name': 'fgnoise', 'args': ['--fgnoise', 'test_scan.jpg'], 'needs_image': True},
            {'name': 'bg_fg_noise', 'args': ['--bgnoise', '--bgsize', '0.5', '--fgnoise', '--fgsize', '2.0', 'test_crown.png'], 'needs_image': True},
        ])
        
        # 6. Smoothing tests
        scenarios.extend([
            {'name': 'smooth_short', 'args': ['-s', 'test_crown.png'], 'needs_image': True},
            {'name': 'smooth_long', 'args': ['--smooth', 'test_scan.jpg'], 'needs_image': True},
            {'name': 'smooth_threshold_short', 'args': ['-s', '-st', '3.0', 'test_crown.png'], 'needs_image': True},
            {'name': 'smooth_threshold_long', 'args': ['--smooth', '--smooththreshold', '1.5', 'test_scan.jpg'], 'needs_image': True},
        ])
        
        # 7. Unit conversion tests
        scenarios.extend([
            {'name': 'convert_dpi', 'args': ['--convert', '--factordpi', '300', 'test_crown.png'], 'needs_image': True},
            {'name': 'convert_pixels', 'args': ['--convert', '--factorpixels', '10', 'test_scan.jpg'], 'needs_image': True},
            {'name': 'convert_both_precedence', 'args': ['--convert', '--factordpi', '150', '--factorpixels', '5', 'test_crown.png'], 'needs_image': True},
        ])
        
        # 8. Analysis options tests
        scenarios.extend([
            {'name': 'prune', 'args': ['--prune', 'test_scan.jpg'], 'needs_image': True},
            {'name': 'prune_threshold_short', 'args': ['--prune', '-pt', '5', 'test_scan.jpg'], 'needs_image': True},
            {'name': 'prune_threshold_long', 'args': ['--prune', '--prunethreshold', '10', 'test_scan.jpg'], 'needs_image': True},
        ])
        
        # 9. Diameter ranges tests
        drange_formats = [
            ('1.0,3.0,5.0', 'test_crown.png'),
            ('1.0, 2.0, 3.0', 'test_scan.jpg'),
            ('2.0 ,4.0 ,6.0 ,8.0', 'test_crown.png'),
            ('2.0 ,5.0 , 6.0, 8.0', 'test_crown.png')
        ]
        for drange, image in drange_formats:
            scenarios.append({
                'name': f'dranges_{drange.replace(",", "_").replace(".", "").replace(" ", "").replace('"', '')}',
                'args': ['--dranges', drange, image],
                'needs_image': True
            })
        
        # 10. Output image tests
        scenarios.extend([
            {'name': 'segment', 'args': ['--segment', 'test_crown.png'], 'needs_image': True},
            {'name': 'feature', 'args': ['--feature', 'test_scan.jpg'], 'needs_image': True},
            {'name': 'segment_feature', 'args': ['--segment', '--feature', 'test_crown.png'], 'needs_image': True},
            {'name': 'custom_suffixes', 'args': ['--segment', '--ssuffix', '_segmented', '--feature', '--fsuffix', '_processed', 'test_scan.jpg'], 'needs_image': True},
        ])
        
        # 11. Feature visualization tests (use crowns for whole root features, scans for broken root features)
        scenarios.extend([
            {'name': 'convexhull_short', 'args': ['--feature', '-ch', 'test_crown.png'], 'needs_image': True},
            {'name': 'convexhull_long', 'args': ['--feature', '--convexhull', 'test_crown.png'], 'needs_image': True},
            {'name': 'holes_short', 'args': ['--feature', '-ho', 'test_crown.png'], 'needs_image': True},
            {'name': 'holes_long', 'args': ['--feature', '--holes', 'test_crown.png'], 'needs_image': True},
            {'name': 'distancemap_short', 'args': ['--feature', '-dm', 'test_scan.jpg'], 'needs_image': True},
            {'name': 'distancemap_long', 'args': ['--feature', '--distancemap', 'test_scan.jpg'], 'needs_image': True},
            {'name': 'medialaxis_short', 'args': ['--feature', '-ma', 'test_crown.png'], 'needs_image': True},
            {'name': 'medialaxis_long', 'args': ['--feature', '--medialaxis', 'test_scan.jpg'], 'needs_image': True},
            {'name': 'medialaxis_width_short', 'args': ['--feature', '-ma', '-mw', '5', 'test_crown.png'], 'needs_image': True},
            {'name': 'medialaxis_width_long', 'args': ['--feature', '--medialaxis', '--medialaxiswidth', '2', 'test_scan.jpg'], 'needs_image': True},
            {'name': 'topology_short', 'args': ['--feature', '-to', 'test_crown.png'], 'needs_image': True},
            {'name': 'topology_long', 'args': ['--feature', '--topology', 'test_scan.jpg'], 'needs_image': True},
            {'name': 'contours_short', 'args': ['--feature', '-co', 'test_crown.png'], 'needs_image': True},
            {'name': 'contours_long', 'args': ['--feature', '--contours', 'test_crown.png'], 'needs_image': True},
            {'name': 'contour_width_short', 'args': ['--feature', '-co', '-cw', '2', 'test_crown.png'], 'needs_image': True},
            {'name': 'contour_width_long', 'args': ['--feature', '--contours', '--contourwidth', '3', 'test_crown.png'], 'needs_image': True},
        ])
        
        # 12. Complex combination tests
        scenarios.extend([
            {
                'name': 'complex_whole_root',
                'args': ['-rt', '0', '-t', '180', '--convert', '--factordpi', '300', '--smooth', '-st', '2.5',
                        '--feature', '-ch', '-ho', '-ma', '-co', '--dranges', '1.0,2.5,5.0',
                        '-o', 'whole_roots.csv', '-op', 'output_dir', 'test_crown.png'],
                'needs_image': True,
                'needs_output_dir': True
            },
            {
                'name': 'complex_broken_root',
                'args': ['-rt', '1', '--threshold', '150', '--invert', '--bgnoise', '--bgsize', '1.5',
                        '--fgnoise', '--fgsize', '0.8', '--prune', '-pt', '3',
                        '--segment', '--feature', '-ma', '-dm',
                        '-o', 'broken_analysis.csv', 'test_images/scans/'],
                'needs_dir': True
            },
        ])
        
        # 13. Error condition tests
        scenarios.extend([
            {'name': 'no_input', 'args': [], 'expect_error': True},
            {'name': 'missing_threshold_value', 'args': ['--threshold'], 'expect_error': True},
            {'name': 'missing_output_value', 'args': ['--output'], 'expect_error': True},
            {'name': 'missing_dranges_value', 'args': ['--dranges'], 'expect_error': True},
            {'name': 'unknown_option', 'args': ['--unknown-option', 'test_crown.png'], 'expect_error': True, 'needs_image': True},
            {'name': 'multiple_inputs', 'args': ['test_crown.png', 'test_scan.jpg'], 'expect_error': True, 'needs_image': True},
            {'name': 'invalid_roottype', 'args': ['-rt', '2', 'test_crown.png'], 'expect_error': True, 'needs_image': True},
            {'name': 'invalid_threshold', 'args': ['-t', '300', 'test_scan.jpg'], 'expect_error': True, 'needs_image': True},
        ])
        
        return scenarios
    
    def setup_test_environment(self):
        """Setup temporary test environment"""
        self.temp_dir = tempfile.mkdtemp(prefix='rve_test_')
        
        # Create test images directory structure
        test_images_path = Path(self.temp_dir) / 'test_images'
        test_images_path.mkdir()
        
        crowns_path = test_images_path / 'crowns'
        scans_path = test_images_path / 'scans'
        crowns_path.mkdir()
        scans_path.mkdir()
        
        # Copy test images from the actual location
        if Path(self.test_images_dir).exists():
            # Copy crown images (whole roots)
            crowns_source = Path(self.test_images_dir) / 'crowns'
            if crowns_source.exists():
                for img_file in crowns_source.glob('*.png'):
                    shutil.copy2(img_file, crowns_path)
                    # Copy first crown as test_crown.png for single image tests
                    if not (Path(self.temp_dir) / 'test_crown.png').exists():
                        shutil.copy2(img_file, Path(self.temp_dir) / 'test_crown.png')
            
            # Copy scan images (broken roots)
            scans_source = Path(self.test_images_dir) / 'scans'
            if scans_source.exists():
                for img_file in scans_source.glob('*.jpg'):
                    shutil.copy2(img_file, scans_path)
                    # Copy first scan as test_scan.jpg for single image tests
                    if not (Path(self.temp_dir) / 'test_scan.jpg').exists():
                        shutil.copy2(img_file, Path(self.temp_dir) / 'test_scan.jpg')
        
        # Create output directory
        (Path(self.temp_dir) / 'output_dir').mkdir()
        
        return self.temp_dir
    
    def cleanup_test_environment(self):
        """Cleanup temporary test environment"""
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def run_command(self, args: List[str], cwd: str = None) -> Tuple[int, str, str]:
        """Run RVE command and return (returncode, stdout, stderr)"""
        cmd = [self.rve_binary] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.temp_dir,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    def validate_help_output(self, stdout: str, stderr: str) -> bool:
        """Validate help output contains expected sections"""
        help_text = stdout + stderr
        required_sections = [
            "Usage:",
            "Arguments:",
            "Output Options:",
            "General Options:",
            "Root Analysis Options:",
            "Examples:"
        ]
        return all(section in help_text for section in required_sections)
    
    def validate_version_output(self, stdout: str, stderr: str) -> bool:
        """Validate version output"""
        output = stdout + stderr
        return "RhizoVision Explorer CLI Version" in output
    
    def validate_license_output(self, stdout: str, stderr: str) -> bool:
        """Validate license output"""
        output = stdout + stderr
        return "GPL-3.0" in output
    
    def validate_credits_output(self, stdout: str, stderr: str) -> bool:
        """Validate credits output"""
        output = stdout + stderr
        return "acknowledges the contributions" in output
    
    def validate_csv_output(self, csv_path: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Validate CSV output file"""
        validation = {
            'exists': False,
            'readable': False,
            'has_header': False,
            'has_data': False,
            'column_count': 0,
            'row_count': 0,
            'errors': []
        }
        
        if not Path(csv_path).exists():
            validation['errors'].append(f"CSV file {csv_path} does not exist")
            return validation
        
        validation['exists'] = True
        
        try:
            with open(csv_path, 'r', newline='') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                validation['readable'] = True
                validation['row_count'] = len(rows)
                
                if rows:
                    validation['has_header'] = True
                    validation['column_count'] = len(rows[0])
                    
                    # Check for expected headers
                    header = rows[0]
                    expected_columns = ['File.Name', 'Region.of.Interest']
                    missing_columns = [col for col in expected_columns if col not in header]
                    if missing_columns:
                        validation['errors'].append(f"Missing expected columns: {missing_columns}")
                    
                    if len(rows) > 1:
                        validation['has_data'] = True
                        
                        # Validate data rows
                        for i, row in enumerate(rows[1:], 1):
                            if len(row) != len(header):
                                validation['errors'].append(f"Row {i} has {len(row)} columns, expected {len(header)}")
                
        except Exception as e:
            validation['errors'].append(f"Error reading CSV: {str(e)}")
        
        return validation
    
    def run_single_test(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test scenario"""
        result = {
            'name': scenario['name'],
            'scenario': scenario,
            'success': False,
            'returncode': None,
            'stdout': '',
            'stderr': '',
            'validation': {},
            'errors': [],
            'csv_validation': None
        }
        
        try:
            # Setup scenario-specific requirements
            if scenario.get('needs_output_dir'):
                (Path(self.temp_dir) / 'output_dir').mkdir(exist_ok=True)
            
            # Run command
            returncode, stdout, stderr = self.run_command(scenario['args'])
            result['returncode'] = returncode
            result['stdout'] = stdout
            result['stderr'] = stderr
            
            # Validate based on expected outcome
            if scenario.get('expect_help'):
                result['success'] = returncode == 0 and self.validate_help_output(stdout, stderr)
                result['validation']['help'] = result['success']
            
            elif scenario.get('expect_version'):
                result['success'] = returncode == 0 and self.validate_version_output(stdout, stderr)
                result['validation']['version'] = result['success']
            
            elif scenario.get('expect_license'):
                result['success'] = returncode == 0 and self.validate_license_output(stdout, stderr)
                result['validation']['license'] = result['success']
            
            elif scenario.get('expect_credits'):
                result['success'] = returncode == 0 and self.validate_credits_output(stdout, stderr)
                result['validation']['credits'] = result['success']
            
            elif scenario.get('expect_error'):
                result['success'] = returncode != 0  # Should fail
                result['validation']['error_expected'] = result['success']
            
            else:
                # Normal processing test
                result['success'] = returncode == 0
                result['validation']['process_success'] = result['success']
                
                # Check for CSV output
                csv_files = list(Path(self.temp_dir).glob('*.csv'))
                if csv_files:
                    csv_path = str(csv_files[0])
                    result['csv_validation'] = self.validate_csv_output(csv_path, scenario)
                    result['csv_path'] = csv_path  # Store the CSV path for later comparison
                    
                    # Copy CSV to a permanent location for comparison
                    csv_backup_dir = Path(self.temp_dir) / 'csv_backups'
                    csv_backup_dir.mkdir(exist_ok=True)
                    backup_path = csv_backup_dir / f"{scenario['name']}.csv"
                    shutil.copy2(csv_path, backup_path)
                    result['csv_backup_path'] = str(backup_path)
                    
                    if result['csv_validation']['errors']:
                        result['success'] = False
                        result['errors'].extend(result['csv_validation']['errors'])
            
            # Check for unexpected errors in successful cases
            if result['success'] and not scenario.get('expect_error'):
                if "Error:" in stderr:
                    result['errors'].append("Unexpected error in stderr")
                    result['success'] = False
        
        except Exception as e:
            result['errors'].append(f"Test execution failed: {str(e)}")
            result['success'] = False
        
        return result
    
    def compare_equivalent_scenarios(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compare results from equivalent scenarios (short vs long args)"""
        equivalence_issues = []
        
        # Group scenarios by their equivalent functionality
        equivalent_groups = {}
        for result in results:
            # Create a normalized version of args for comparison
            normalized_args = self.normalize_args(result['scenario']['args'])
            key = tuple(sorted(normalized_args))
            
            if key not in equivalent_groups:
                equivalent_groups[key] = []
            equivalent_groups[key].append(result)
        
        # Compare results within each group
        for group_key, group_results in equivalent_groups.items():
            if len(group_results) > 1:
                # Compare CSV outputs if they exist
                csv_results = [r for r in group_results if r.get('csv_backup_path') and Path(r['csv_backup_path']).exists()]
                if len(csv_results) > 1:
                    base_result = csv_results[0]
                    base_csv_path = base_result['csv_backup_path']
                    
                    for csv_result in csv_results[1:]:
                        compare_csv_path = csv_result['csv_backup_path']
                        
                        # Perform exact CSV comparison
                        comparison = self.compare_csv_files_exact(base_csv_path, compare_csv_path)
                        
                        if not comparison['equivalent']:
                            issue = {
                                'type': 'csv_content_mismatch',
                                'scenarios': [base_result['name'], csv_result['name']],
                                'details': f"CSV content differs: {'; '.join(comparison['differences'][:3])}"  # Show first 3 differences
                            }
                            
                            if comparison['errors']:
                                issue['details'] += f" (Errors: {'; '.join(comparison['errors'])})"
                            
                            equivalence_issues.append(issue)
        
        return equivalence_issues
    
    def normalize_args(self, args: List[str]) -> List[str]:
        """Normalize arguments by converting short forms to long forms"""
        normalized = []
        i = 0
        while i < len(args):
            arg = args[i]
            if arg in self.arg_mappings:
                normalized.append(self.arg_mappings[arg])
            else:
                normalized.append(arg)
            i += 1
        return normalized
    
    def csv_results_equivalent(self, csv1: Dict, csv2: Dict) -> bool:
        """Compare two CSV validation results for equivalence"""
        if csv1['exists'] != csv2['exists']:
            return False
        if not csv1['exists']:  # Both don't exist
            return True
        
        # Compare structure
        if (csv1['column_count'] != csv2['column_count'] or 
            csv1['row_count'] != csv2['row_count']):
            return False
        
        return True
    
    def compare_csv_files_exact(self, csv_path1: str, csv_path2: str) -> Dict[str, Any]:
        """Compare two CSV files for exact content equivalence"""
        comparison = {
            'equivalent': False,
            'structure_match': False,
            'content_match': False,
            'differences': [],
            'errors': []
        }
        
        try:
            # Check if both files exist
            if not Path(csv_path1).exists():
                comparison['errors'].append(f"CSV file {csv_path1} does not exist")
                return comparison
            
            if not Path(csv_path2).exists():
                comparison['errors'].append(f"CSV file {csv_path2} does not exist")
                return comparison
            
            # Read both CSV files
            with open(csv_path1, 'r', newline='') as f1, open(csv_path2, 'r', newline='') as f2:
                reader1 = csv.reader(f1)
                reader2 = csv.reader(f2)
                
                rows1 = list(reader1)
                rows2 = list(reader2)
                
                # Compare structure
                if len(rows1) != len(rows2):
                    comparison['differences'].append(
                        f"Row count mismatch: {len(rows1)} vs {len(rows2)}"
                    )
                    return comparison
                
                if rows1 and rows2 and len(rows1[0]) != len(rows2[0]):
                    comparison['differences'].append(
                        f"Column count mismatch: {len(rows1[0])} vs {len(rows2[0])}"
                    )
                    return comparison
                
                comparison['structure_match'] = True
                
                # Compare headers
                if rows1 and rows2:
                    header1, header2 = rows1[0], rows2[0]
                    if header1 != header2:
                        comparison['differences'].append(
                            f"Header mismatch: {header1} vs {header2}"
                        )
                        return comparison
                
                # Compare data rows
                content_differences = []
                for row_idx, (row1, row2) in enumerate(zip(rows1[1:], rows2[1:]), 1):
                    for col_idx, (val1, val2) in enumerate(zip(row1, row2)):
                        # Try to compare as numbers first (for floating point tolerance)
                        try:
                            num1, num2 = float(val1), float(val2)
                            # Use relative tolerance for floating point comparison
                            if abs(num1 - num2) > max(1e-9 * max(abs(num1), abs(num2)), 1e-12):
                                content_differences.append(
                                    f"Row {row_idx}, Col {col_idx}: {val1} vs {val2} (numeric diff: {abs(num1-num2)})"
                                )
                        except ValueError:
                            # Compare as strings if not numeric
                            if val1.strip() != val2.strip():
                                content_differences.append(
                                    f"Row {row_idx}, Col {col_idx}: '{val1}' vs '{val2}'"
                                )
                
                if content_differences:
                    comparison['differences'].extend(content_differences[:10])  # Limit to first 10 differences
                    if len(content_differences) > 10:
                        comparison['differences'].append(f"... and {len(content_differences) - 10} more differences")
                else:
                    comparison['content_match'] = True
                    comparison['equivalent'] = True
                
        except Exception as e:
            comparison['errors'].append(f"Error comparing CSV files: {str(e)}")
        
        return comparison
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test scenarios"""
        print(f"Setting up test environment...")
        self.setup_test_environment()
        
        print(f"Running {len(self.test_scenarios)} test scenarios...")
        
        results = []
        passed = 0
        failed = 0
        
        for i, scenario in enumerate(self.test_scenarios):
            print(f"[{i+1}/{len(self.test_scenarios)}] Running: {scenario['name']}")
            
            result = self.run_single_test(scenario)
            results.append(result)
            
            if result['success']:
                passed += 1
                print(f"  ✓ PASSED")
            else:
                failed += 1
                print(f"  ✗ FAILED: {'; '.join(result['errors']) if result['errors'] else 'Unknown error'}")
        
        # Compare equivalent scenarios
        print("\nComparing equivalent scenarios...")
        equivalence_issues = self.compare_equivalent_scenarios(results)
        
        # Cleanup
        self.cleanup_test_environment()
        
        summary = {
            'total_tests': len(self.test_scenarios),
            'passed': passed,
            'failed': failed,
            'success_rate': passed / len(self.test_scenarios) * 100,
            'results': results,
            'equivalence_issues': equivalence_issues
        }
        
        return summary
    
    def generate_report(self, summary: Dict[str, Any], output_file: str = None):
        """Generate detailed test report"""
        report = {
            'summary': {
                'total_tests': summary['total_tests'],
                'passed': summary['passed'],
                'failed': summary['failed'],
                'success_rate': summary['success_rate']
            },
            'failed_tests': [],
            'equivalence_issues': summary['equivalence_issues'],
            'detailed_results': []
        }
        
        # Collect failed tests
        for result in summary['results']:
            if not result['success']:
                report['failed_tests'].append({
                    'name': result['name'],
                    'args': result['scenario']['args'],
                    'errors': result['errors'],
                    'returncode': result['returncode'],
                    'stdout': result['stdout'],  # Truncate for readability
                    'stderr': result['stderr'][:500]  # Truncate for readability
                })
            
            # Add to detailed results
            report['detailed_results'].append({
                'name': result['name'],
                'success': result['success'],
                'args': result['scenario']['args'],
                'returncode': result['returncode'],
                'validation': result['validation'],
                'csv_validation': result.get('csv_validation')
            })
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        
        if summary['failed'] > 0:
            print(f"\nFAILED TESTS:")
            for failed_test in report['failed_tests']:
                print(f"  - {failed_test['name']}: {'; '.join(failed_test['errors'])}")
        
        if summary['equivalence_issues']:
            print(f"\nEQUIVALENCE ISSUES:")
            for issue in summary['equivalence_issues']:
                print(f"  - {issue['type']}: {issue['details']}")
                print(f"    Scenarios: {', '.join(issue['scenarios'])}")
        
        # Save detailed report if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nDetailed report saved to: {output_file}")
        
        return report

def main():
    parser = argparse.ArgumentParser(description='Test RhizoVision Explorer CLI')
    parser.add_argument('rve_binary', help='Path to RVE CLI binary (e.g., ~/apps/miniforge3/envs/rve/bin/rve)')
    parser.add_argument('--test_images_dir', 
                       default='~/apps/miniforge3/envs/rve/share/RhizoVisionExplorer/imageexamples',
                       help='Directory containing test images (default: RVE conda package imageexamples)')
    parser.add_argument('--output', '-o', help='Output file for detailed report (JSON)')
    parser.add_argument('--filter', help='Filter tests by name pattern')
    
    args = parser.parse_args()
    
    # Expand user paths
    rve_binary = Path(args.rve_binary).expanduser()
    test_images_dir = Path(args.test_images_dir).expanduser()
    
    # Validate inputs
    if not rve_binary.exists():
        print(f"Error: RVE binary not found: {rve_binary}")
        print("Expected location for conda install: ~/apps/miniforge3/envs/rve/bin/rve")
        sys.exit(1)
    
    if not test_images_dir.exists():
        print(f"Error: Test images directory not found: {test_images_dir}")
        print("Expected structure:")
        print("  imageexamples/")
        print("    crowns/")
        print("      crown1.png, crown2.png, crown3.png")
        print("    scans/")
        print("      scan1.jpg, scan2.jpg, scan3.jpg")
        sys.exit(1)
    
    # Validate directory structure
    crowns_dir = test_images_dir / 'crowns'
    scans_dir = test_images_dir / 'scans'
    
    if not crowns_dir.exists() or not scans_dir.exists():
        print(f"Error: Missing crowns/ or scans/ subdirectories in {test_images_dir}")
        print("Expected structure:")
        print("  imageexamples/")
        print("    crowns/")
        print("    scans/")
        sys.exit(1)
    
    crown_images = list(crowns_dir.glob('*.png'))
    scan_images = list(scans_dir.glob('*.jpg'))
    
    if not crown_images:
        print(f"Error: No PNG images found in {crowns_dir}")
        sys.exit(1)
    
    if not scan_images:
        print(f"Error: No JPG images found in {scans_dir}")
        sys.exit(1)
    
    print(f"Found {len(crown_images)} crown images and {len(scan_images)} scan images")
    
    # Create tester and run tests
    tester = RVECliTester(str(rve_binary), str(test_images_dir))
    
    # Filter tests if requested
    if args.filter:
        tester.test_scenarios = [s for s in tester.test_scenarios if args.filter in s['name']]
        print(f"Filtered to {len(tester.test_scenarios)} tests matching '{args.filter}'")
    
    # Run tests
    summary = tester.run_all_tests()
    
    # Generate report
    report = tester.generate_report(summary, args.output)
    
    # Exit with error code if tests failed
    sys.exit(0 if summary['failed'] == 0 else 1)

if __name__ == '__main__':
    main()
