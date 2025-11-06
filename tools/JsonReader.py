import json
import os
from config import BASE_DIR


def load_products(papka, file_json) -> list:
    with open(os.path.join(BASE_DIR, papka, file_json), 'r') as f:
        data = json.load(f)
    print(data)
    return data