import os
import json
import sys

# Add backend directory to path so we can import cyrillic_to_latin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraper import cyrillic_to_latin

def transliterate_db(db_path):
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    print(f"Reading database from {db_path}...")
    with open(db_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return

    if '_default' not in data:
        print("Database schema matches expectations, but '_default' table is missing.")
        return

    default_table = data['_default']
    modified_count = 0

    for key, lead in default_table.items():
        original_category = lead.get('category')
        if original_category:
            converted_category = cyrillic_to_latin(original_category)
            if original_category != converted_category:
                lead['category'] = converted_category
                modified_count += 1

    if modified_count > 0:
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully transliterated {modified_count} categories in the database.")
    else:
        print("No Cyrillic categories found to transliterate.")

if __name__ == '__main__':
    default_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.json')
    db_file = sys.argv[1] if len(sys.argv) > 1 else default_db_path
    transliterate_db(db_file)
