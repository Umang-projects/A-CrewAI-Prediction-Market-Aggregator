import json
from collections import Counter

def mark_duplicates(data, key='product', case_sensitive=True, strip_whitespace=True):
    def normalize(v):
        if v is None: return None
        if isinstance(v, str):
            nv = v.strip() if strip_whitespace else v
            return nv if case_sensitive else nv.lower()
        try:
            return json.dumps(v, sort_keys=True)
        except:
            return str(v)

    norms = [normalize(item.get(key) if isinstance(item, dict) else None) for item in data]
    freqs = Counter(v for v in norms if v is not None)
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        norm = norms[i]
        item['is_duplicate'] = bool(norm is not None and freqs.get(norm, 0) > 1)
    return data

# load your file
with open('C:/Users/singh/Documents/crewai_project_env/A-CrewAI-Prediction-Market-Aggregator/CrewAI/combined_data.json','r',encoding='utf-8') as f:
    d = json.load(f)
out = mark_duplicates(d, key='product', case_sensitive=False)
with open('C:/Users/singh/Documents/crewai_project_env/A-CrewAI-Prediction-Market-Aggregator/CrewAI/output.json','w',encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

# Print summary
print("Saved output.json; sample duplicates:")
for item in out:
    if isinstance(item, dict) and item.get('is_duplicate'):
        print(item.get('product'))
