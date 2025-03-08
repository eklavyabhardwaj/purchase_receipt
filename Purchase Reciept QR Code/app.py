# app.py
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
import requests
import pandas as pd
import random
import psycopg2
from io import BytesIO
import base64
import string
from sqlalchemy import create_engine, text
from urllib.parse import quote

random_number = random.randint(14364546454654654654651465654, 9168468484867187618761871687171)

app = Flask(__name__)
app.secret_key = str(random_number)

# API Configuration
BASE_URL = 'https://erpv14.electrolabgroup.com/'
ENDPOINT = 'api/resource/Purchase Receipt'
ENDPOINT2 = 'api/resource/Work Order'

API_URL = BASE_URL + ENDPOINT
API_URL2 = BASE_URL + ENDPOINT2

# First API call parameters
API_PARAMS = {
    'fields': '["name","items.item_name","posting_date","items.qty","items.custom_batch_code","items.custom_date_code","supplier_name"]',
    'limit_start': 0,
    'limit_page_length': 100000000000,
    'filters': '[["posting_date", ">", "2024-04-01"],["creation", ">", "2025-01-01"]]'
}

# Second API call parameters
NAME_PARAMS = {
    'fields': '["items.name","items.item_name","creation"]',
    'limit_start': 0,
    'limit_page_length': 100000000000,
    'filters': '[["posting_date", ">", "2024-04-01"],["creation", ">", "2025-01-01"]]'
}

WORK_ORDER_PARAMS = {
    'fields': '["name","qty","custom_inhouse_supplier_name"]',
    'limit_start': 0, 
    'limit_page_length': 100000000000,
    'filters': '[["creation", ">", "2025-01-01"]]'
}

API_HEADERS = {
    'Authorization': 'token 3ee8d03949516d0:6baa361266cf807'
}

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'admin@123'
}

def get_api_data_pr():
    response = requests.get(API_URL, params=API_PARAMS, headers=API_HEADERS)
    if response.status_code != 200:
        return pd.DataFrame()
    
    api_df = pd.DataFrame(response.json()['data'])
    
    name_response = requests.get(API_URL, params=NAME_PARAMS, headers=API_HEADERS)
    if name_response.status_code != 200:
        return api_df
    
    name_df = pd.DataFrame(name_response.json()['data'])
    name_df.rename(columns={'name': 'child_name'}, inplace=True)
    
    if not api_df.empty and not name_df.empty:
        api_df['child_name'] = name_df['child_name']
    
    return api_df

def get_db_data_pr():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        query = "SELECT * FROM purchase_reciept_batch"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return pd.DataFrame()

def merge_data_pr(api_df, db_df):
    if not api_df.empty and not db_df.empty:
        if 'child_name' in api_df.columns and 'child_name' in db_df.columns:
            merged_df = pd.merge(api_df, db_df, on=['name', 'child_name', 'item_name'], how='inner', suffixes=('_api', '_db'))
        else:
            merged_df = pd.merge(api_df, db_df, on=['name', 'item_name'], how='inner', suffixes=('_api', '_db'))
        return merged_df
    return api_df if not api_df.empty else db_df

import qrcode

def generate_qr_code(result_name):
    """Generates a QR Code image for the erpv14 URL, and returns a data URI."""
    url = f"https://erpv14.electrolabgroup.com/app/purchase-receipt/{result_name}"
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4)

        qr.add_data(url)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()

        img.save(buffer)

        encoded_string = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return 'data:image/png;base64,' + encoded_string
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return ""


@app.route('/')
def home():
    return render_template('main.html')

@app.route('/purchase_reciept')
def issue():
    return render_template('purchase_reciept.html')

