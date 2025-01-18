from flask import Flask, request, jsonify
import pickle
from phe import paillier

# Initialize Flask app
app = Flask(__name__)

# Simulated database
database = ["Record_" + str(i) for i in range(10)]  # For 10 records
database = ["Record_" + str(i) for i in range(100)]  # For 100 records
database = ["Record_" + str(i) for i in range(1000)]  # For 1000 records


# Generate public and private keys for Paillier encryption
public_key, private_key = paillier.generate_paillier_keypair()

# Process the encrypted query
def process_query(encrypted_query):
    encrypted_result = public_key.encrypt(0)  # Start with encrypted zero
    for enc_query_val, record in zip(encrypted_query, database):
        record_size = len(record)  # Simulate data retrieval
        encrypted_result += enc_query_val * record_size  # Homomorphic operation
    return encrypted_result

# PIR endpoint: Process encrypted queries
@app.route('/submit_query', methods=['POST'])
def submit_query():
    try:
        encrypted_query = pickle.loads(request.data)  # Deserialize the query
        encrypted_response = process_query(encrypted_query)  # Process query
        return pickle.dumps(encrypted_response)  # Serialize the response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to provide the public key to the client
@app.route('/get_public_key', methods=['GET'])
def get_public_key():
    try:
        return pickle.dumps(public_key)  # Serialize and return the public key
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Dynamic operations: Add a new record
@app.route('/add_record', methods=['POST'])
def add_record():
    try:
        data = request.json
        new_record = data['record']
        database.append(new_record)
        return jsonify({"status": "success", "message": f"Record '{new_record}' added."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Dynamic operations: Edit an existing record
@app.route('/edit_record/<int:record_id>', methods=['POST'])
def edit_record(record_id):
    try:
        data = request.json
        updated_record = data['record']
        if 0 <= record_id < len(database):
            database[record_id] = updated_record
            return jsonify({"status": "success", "message": f"Record ID {record_id} updated to '{updated_record}'."})
        else:
            return jsonify({"status": "error", "message": "Invalid record ID"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Dynamic operations: Delete a record
@app.route('/delete_record/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    try:
        if 0 <= record_id < len(database):
            deleted_record = database.pop(record_id)
            return jsonify({"status": "success", "message": f"Record '{deleted_record}' deleted."})
        else:
            return jsonify({"status": "error", "message": "Invalid record ID"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Home route
@app.route('/', methods=['GET'])
def home():
    return "Server is running! Use the defined endpoints for PIR or database operations."

# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
