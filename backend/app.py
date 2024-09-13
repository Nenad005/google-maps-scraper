from flask import Flask, request, jsonify
from playwright.async_api import async_playwright

app = Flask(__name__)

# Dummy data to simulate a database
leads = []

# Get all leads
@app.route('/leads', methods=['GET'])
def get_leads():
    return jsonify(leads), 200

# Add a new lead
@app.route('/leads', methods=['POST'])
def add_lead():
    new_lead = request.get_json()
    leads.append(new_lead)
    return jsonify({"message": "Lead added successfully"}), 201

# Edit an existing lead
@app.route('/leads/<int:lead_id>', methods=['PUT'])
def edit_lead(lead_id):
    updated_lead = request.get_json()
    for lead in leads:
        if lead['id'] == lead_id:
            lead.update(updated_lead)
            return jsonify({"message": "Lead updated successfully"}), 200
    return jsonify({"message": "Lead not found"}), 404

# Remove a lead
@app.route('/leads/<int:lead_id>', methods=['DELETE'])
def remove_lead(lead_id):
    global leads
    leads = [lead for lead in leads if lead['id'] != lead_id]
    return jsonify({"message": "Lead removed successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
