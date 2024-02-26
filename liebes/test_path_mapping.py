import json
from pathlib import Path

mapping_config = json.load(open('mapping_config.json', 'r'))

groups = [x for x in mapping_config.keys()]

cache_file = "mapping_cache.json"
mapping_cache = {}
if Path(cache_file).exists():
    mapping_cache = json.load(open(cache_file, 'r'))

updated_number = 0


def update_cache(k, v):
    global updated_number
    mapping_cache[k] = v
    updated_number += 1
    if updated_number % 100 == 0:
        json.dump(mapping_cache, open(cache_file, 'w'))


def has_mapping(test_name):
    if test_name in mapping_cache.keys():
        return mapping_cache[test_name]
    for g in groups:
        if g in test_name:
            for k, v in mapping_config[g].items():
                if k in test_name:
                    update_cache(test_name, v)
                    return v
            return None
    return None
