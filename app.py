import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Use Render's connection string
db = SQLAlchemy(app)

# Allow CORS for all routes and origins
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Fixes CORS for all API routes

# Your existing routes below...
# [Keep your existing code for /api/search, /api/add-part, etc.]
# Connect to the database
def get_db_connection():
    conn = sqlite3.connect('parts.db')
    conn.row_factory = sqlite3.Row
    return conn

# Search parts
@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parts WHERE part_number LIKE ? OR part_name LIKE ? OR description LIKE ?", 
                   (f'%{query}%', f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a list of dictionaries
    results = []
    for row in rows:
        results.append({
            "part_number": row[0],
            "part_name": row[1],
            "description": row[2],
            "quantity": row[3],
            "unit_price": row[4],
            "supplier": row[5],
            "lead_time": row[6],
            "notes": row[7]
        })

    return jsonify(results)

# Add a new part
@app.route('/api/add-part', methods=['POST'])
def add_part():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO parts (part_number, part_name, description, quantity, unit_price, supplier, lead_time, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['part_number'],
        data['part_name'],
        data['description'],
        data['quantity'],
        data['unit_price'],
        data['supplier'],
        data['lead_time'],
        data['notes']
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Part added successfully!"})

# Create the parts table if it doesn't exist
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parts (
            part_number VARCHAR(20) PRIMARY KEY,
            part_name VARCHAR(100),
            description TEXT,
            quantity INT,
            unit_price DECIMAL(10, 2),
            supplier VARCHAR(100),
            lead_time INT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Get single part
@app.route('/api/parts/<part_number>', methods=['GET'])
def get_part(part_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parts WHERE part_number = ?", (part_number,))
    part = cursor.fetchone()
    conn.close()

    if part:
        return jsonify(dict(part))
    else:
        return jsonify({"error": "Part not found"}), 404

# Update part
@app.route('/api/parts/<part_number>', methods=['PUT'])
def update_part(part_number):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE parts SET 
            part_name = ?,
            description = ?,
            quantity = ?,
            unit_price = ?,
            supplier = ?,
            lead_time = ?,
            notes = ?
        WHERE part_number = ?
    ''', (
        data['part_name'],
        data['description'],
        data['quantity'],
        data['unit_price'],
        data['supplier'],
        data['lead_time'],
        data['notes'],
        part_number
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Part updated successfully!"})

# Delete part
@app.route('/api/parts/<part_number>', methods=['DELETE'])
def delete_part(part_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM parts WHERE part_number = ?", (part_number,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Part deleted successfully!"}) 

# Search parts for edit page
@app.route('/api/edit/search', methods=['GET'])
def edit_search():
    query = request.args.get('q')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parts WHERE part_number LIKE ? OR part_name LIKE ? OR description LIKE ? OR notes LIKE ?", 
                   (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a list of dictionaries
    results = []
    for row in rows:
        results.append({
            "part_number": row[0],
            "part_name": row[1],
            "description": row[2],
            "quantity": row[3],
            "unit_price": row[4],
            "supplier": row[5],
            "lead_time": row[6],
            "notes": row[7]
        })

    return jsonify(results)    
if __name__ == '__main__':
    initialize_database()  # Ensure the table exists
    app.run(debug=True, port=5000)
