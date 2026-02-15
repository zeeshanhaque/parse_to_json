"""
Script to parse data records and convert them to JSON format.
Each line contains: RITM_number, cat_item, requested_for (name), opened_at, 
sys_updated_on, u_desired_completion_date, and u_requestdetails
"""

import json
import re
from datetime import datetime


def parse_datetime(date_str, time_str):
    """Convert DD/MM/YYYY HH:MM:SS to YYYY/MM/DD HH:MM:SS"""
    day, month, year = date_str.split('/')
    return f"{year}/{month}/{day} {time_str}"


def parse_date(date_str):
    """Convert DD/MM/YYYY to YYYY/MM/DD"""
    day, month, year = date_str.split('/')
    return f"{year}/{month}/{day}"


def extract_files(text):
    """
    Extract .DAT filenames from the request details text.
    Matches patterns like:
    - FILENAME.DAT
    - FILENAME(PARAM=VALUE).EXTENSION.DAT
    - Numbers and special characters in filename
    """
    # Pattern to match .DAT files with various naming conventions
    # This matches any sequence of word characters, hyphens, underscores, parentheses, 
    # dots, and equals signs before .DAT
    pattern = r'[\w\-_]+(?:\([^)]+\))?(?:\.[\w]+)*\.DAT\b'
    files = re.findall(pattern, text, re.IGNORECASE)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for file in files:
        if file.upper() not in seen:
            seen.add(file.upper())
            unique_files.append(file)
    
    return unique_files


def parse_line(line):
    """
    Parse a single line of data.
    Format: RITM# cat_item name datetime1 datetime2 date3 request_text
    """
    line = line.strip()
    if not line:
        return None
    
    # Split the line into parts
    parts = line.split()
    
    if len(parts) < 8:
        print(f"Warning: Skipping malformed line (too few fields): {line[:50]}...")
        return None
    
    # Extract fixed fields
    number = parts[0]
    cat_item_parts = []
    name_parts = []
    
    # Find where cat_item ends (should be "Risk Rolling" based on examples)
    idx = 1
    # Collect cat_item (e.g., "Risk Rolling")
    while idx < len(parts) and not parts[idx].startswith('RITM') and not parts[idx][0].isupper() or parts[idx] in ['Risk', 'Rolling']:
        cat_item_parts.append(parts[idx])
        idx += 1
        if len(cat_item_parts) >= 2:  # "Risk Rolling" is 2 words
            break
    
    cat_item = ' '.join(cat_item_parts)
    
    # Collect name parts (all uppercase words until we hit a date)
    while idx < len(parts) and not re.match(r'\d{2}/\d{2}/\d{4}', parts[idx]):
        name_parts.append(parts[idx])
        idx += 1
    
    requested_for = ' '.join(name_parts)
    
    # Extract dates and times
    if idx + 5 >= len(parts):
        print(f"Warning: Skipping malformed line (missing date fields): {line[:50]}...")
        return None
    
    opened_date = parts[idx]
    opened_time = parts[idx + 1]
    updated_date = parts[idx + 2]
    updated_time = parts[idx + 3]
    completion_date = parts[idx + 4]
    
    # Everything else is the request details
    request_details = ' '.join(parts[idx + 5:])
    
    # Convert dates to required format
    opened_at = parse_datetime(opened_date, opened_time)
    sys_updated_on = parse_datetime(updated_date, updated_time)
    u_desired_completion_date = parse_date(completion_date)
    
    # Extract files from request details
    files = extract_files(request_details)
    
    return {
        "number": number,
        "cat_item": cat_item,
        "requested_for": requested_for,
        "opened_at": opened_at,
        "sys_updated_on": sys_updated_on,
        "u_desired_completion_date": u_desired_completion_date,
        "u_requestdetails": request_details,
        "files": files
    }


def parse_file(input_filename, output_filename=None):
    """
    Parse the input file and convert to JSON format.
    
    Args:
        input_filename: Path to the input data file
        output_filename: Path to the output JSON file (optional)
    
    Returns:
        Dictionary containing the parsed records
    """
    records = []
    
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                record = parse_line(line)
                if record:
                    records.append(record)
    except FileNotFoundError:
        print(f"Error: File '{input_filename}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    result = {"records": records}
    
    # Write to output file if specified
    if output_filename:
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=3)
            print(f"Successfully wrote {len(records)} records to {output_filename}")
        except Exception as e:
            print(f"Error writing output file: {e}")
            return None
    
    return result


def main():
    """Main function to run the script."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python parse_data_to_json.py <input_file> [output_file]")
        print("\nExample:")
        print("  python parse_data_to_json.py data.txt output.json")
        print("  python parse_data_to_json.py data.txt  # prints to stdout")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = parse_file(input_file, output_file)
    
    if result and not output_file:
        # Print to stdout if no output file specified
        print(json.dumps(result, indent=3))


if __name__ == "__main__":
    main()