import csv
import json
from crewai.tools import tool


@tool("JSON to CSV Converter Tool")
def json_to_csv_converter_tool(input_file: str, output_file: str) -> str:
    """
    Converts a JSON file containing a list of objects into a CSV file.
    This tool intelligently handles objects with different structures,
    ensuring all data, including error messages, is captured.
    """
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not isinstance(data, list) or len(data) == 0:
            return "Error: JSON data must be a non-empty list of objects."
            
        # ✅ This is the key logic: It scans ALL objects to find every possible header
        all_headers = set()
        for item in data:
            if isinstance(item, dict):
                all_headers.update(item.keys())
        
        # Use a sorted list of headers for consistent column order
        fieldnames = sorted(list(all_headers))
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data) # DictWriter automatically handles missing keys in any given row
            
        return f"Success! The file {input_file} has been robustly converted to CSV and saved as {output_file}."
        
    except FileNotFoundError:
        return f"Error: The input file {input_file} was not found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"