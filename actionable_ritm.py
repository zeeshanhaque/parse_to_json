#!/usr/bin/env python3
"""
Script to filter JSON records based on desired completion dates.
Reads records from a JSON file and writes those with matching dates
(found in open_dates.txt) to valid_ritm.txt.
"""

import json
import sys
from datetime import datetime


def load_open_dates(open_dates_file):
    """
    Load dates from the open_dates.txt file.
    
    Args:
        open_dates_file: Path to the file containing valid dates
        
    Returns:
        Set of date strings in YYYY/MM/DD format
    """
    open_dates = set()
    
    try:
        with open(open_dates_file, 'r', encoding='utf-8') as f:
            for line in f:
                date = line.strip()
                if date:  # Skip empty lines
                    open_dates.add(date)
        
        print(f"Loaded {len(open_dates)} open dates from {open_dates_file}")
        return open_dates
        
    except FileNotFoundError:
        print(f"Error: File '{open_dates_file}' not found.")
        return None
    except Exception as e:
        print(f"Error reading open dates file: {e}")
        return None


def load_json_records(json_file):
    """
    Load records from a JSON file.
    
    Args:
        json_file: Path to the JSON file containing records
        
    Returns:
        List of records or None if error
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = data.get('records', [])
        print(f"Loaded {len(records)} records from {json_file}")
        return records
        
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {json_file}: {e}")
        return None
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return None


def filter_valid_records(records, open_dates):
    """
    Filter records whose u_desired_completion_date is in open_dates.
    
    Args:
        records: List of record dictionaries
        open_dates: Set of valid date strings
        
    Returns:
        List of valid records
    """
    valid_records = []
    
    for record in records:
        completion_date = record.get('u_desired_completion_date', '')
        
        if completion_date in open_dates:
            valid_records.append(record)
    
    return valid_records


def write_valid_records(valid_records, output_file):
    """
    Write valid records to output file in JSON format.
    
    Args:
        valid_records: List of valid record dictionaries
        output_file: Path to the output file
    """
    try:
        output_data = {"records": valid_records}
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=3)
        
        print(f"Successfully wrote {len(valid_records)} valid records to {output_file}")
        
    except Exception as e:
        print(f"Error writing output file: {e}")


def main():
    """Main function to run the script."""
    
    # Default file paths
    json_file = "records.json"
    open_dates_file = "open_dates.txt"
    output_file = "valid_ritm.txt"
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    if len(sys.argv) > 2:
        open_dates_file = sys.argv[2]
    if len(sys.argv) > 3:
        output_file = sys.argv[3]
    
    print(f"Input JSON file: {json_file}")
    print(f"Open dates file: {open_dates_file}")
    print(f"Output file: {output_file}")
    print("-" * 50)
    
    # Load open dates
    open_dates = load_open_dates(open_dates_file)
    if open_dates is None:
        sys.exit(1)
    
    # Load JSON records
    records = load_json_records(json_file)
    if records is None:
        sys.exit(1)
    
    # Filter valid records
    valid_records = filter_valid_records(records, open_dates)
    print(f"Found {len(valid_records)} valid records (out of {len(records)} total)")
    
    # Write valid records to output
    write_valid_records(valid_records, output_file)
    
    # Print summary
    print("-" * 50)
    print("Summary:")
    print(f"  Total records: {len(records)}")
    print(f"  Valid records: {len(valid_records)}")
    print(f"  Invalid records: {len(records) - len(valid_records)}")
    
    # Print details of valid records
    if valid_records:
        print("\nValid RITM numbers:")
        for record in valid_records:
            print(f"  - {record.get('number')} (Date: {record.get('u_desired_completion_date')})")


if __name__ == "__main__":
    main()