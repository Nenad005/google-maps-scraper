from flask import Flask, request, jsonify
import random
from tinydb import TinyDB, Query
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
Lead = Query()

@app.route('/lead/<string:lead_id>', methods=['GET'])
def get_lead(lead_id):
    with TinyDB('db.json') as db:
        if db.search(Lead.id == lead_id):
            return db.search(Lead.id == lead_id)
    return jsonify({"message": "Lead not found"}), 404

@app.route('/leads', methods=['GET'])
def get_leads():
    with TinyDB('db.json') as db:
        leads = db.all()
    return jsonify(leads), 200

def get_id():
    id = ''
    with TinyDB('db.json') as db:
        for i in range(20):
            id += str(random.randint(1,9) if i == 0 else random.randint(0,9))
        while not db.search(Lead.id == id):
            id = ''
            for i in range(20):
                id += str(random.randint(1,9) if i == 0 else random.randint(0,9))
    return id

@app.route('/leads', methods=['POST'])
def add_lead():
    new_lead = request.get_json()
    placeholder = dict(
        id=get_id(),
        gm_url='',
        title='',
        rating=None,
        category=None,
        website=None,
        phone=None,
        hours=None,
        status='idle'
    )
    for key in new_lead.keys():
        if key in placeholder:
            placeholder[key] = new_lead[key]

    if placeholder['title'] == '':
        return jsonify({"message" : "Title can not be empty"}), 400
    
    with TinyDB('db.json') as db:
        db.insert(placeholder)

    return jsonify({"message": "Lead added successfully"}), 201

@app.route('/leads/<string:lead_id>', methods=['PUT'])
def edit_lead(lead_id):
    updated_lead = request.get_json()
    print(updated_lead)
    with TinyDB('db.json') as db:
        if db.search(Lead.id == lead_id):
            db.update(updated_lead, Lead.id == lead_id)
            return jsonify({"message": "Lead updated successfully"}), 200
        else:
            return jsonify({"message": "Lead not found"}), 404

@app.route('/leads/<string:lead_id>', methods=['DELETE'])
def remove_lead(lead_id):
    with TinyDB('db.json') as db:
        if db.search(Lead.id == lead_id):
            db.remove(Lead.id == lead_id)
        else:
            return jsonify({"message": "Lead not found"}), 404
    return jsonify({"message": "Lead removed successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
