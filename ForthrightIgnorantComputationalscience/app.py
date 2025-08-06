from flask import Flask, render_template, request, jsonify, flash, send_file, redirect, url_for, session
import json
import os
import pandas as pd
from datetime import datetime
from difflib import SequenceMatcher
import tempfile
import zipfile
import io

app = Flask(__name__)
app.secret_key = 'tc-hub-assist-secure-key-2024-v1.0-production'

# File paths
CUSTOMERS_FILE = 'customers.json'
RESTRICTED_PARTIES_FILE = 'restricted_parties.json'
MATCHES_FILE = 'matches.json'

# Helper function to load data from JSON files
def load_data(filename: str) -> list:
    """Loads data from a JSON file, returns an empty list if file not found or invalid."""
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                # Ensure data is always a list, even if the file contains a single object or is empty
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

# Helper function to save data to JSON files
def save_data(data: list, filename: str):
    """Saves data to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)

# Initialize data files if they don't exist
def initialize_data_files():
    if not os.path.exists(CUSTOMERS_FILE):
        save_data([], CUSTOMERS_FILE)
    if not os.path.exists(RESTRICTED_PARTIES_FILE):
        save_data([], RESTRICTED_PARTIES_FILE)
    if not os.path.exists(MATCHES_FILE):
        save_data([], MATCHES_FILE)

initialize_data_files()

# --- Tool Functionality ---

def calculate_similarity(name1: str, name2: str) -> float:
    """Calculates the similarity ratio between two names."""
    return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

# --- Authentication Functions ---
def is_authenticated():
    return session.get('authenticated') == True and session.get('user_id') == 'tchub'

# --- Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()

        if user_id.lower() == 'tchub':
            session['authenticated'] = True
            session['user_id'] = 'tchub'
            flash('Successfully logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not is_authenticated():
        return redirect(url_for('login'))
    customers = load_data(CUSTOMERS_FILE)
    restricted_parties = load_data(RESTRICTED_PARTIES_FILE)
    matches = load_data(MATCHES_FILE)

    return render_template('index.html',
                         customers_count=len(customers),
                         restricted_parties_count=len(restricted_parties),
                         matches_count=len(matches))

@app.route('/customers')
def customers():
    if not is_authenticated():
        return redirect(url_for('login'))
    customers = load_data(CUSTOMERS_FILE)
    return render_template('customers.html', customers=customers)

@app.route('/restricted-parties')
def restricted_parties():
    if not is_authenticated():
        return redirect(url_for('login'))
    restricted_parties_data = load_data(RESTRICTED_PARTIES_FILE)
    print(f"Loaded {len(restricted_parties_data)} restricted parties")  # Debug log
    return render_template('restricted_parties.html', restricted_parties=restricted_parties_data)

@app.route('/search')
def search():
    if not is_authenticated():
        return redirect(url_for('login'))
    try:
        customers = load_data(CUSTOMERS_FILE)
        restricted_parties = load_data(RESTRICTED_PARTIES_FILE)
        return render_template('search.html', customers=customers, restricted_parties=restricted_parties)
    except Exception as e:
        flash(f'Error loading data: {str(e)}', 'error')
        return render_template('search.html', customers=[], restricted_parties=[])

@app.route('/comments')
def comments():
    if not is_authenticated():
        return redirect(url_for('login'))
    comments_data = [
        {"code": "C1", "description": "Customer cleared after manual review - no match found in current sanctions lists"},
        {"code": "C2", "description": "Customer name similar to restricted party but different entity confirmed through documentation"},
        {"code": "C3", "description": "False positive - customer operates in different jurisdiction with clear business purpose"},
        {"code": "C4", "description": "Enhanced due diligence completed - customer approved for transaction"},
        {"code": "C5", "description": "Customer provides satisfactory explanation and supporting documentation"},
        {"code": "NM", "description": "No Match - Customer name does not appear on any restricted party lists"},
        {"code": "PM", "description": "Possible Match - Requires further investigation and documentation"},
        {"code": "CM", "description": "Close Match - Enhanced due diligence required before proceeding"},
        {"code": "EM", "description": "Exact Match - Transaction blocked pending compliance review"}
    ]
    return render_template('comments.html', comments=comments_data)

@app.route('/country-codes')
def country_codes():
    if not is_authenticated():
        return redirect(url_for('login'))
    # Sample country codes - in production, this would come from a database
    country_codes = [
        {"code": "US", "name": "United States", "region": "North America"},
        {"code": "CA", "name": "Canada", "region": "North America"},
        {"code": "GB", "name": "United Kingdom", "region": "Europe"},
        {"code": "DE", "name": "Germany", "region": "Europe"},
        {"code": "FR", "name": "France", "region": "Europe"},
        {"code": "JP", "name": "Japan", "region": "Asia"},
        {"code": "CN", "name": "China", "region": "Asia"},
        {"code": "IN", "name": "India", "region": "Asia"},
        {"code": "AU", "name": "Australia", "region": "Oceania"},
        {"code": "BR", "name": "Brazil", "region": "South America"},
        {"code": "MX", "name": "Mexico", "region": "North America"},
        {"code": "IT", "name": "Italy", "region": "Europe"},
        {"code": "ES", "name": "Spain", "region": "Europe"},
        {"code": "RU", "name": "Russia", "region": "Europe/Asia"},
        {"code": "KR", "name": "South Korea", "region": "Asia"},
        {"code": "SG", "name": "Singapore", "region": "Asia"},
        {"code": "AE", "name": "United Arab Emirates", "region": "Middle East"},
        {"code": "SA", "name": "Saudi Arabia", "region": "Middle East"},
        {"code": "ZA", "name": "South Africa", "region": "Africa"},
        {"code": "EG", "name": "Egypt", "region": "Africa"}
    ]
    return render_template('country_codes.html', country_codes=country_codes)

# --- API Endpoints ---

@app.route('/api/customers', methods=['GET', 'POST'])
def api_customers():
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    if request.method == 'POST':
        data = request.get_json()
        customers = load_data(CUSTOMERS_FILE)
        # Use max ID + 1 to ensure unique IDs
        new_id = max([c.get('id', 0) for c in customers], default=0) + 1

        customer = {
            'id': new_id,
            'name': data.get('name', '').strip(),
            'address': data.get('address', '').strip(),
            'phone': data.get('phone', '').strip(),
            'email': data.get('email', '').strip(),
            'comments': data.get('comments', '').strip(),
            'created_date': datetime.now().isoformat()
        }

        customers.append(customer)
        save_data(customers, CUSTOMERS_FILE)
        return jsonify({'message': 'Customer added successfully', 'customer': customer})
    else:
        return jsonify(load_data(CUSTOMERS_FILE))

@app.route('/api/customers/<int:customer_id>', methods=['GET', 'PUT', 'DELETE'])
def api_customer(customer_id):
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    customers = load_data(CUSTOMERS_FILE)
    customer = next((c for c in customers if c['id'] == customer_id), None)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    if request.method == 'GET':
        return jsonify(customer)
    elif request.method == 'PUT':
        data = request.get_json()
        customer.update({
            'name': data.get('name', customer['name']).strip(),
            'address': data.get('address', customer['address']).strip(),
            'phone': data.get('phone', customer['phone']).strip(),
            'email': data.get('email', customer['email']).strip(),
            'comments': data.get('comments', customer['comments']).strip(),
            'modified_date': datetime.now().isoformat()
        })
        save_data(customers, CUSTOMERS_FILE)
        return jsonify({'message': 'Customer updated successfully', 'customer': customer})
    elif request.method == 'DELETE':
        customers = [c for c in customers if c['id'] != customer_id]
        save_data(customers, CUSTOMERS_FILE)
        return jsonify({'message': 'Customer deleted successfully'})

@app.route('/api/restricted-parties', methods=['GET', 'POST'])
def api_restricted_parties():
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    if request.method == 'POST':
        data = request.get_json()
        parties = load_data(RESTRICTED_PARTIES_FILE)
        # Use max ID + 1 to ensure unique IDs
        new_id = max([p.get('id', 0) for p in parties], default=0) + 1

        party = {
            'id': new_id,
            'name': data.get('name', '').strip(),
            'reason': data.get('reason', '').strip(),
            'source': data.get('source', '').strip(),
            'comments': data.get('comments', '').strip(),
            'created_date': datetime.now().isoformat()
        }

        parties.append(party)
        save_data(parties, RESTRICTED_PARTIES_FILE)
        return jsonify({'message': 'Restricted party added successfully', 'party': party})
    else:
        return jsonify(load_data(RESTRICTED_PARTIES_FILE))

@app.route('/api/restricted-parties/<int:party_id>', methods=['GET', 'PUT', 'DELETE'])
def api_restricted_party(party_id):
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    parties = load_data(RESTRICTED_PARTIES_FILE)
    party = next((p for p in parties if p['id'] == party_id), None)

    if not party:
        return jsonify({'error': 'Restricted party not found'}), 404

    if request.method == 'GET':
        return jsonify(party)
    elif request.method == 'PUT':
        data = request.get_json()
        party.update({
            'name': data.get('name', party['name']).strip(),
            'reason': data.get('reason', party['reason']).strip(),
            'source': data.get('source', party['source']).strip(),
            'comments': data.get('comments', party['comments']).strip(),
            'modified_date': datetime.now().isoformat()
        })
        save_data(parties, RESTRICTED_PARTIES_FILE)
        return jsonify({'message': 'Restricted party updated successfully', 'party': party})
    elif request.method == 'DELETE':
        parties = [p for p in parties if p['id'] != party_id]
        save_data(parties, RESTRICTED_PARTIES_FILE)
        return jsonify({'message': 'Restricted party deleted successfully'})

@app.route('/api/upload-customers', methods=['POST'])
def upload_customers():
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        df = pd.read_excel(file)
        customers = load_data(CUSTOMERS_FILE)
        imported_count = 0

        max_id = max([c.get('id', 0) for c in customers], default=0)

        for index, row in df.iterrows():
            name = str(row.get('Name', '')).strip() if pd.notna(row.get('Name')) else ''
            if name:
                max_id += 1
                customer = {
                    'id': max_id,
                    'name': name,
                    'address': str(row.get('Address', '')).strip() if pd.notna(row.get('Address')) else '',
                    'phone': str(row.get('Phone', '')).strip() if pd.notna(row.get('Phone')) else '',
                    'email': str(row.get('Email', '')).strip() if pd.notna(row.get('Email')) else '',
                    'comments': str(row.get('Comments', '')).strip() if pd.notna(row.get('Comments')) else '',
                    'created_date': datetime.now().isoformat()
                }
                customers.append(customer)
                imported_count += 1

        save_data(customers, CUSTOMERS_FILE)
        return jsonify({'message': f'Successfully imported {imported_count} customers', 'imported_count': imported_count})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-restricted-parties', methods=['POST'])
def upload_restricted_parties():
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        df = pd.read_excel(file)
        parties = load_data(RESTRICTED_PARTIES_FILE)
        imported_count = 0

        max_id = max([p.get('id', 0) for p in parties], default=0)

        for index, row in df.iterrows():
            name = str(row.get('Name', '')).strip() if pd.notna(row.get('Name')) else ''
            if name:
                max_id += 1
                party = {
                    'id': max_id,
                    'name': name,
                    'reason': str(row.get('Reason', '')).strip() if pd.notna(row.get('Reason')) else '',
                    'source': str(row.get('Source', '')).strip() if pd.notna(row.get('Source')) else '',
                    'comments': str(row.get('Comments', '')).strip() if pd.notna(row.get('Comments')) else '',
                    'created_date': datetime.now().isoformat()
                }
                parties.append(party)
                imported_count += 1

        save_data(parties, RESTRICTED_PARTIES_FILE)
        return jsonify({'message': f'Successfully imported {imported_count} restricted parties', 'imported_count': imported_count})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/screen', methods=['POST'])
def run_screening():
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    customers = load_data(CUSTOMERS_FILE)
    restricted_parties = load_data(RESTRICTED_PARTIES_FILE)

    matches = []

    # Find exact matches first
    for customer in customers:
        for party in restricted_parties:
            similarity = calculate_similarity(customer['name'], party['name'])
            if similarity >= 0.3:  # 30% threshold for similar matches
                match_type = 'exact' if similarity == 1.0 else 'similar'
                matches.append({
                    'customer': customer,
                    'restricted_party': party,
                    'similarity': similarity,
                    'match_type': match_type,
                    'match_date': datetime.now().isoformat()
                })

    # Sort matches by similarity (highest first)
    matches.sort(key=lambda x: x['similarity'], reverse=True)

    # Save matches
    save_data(matches, MATCHES_FILE)

    return jsonify({
        'matches': matches,
        'total_matches': len(matches),
        'exact_matches': len([m for m in matches if m['match_type'] == 'exact']),
        'similar_matches': len([m for m in matches if m['match_type'] == 'similar'])
    })

@app.route('/download/<data_type>')
def download_data(data_type):
    try:
        if data_type == 'customers':
            return send_file('customers.json', as_attachment=True, download_name='customers.json')
        elif data_type == 'restricted-parties':
            return send_file('restricted_parties.json', as_attachment=True, download_name='restricted_parties.json')
        elif data_type == 'matches':
            return send_file('matches.json', as_attachment=True, download_name='matches.json')
        elif data_type == 'project-zip':
            return create_project_zip()
        elif data_type == 'standalone':
            return send_file('standalone_tool.py', as_attachment=True, download_name='TC_HUB_Assist_Standalone.py')
        else:
            return "Invalid data type", 404
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

@app.route('/api/download-selected-customers', methods=['POST'])
def download_selected_customers():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    selected_ids = request.form.getlist('selected_ids')
    if not selected_ids:
        return "No customers selected", 400
    
    try:
        customers = load_data(CUSTOMERS_FILE)
        selected_customers = [c for c in customers if str(c.get('id')) in selected_ids]
        
        if not selected_customers:
            return "No matching customers found", 404
        
        # Create DataFrame
        df = pd.DataFrame(selected_customers)
        
        # Create Excel file in memory
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Selected_Customers', index=False)
        
        excel_buffer.seek(0)
        
        return send_file(
            io.BytesIO(excel_buffer.read()),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'selected_customers_{len(selected_customers)}_records.xlsx'
        )
        
    except Exception as e:
        return f"Error creating Excel file: {str(e)}", 500

@app.route('/api/download-selected-parties', methods=['POST'])
def download_selected_parties():
    if not is_authenticated():
        return redirect(url_for('login'))
    
    selected_ids = request.form.getlist('selected_ids')
    if not selected_ids:
        return "No restricted parties selected", 400
    
    try:
        parties = load_data(RESTRICTED_PARTIES_FILE)
        selected_parties = [p for p in parties if str(p.get('id')) in selected_ids]
        
        if not selected_parties:
            return "No matching restricted parties found", 404
        
        # Create DataFrame
        df = pd.DataFrame(selected_parties)
        
        # Create Excel file in memory
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Selected_Restricted_Parties', index=False)
        
        excel_buffer.seek(0)
        
        return send_file(
            io.BytesIO(excel_buffer.read()),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'selected_restricted_parties_{len(selected_parties)}_records.xlsx'
        )
        
    except Exception as e:
        return f"Error creating Excel file: {str(e)}", 500

def create_project_zip():
    # Create a BytesIO buffer for the ZIP file
    zip_buffer = io.BytesIO()

    # Files to include in the ZIP
    files_to_zip = [
        'app.py',
        'main.py', 
        'standalone_tool.py',
        'highlighter_app.py',
        'desktop_highlighter.py',
        'install_desktop_highlighter.py',
        'requirements.txt',
        'requirements_desktop.txt',
        'requirement.txt',
        'README.md',
        'README_desktop_highlighter.md',
        'customers.json',
        'restricted_parties.json',
        'matches.json',
        'users.json',
        'analytics.json',
        '.replit',
        '.gitignore',
        'procfile',
        'pyproject.toml',
        'uv.lock'
    ]

    # Directories to include
    dirs_to_zip = ['templates', 'attached_assets', 'uploads']

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add individual files
        for file_path in files_to_zip:
            if os.path.exists(file_path):
                zip_file.write(file_path)

        # Add directories
        for dir_path in dirs_to_zip:
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zip_file.write(file_path)

    zip_buffer.seek(0)

    return send_file(
        io.BytesIO(zip_buffer.read()),
        mimetype='application/zip',
        as_attachment=True,
        download_name='TC_HUB_Assist_Complete_Project.zip'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)