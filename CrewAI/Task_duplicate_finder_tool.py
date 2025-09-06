import json
from collections import Counter
from typing import Any
from crewai.tools import tool

@tool("Duplicate Finder Tool")
def duplicate_finder_tool(
    input_file: str,  # Now a required argument
    duplicate_key: str,
    output_file: str, # Now a required argument
    case_sensitive: bool = True,
    strip_whitespace: bool = True
) -> str:
    """Finds duplicates in a JSON file based on a specific key, adds an 'is_duplicate' flag, and saves the result to a new file."""

    # No need to check for 'data' anymore, we always load from a file.
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return f"Error: Failed to load or parse JSON from {input_file}. Details: {e}"

    if not isinstance(data, list):
        return "Error: The JSON file must contain a list of objects."

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

    # Save the results
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return f"Success! Processed {processed} objects. {duplicates_count} duplicates were flagged. The updated data has been saved to {output_file}."
    except Exception as e:
        return f"Error: Failed to write the output to {output_file}. Details: {e}"
