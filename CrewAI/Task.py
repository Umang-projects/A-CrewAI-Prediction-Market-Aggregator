# task.py
import json
from collections import Counter
from typing import Any
from crewai.tools import tool  # Import the decorator

@tool("Duplicate Finder Tool")
def duplicate_finder_tool(
    input_file: str = None,
    data: list = None,
    duplicate_key: str = 'product',
    output_file: str = None,
    case_sensitive: bool = True,
    strip_whitespace: bool = True
) -> str:
    """Find duplicates in a JSON list by a specified key, mark with is_duplicate, and save (optional)."""
    
    # Load data if not provided directly
    if data is None:
        if not input_file:
            return "Error: Must provide either 'data' or 'input_file'."
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            return f"Error loading JSON from {input_file}: {e}"
    
    if not isinstance(data, list):
        return "Error: Input data must be a list of objects."
    
    # Normalization function
    def normalize(v: Any) -> Any:
        if v is None:
            return None
        if isinstance(v, str):
            nv = v.strip() if strip_whitespace else v
            return nv if case_sensitive else nv.lower()
        try:
            return json.dumps(v, sort_keys=True)
        except Exception:
            return str(v)
    
    # Calculate frequencies
    norms = [normalize(item.get(duplicate_key) if isinstance(item, dict) else None) for item in data]
    freqs = Counter(v for v in norms if v is not None)
    
    # Mark duplicates
    processed = 0
    duplicates_count = 0
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        norm_val = norms[i]
        is_dup = norm_val is not None and freqs.get(norm_val, 0) > 1
        item['is_duplicate'] = is_dup
        if is_dup:
            duplicates_count += 1
        processed += 1
    
    # Save or return results
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return f"Processed {processed} objects. {duplicates_count} duplicates flagged. Output saved to {output_file}."
        except Exception as e:
            return f"Error writing to {output_file}: {e}"
    else:
        return f"Processed {processed} objects. {duplicates_count} duplicates flagged. Data: {json.dumps(data, indent=2)}"