@app.route('/search_pr', methods=['GET', 'POST'])
def search():
    #Api Get Method
    import requests
    import pandas as pd

    base_url = BASE_URL
    endpoint = 'api/resource/Purchase Receipt'
    url = base_url + endpoint

    params = {
        'fields': '["name","items.item_name","posting_date","items.qty","items.custom_batch_code","items.custom_date_code","supplier_name","creation"]',
        'limit_start': 0, 
        'limit_page_length': 100000000000,
        'filters': '[["posting_date", ">", "2024-04-01"],["creation", ">", "2025-01-01"]]'
    }

    headers = {
        'Authorization': 'token 3ee8d03949516d0:6baa361266cf807'
    }
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Fields are correct.")
        df = pd.DataFrame(data['data'])
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print("Response:", response.json())

    #Api Get Method
    import requests
    import pandas as pd

    base_url = BASE_URL
    endpoint = 'api/resource/Purchase Receipt'
    url = base_url + endpoint

    params = {
        'fields': '["items.name","items.item_name","creation"]',
        'limit_start': 0, 
        'limit_page_length': 100000000000,
        'filters': '[["posting_date", ">", "2024-04-01"],["creation", ">", "2025-01-01"]]'
    }

    headers = {
        'Authorization': 'token 3ee8d03949516d0:6baa361266cf807'
    }
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Fields are correct.")
        name_df = pd.DataFrame(data['data'])
        name_df.rename(columns={'name': 'child_name'}, inplace=True)
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print("Response:", response.json())

    df['child_name'] = name_df['child_name']

    db_config= DB_CONFIG 

    #Optional
    # Create engine once
    encoded_password = quote(db_config['password'])
    engine = create_engine(f"postgresql://{db_config['user']}:{encoded_password}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

    # First, fetch ALL existing batch codes from database
    def get_existing_codes(engine):
        with engine.connect() as conn:
            # Get all existing data
            existing_data = pd.read_sql(text("SELECT name, eipl_unique_batch_code FROM purchase_reciept_batch"), conn)
            
        return set(existing_data['name']), set(existing_data['eipl_unique_batch_code'])

    # Function to get 4-digit fiscal year
    def get_fiscal_year(date):
        year = date.year
        if date.month >= 4:
            return f"{str(year)[-2:]}{str(year+1)[-2:]}"
        else:
            return f"{str(year-1)[-2:]}{str(year)[-2:]}"

    # Modified function to generate unique batch with extra verification
    def generate_unique_batch(fiscal_year, existing_codes, engine):
        max_attempts = 1000  # Safety limit
        attempt = 0
        
        while attempt < max_attempts:
            # Generate random part
            unique_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            new_code = f"RAW{fiscal_year}{unique_part}"
            
            # Double check it's not in existing codes
            if new_code not in existing_codes:
                # Verify one more time with database
                with engine.connect() as conn:
                    verify_query = text("SELECT COUNT(*) FROM purchase_reciept_batch WHERE eipl_unique_batch_code = :code")
                    result = conn.execute(verify_query, {"code": new_code}).scalar()
                    
                    if result == 0:  # Code definitely doesn't exist
                        existing_codes.add(new_code)
                        return new_code
            
            attempt += 1
        
        raise Exception("Unable to generate unique batch code after maximum attempts")

    # Main process
    # First get all existing data
    existing_names_set, existing_batch_codes_set = get_existing_codes(engine)

    # Your main dataframe (df) with new data
    df['posting_date'] = pd.to_datetime(df['posting_date'])

    # Filter out rows where 'name' already exists
    new_rows_df = df[~df['name'].isin(existing_names_set)].copy()

    # Generate fiscal year
    new_rows_df['fiscal_year'] = new_rows_df['posting_date'].apply(get_fiscal_year)

    # Generate batch codes with extra verification
    new_rows_df['eipl_unique_batch_code'] = new_rows_df['fiscal_year'].apply(
        lambda x: generate_unique_batch(x, existing_batch_codes_set, engine)
    )

    # Drop the fiscal year column
    new_rows_df.drop(columns=['fiscal_year'], inplace=True)

    # Select required columns
    df_to_upload = new_rows_df[['name', 'item_name', 'child_name', 'eipl_unique_batch_code']]

    # Insert new rows only
    if not df_to_upload.empty:
        df_to_upload.to_sql('purchase_reciept_batch', engine, if_exists='append', index=False)
        print(f"{len(df_to_upload)} new rows uploaded successfully!")
    else:
        print("No new data to upload.")

    search_term = request.form.get('search_name') or request.args.get('search_name')
    api_data = get_api_data_pr()
    db_data = get_db_data_pr()
    merged_data = merge_data_pr(api_data, db_data)

    if not merged_data.empty:
        results = merged_data[
            (merged_data['name'].str.lower() == search_term.lower()) |
            (merged_data['eipl_unique_batch_code'].str.lower() == search_term.lower())
        ]
        #Pass the base URL to the template
        return render_template('results_pr.html', results=results.to_dict('records'), generate_qr_code=generate_qr_code, base_url=request.url_root)

    return render_template('results_pr.html', results=[])

@app.route('/search_pr/<search_term>', methods=['GET']) # Example using name
def search_by_name(search_term):
    api_data = get_api_data_pr()
    db_data = get_db_data_pr()
    merged_data = merge_data_pr(api_data, db_data)
    if not merged_data.empty:
        results = merged_data[
            (merged_data['name'].str.lower() == search_term.lower()) |
            (merged_data['eipl_unique_batch_code'].str.lower() == search_term.lower())
        ]
        return render_template('results_pr.html', results=results.to_dict('records'), generate_qr_code=generate_qr_code)

    return render_template('results_pr.html', results=[])

@app.template_filter('custom_truncate')
def custom_truncate(s, length=82):
    return s[:length] if s else ""

# ------------------------------------------------------------------------------------------------------------------------------------------------
def get_api_data_wo():
    # First API call
    response = requests.get(API_URL2, params=WORK_ORDER_PARAMS, headers=API_HEADERS)
    if response.status_code != 200:
        return pd.DataFrame()
    
    api_df = pd.DataFrame(response.json()['data'])   
    return api_df

def get_db_data_wo():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        query = "SELECT * FROM work_order_batch"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return pd.DataFrame()

def merge_data_wo(api_df, db_df):
    # Merge based on name, child_name and item_name
    if not api_df.empty and not db_df.empty:
        merged_df = pd.merge(api_df, db_df, on=['name'], how='inner')
        return merged_df
    return api_df if not api_df.empty else db_df

@app.route('/work_order')
def warranty():
    return render_template('work_order.html')

@app.route('/search_wo', methods=['POST'])
def search2():

    base_url = BASE_URL
    endpoint = 'api/resource/Work Order'
    url = base_url + endpoint

    params = {
        'fields': '["name","qty","custom_inhouse_supplier_name"]',
        'limit_start': 0, 
        'limit_page_length': 100000000000,
        'filters': '[["creation", ">", "2025-01-01"]]'
    }

    headers = {
        'Authorization': 'token 3ee8d03949516d0:6baa361266cf807'
    }
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Fields are correct.")
        wo_df = pd.DataFrame(data['data'])
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print("Response:", response.json())

    db_config= DB_CONFIG

    # Create engine once
    encoded_password = quote(db_config['password'])
    engine = create_engine(f"postgresql://{db_config['user']}:{encoded_password}@{db_config['host']}:{db_config['port']}/{db_config['database']}")

    # Fetch existing names and batch codes
    def get_existing_codes(engine):
        with engine.connect() as conn:
            existing_data = pd.read_sql(text("SELECT name, eipl_unique_batch_code_wo FROM work_order_batch"), conn)
        
        return set(existing_data['name']), set(existing_data['eipl_unique_batch_code_wo'])

    # Function to generate a unique batch code
    def generate_unique_batch(existing_codes, engine):
        max_attempts = 1000
        attempt = 0
        
        while attempt < max_attempts:
            # Generate random 9-character alphanumeric code
            unique_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
            new_code = f"PCB{unique_part}"
            
            # Check if the code exists in memory
            if new_code not in existing_codes:
                # Double-check with the database
                with engine.connect() as conn:
                    verify_query = text("SELECT COUNT(*) FROM work_order_batch WHERE eipl_unique_batch_code_wo = :code")
                    result = conn.execute(verify_query, {"code": new_code}).scalar()
                    
                    if result == 0:
                        existing_codes.add(new_code)
                        return new_code
            
            attempt += 1
        
        raise Exception("Unable to generate unique batch code after maximum attempts")

    # Main process
    existing_names_set, existing_batch_codes_set = get_existing_codes(engine)

    # Filter new names (names that do not exist in the database)
    new_entries = wo_df[~wo_df['name'].isin(existing_names_set)].copy()

    if not new_entries.empty:
        # Only select required columns before inserting into the database


        # Generate unique batch codes
        new_entries['eipl_unique_batch_code_wo'] = new_entries.apply(
            lambda row: generate_unique_batch(existing_batch_codes_set, engine), axis=1
        )
        
        # Insert new data into the database
        new_entries[['name', 'eipl_unique_batch_code_wo']].to_sql(
            'work_order_batch', engine, if_exists='append', index=False
        )
        print(f"{len(new_entries)} new rows uploaded successfully!")
    else:
        print("No new data to upload.")

    search_term = request.form.get('search_name')
    api_data = get_api_data_wo()
    db_data = get_db_data_wo()
    
    merged_data = merge_data_wo(api_data, db_data)
    
    if not merged_data.empty:
        # Search in both name and eipl_unique_batch_code columns
        results = merged_data[
            (merged_data['name'].str.lower() == search_term.lower()) |
            (merged_data['eipl_unique_batch_code_wo'].str.lower() == search_term.lower())
        ]
        return render_template('results_wo.html', results=results.to_dict('records'), generate_qr_code_wo=generate_qr_code_wo, base_url=request.url_root)
    
    return render_template('results_wo.html', results=[])

@app.route('/search_wo/<search_term>', methods=['GET']) # Example using name
def search_by_name2(search_term):
    api_data = get_api_data_wo()
    db_data = get_db_data_wo()
    merged_data = merge_data_wo(api_data, db_data)
    if not merged_data.empty:
        results = merged_data[
            (merged_data['name'].str.lower() == search_term.lower()) |
            (merged_data['eipl_unique_batch_code_wo'].str.lower() == search_term.lower())
        ]
        return render_template('results_wo.html', results=results.to_dict('records'), generate_qr_code_wo=generate_qr_code_wo)

    return render_template('results_wo.html', results=[])

def generate_qr_code_wo(result_name):
    """Generates a QR Code image for the erpv14 URL, and returns a data URI."""
    url = f"https://erpv14.electrolabgroup.com/app/work-order/{result_name}"
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4)

        qr.add_data(url)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()

        img.save(buffer)

        encoded_string = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return 'data:image/png;base64,' + encoded_string
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return ""

# ------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)