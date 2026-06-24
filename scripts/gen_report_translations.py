"""
Parse INDUSTRY_REPORTS dict with ast.literal_eval, add _en/_vi/_ms
for ALL string values, then write back as JSON.
"""

import ast, json, sys, math

path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Locate INDUSTRY_REPORTS = { ... }
start_tag = 'INDUSTRY_REPORTS = {'
start_idx = content.index(start_tag)
brace_idx = content.index('{', start_idx)

# Parse the dict using ast
# Find the matching closing brace
depth = 0
end_idx = brace_idx
for i in range(brace_idx, len(content)):
    if content[i] == '{': depth += 1
    elif content[i] == '}':
        depth -= 1
        if depth == 0:
            end_idx = i
            break

dict_src = content[brace_idx:end_idx+1]
data = ast.literal_eval(dict_src)

EXCLUDE_KEYS = {'icon', 'module', 'amount', 'total_investment', 'annual_savings', 'roi_percent', 'payback_months', 'before', 'after', 'improvement'}

def add_lang_variants(obj):
    """Recursively add _en, _vi, _ms for every string value in dicts."""
    if isinstance(obj, dict):
        keys_to_add = {}
        for k, v in obj.items():
            if isinstance(v, str) and k not in EXCLUDE_KEYS and not k.endswith(('_en', '_vi', '_ms')):
                if f'{k}_en' not in obj and f'{k}_vi' not in obj and f'{k}_ms' not in obj:
                    keys_to_add[f'{k}_en'] = v
                    keys_to_add[f'{k}_vi'] = v
                    keys_to_add[f'{k}_ms'] = v
        obj.update(keys_to_add)
        for v in obj.values():
            add_lang_variants(v)
    elif isinstance(obj, list):
        for item in obj:
            add_lang_variants(item)

add_lang_variants(data)

# Convert back to JSON with nice formatting
json_str = json.dumps(data, indent=4, ensure_ascii=False)

# Reconstruct the file: replace the dict portion
new_content = content[:brace_idx] + json_str + content[end_idx+1:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

# Count total added fields
def count_added(obj):
    n = 0
    if isinstance(obj, dict):
        for k in obj:
            if k.endswith(('_en', '_vi', '_ms')):
                base = k[:-3]
                if base in obj and isinstance(obj[base], str):
                    n += 1
        for v in obj.values():
            n += count_added(v)
    elif isinstance(obj, list):
        for item in obj:
            n += count_added(item)
    return n

total = count_added(data)
print(f"Done. Total {total} _en/_vi/_ms fields in dict.")
