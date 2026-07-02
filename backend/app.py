import os
import random
import queue
import threading
import asyncio
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from tinydb import TinyDB, Query
from scraper import scrape_data, DB_PATH, cyrillic_to_latin

app = Flask(__name__)
# Enable CORS for Next.js frontend (default port is usually 3000)
CORS(app, resources={r"/*": {"origins": "*"}})

Lead = Query()
db_write_lock = threading.Lock()

def get_id():
    with db_write_lock:
        with TinyDB(DB_PATH) as db:
            while True:
                # Generate a 20-digit unique random ID
                new_id = ''.join(str(random.randint(1, 9) if i == 0 else random.randint(0, 9)) for i in range(20))
                if not db.search(Lead.id == new_id):
                    return new_id

# CRUD: Get all leads
@app.route('/leads', methods=['GET'])
def get_leads():
    with db_write_lock:
        with TinyDB(DB_PATH) as db:
            leads = db.all()
    return jsonify(leads), 200

# CRUD: Get single lead (supports both /lead/<id> and /leads/<id>)
@app.route('/lead/<string:lead_id>', methods=['GET'])
@app.route('/leads/<string:lead_id>', methods=['GET'])
def get_lead(lead_id):
    with db_write_lock:
        with TinyDB(DB_PATH) as db:
            results = db.search(Lead.id == lead_id)
            if results:
                return jsonify(results[0]), 200
    return jsonify({"message": "Lead not found"}), 404

# CRUD: Create lead
@app.route('/leads', methods=['POST'])
def add_lead():
    new_lead = request.get_json() or {}
    placeholder = {
        'id': get_id(),
        'gm_url': '',
        'title': '',
        'rating': None,
        'category': None,
        'website': None,
        'phone': None,
        'hours': None,
        'status': 'idle'
    }
    for key in placeholder:
        if key in new_lead:
            placeholder[key] = new_lead[key]

    if not placeholder['title']:
        return jsonify({"message": "Title cannot be empty"}), 400

    # Ensure Cyrillic category is transliterated
    if placeholder['category']:
        placeholder['category'] = cyrillic_to_latin(placeholder['category'])

    with db_write_lock:
        with TinyDB(DB_PATH) as db:
            db.insert(placeholder)

    return jsonify({"message": "Lead added successfully", "lead": placeholder}), 201

# CRUD: Update lead (supports both /lead/<id> and /leads/<id>)
@app.route('/lead/<string:lead_id>', methods=['PUT'])
@app.route('/leads/<string:lead_id>', methods=['PUT'])
def edit_lead(lead_id):
    updated_fields = request.get_json() or {}
    
    # Do not allow modifying the ID
    if 'id' in updated_fields:
        del updated_fields['id']

    # Transliterate category if present in the update
    if 'category' in updated_fields and updated_fields['category']:
        updated_fields['category'] = cyrillic_to_latin(updated_fields['category'])

    with db_write_lock:
        with TinyDB(DB_PATH) as db:
            if db.search(Lead.id == lead_id):
                db.update(updated_fields, Lead.id == lead_id)
                return jsonify({"message": "Lead updated successfully"}), 200
            else:
                return jsonify({"message": "Lead not found"}), 404

# CRUD: Delete lead (supports both /lead/<id> and /leads/<id>)
@app.route('/lead/<string:lead_id>', methods=['DELETE'])
@app.route('/leads/<string:lead_id>', methods=['DELETE'])
def remove_lead(lead_id):
    with db_write_lock:
        with TinyDB(DB_PATH) as db:
            if db.search(Lead.id == lead_id):
                db.remove(Lead.id == lead_id)
                return jsonify({"message": "Lead removed successfully"}), 200
            else:
                return jsonify({"message": "Lead not found"}), 404

# Thread target function to run async scraping logic
def run_scraper_in_thread(query_str: str, limit: int, headless: bool, q: queue.Queue):
    async def run():
        try:
            async for progress in scrape_data(query_str, limit, headless=headless):
                q.put(progress)
        except Exception as e:
            q.put(f"data: [ERROR] - Scraper execution failed: {str(e)}\n")
        finally:
            q.put(None) # Sentinel value to indicate completion

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run())
    loop.close()

# Scraper triggering route with SSE/text streaming
@app.route('/scrape', methods=['GET', 'POST'])
def scrape():
    # Retrieve query parameters or JSON body
    if request.method == 'POST':
        data = request.get_json() or {}
        query = data.get('query', 'laboratorija u beograd')
        limit = data.get('limit', 50)
    else:
        query = request.args.get('query', 'laboratorija u beograd')
        limit = int(request.args.get('limit', 50))

    headless = os.getenv("HEADLESS_SCRAPE", "true").lower() == "true"
    
    q = queue.Queue()
    # Start scraper async runner in a background thread to prevent blocking Flask requests
    threading.Thread(
        target=run_scraper_in_thread, 
        args=(query, limit, headless, q),
        daemon=True
    ).start()

    def generate_responses():
        while True:
            val = q.get()
            if val is None:
                break
            yield val

    return Response(generate_responses(), mimetype='text/plain')

if __name__ == '__main__':
    # Run the server on port 5000 by default (Flask default)
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
