"""
Bulk Insert Script for API Aadhar Data
This script reads the combined CSV files and inserts them into the corresponding SQL Server tables.
Uses Azure Entra ID (Azure AD) authentication with fast_executemany for bulk performance.
"""

import pandas as pd
import pyodbc
import struct
import os
from datetime import datetime
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential

# Configuration - Update these values to match your SQL Server connection
SERVER = 'personal-db.database.windows.net'  # Your Azure SQL Server address
DATABASE = 'uidai_2026_datasets'  # Update with your database name
DRIVER = '{ODBC Driver 18 for SQL Server}'  # Update if using different driver

# Set to True to use interactive browser login, False to use DefaultAzureCredential
USE_INTERACTIVE_LOGIN = False

# Dataset paths
DATASETS_PATH = '/Users/aishik/Desktop/uidai_data_hack_2026/datasets/'

# CSV to Table mapping
DATASETS = [
    {
        'csv_file': 'api_data_aadhar_biometric_combined.csv',
        'table_name': 'api_data_aadhar_biometric',
        'columns': ['date_of_data', 'state_name', 'district_name', 'pincode', 'bio_age_5_17', 'bio_age_17_']
    },
    {
        'csv_file': 'api_data_aadhar_demographic_combined.csv',
        'table_name': 'api_data_aadhar_demographic',
        'columns': ['date_of_data', 'state_name', 'district_name', 'pincode', 'demo_age_5_17', 'demo_age_17_']
    },
    {
        'csv_file': 'api_data_aadhar_enrolment_combined.csv',
        'table_name': 'api_data_aadhar_enrollment',
        'columns': ['date_of_data', 'state_name', 'district_name', 'pincode', 'age_0_5', 'age_5_17', 'age_18_greater']
    }
]

BATCH_SIZE = 50000  # Number of rows to insert per batch (increased for better performance)


def get_access_token():
    """Get Azure AD access token for SQL Server."""
    # Azure SQL Database resource ID
    sql_resource = "https://database.windows.net/.default"
    
    if USE_INTERACTIVE_LOGIN:
        # Interactive browser login - opens browser for authentication
        credential = InteractiveBrowserCredential()
    else:
        # DefaultAzureCredential tries multiple auth methods:
        # Environment variables, Managed Identity, Azure CLI, etc.
        credential = DefaultAzureCredential()
    
    token = credential.get_token(sql_resource)
    return token.token


def get_connection():
    """Create and return a database connection using Azure Entra ID authentication."""
    # Get access token
    print('   Acquiring Azure Entra ID token...')
    access_token = get_access_token()
    
    # Convert token to bytes for pyodbc
    token_bytes = access_token.encode('utf-8')
    exp_token = b''
    for i in token_bytes:
        exp_token += bytes([i]) + bytes(1)
    
    token_struct = struct.pack('=i', len(exp_token)) + exp_token
    
    # Connection string without credentials
    connection_string = (
        f'DRIVER={DRIVER};'
        f'SERVER={SERVER};'
        f'DATABASE={DATABASE};'
        f'Encrypt=yes;'
        f'TrustServerCertificate=no;'
    )
    
    # SQL_COPT_SS_ACCESS_TOKEN attribute
    SQL_COPT_SS_ACCESS_TOKEN = 1256
    
    conn = pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    return conn


def truncate_table(conn, table_name):
    """Truncate a table before inserting new data."""
    print(f'>> Truncating Table: {table_name}')
    cursor = conn.cursor()
    cursor.execute(f'TRUNCATE TABLE {table_name}')
    conn.commit()
    cursor.close()


def bulk_insert_dataframe(conn, df, table_name, columns):
    """Insert a DataFrame into SQL Server table using fast_executemany for bulk performance."""
    placeholders = ', '.join(['?' for _ in columns])
    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    total_rows = len(df)
    inserted = 0
    
    # Create cursor with fast_executemany enabled for bulk insert performance
    cursor = conn.cursor()
    cursor.fast_executemany = True  # This is the key for bulk insert performance!
    
    for start in range(0, total_rows, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total_rows)
        batch = df.iloc[start:end]
        
        # Convert DataFrame rows to list of tuples
        data = [tuple(row) for row in batch.values]
        
        cursor.executemany(insert_sql, data)
        conn.commit()
        
        inserted += len(data)
        print(f'   Inserted {inserted:,} / {total_rows:,} rows ({(inserted/total_rows)*100:.1f}%)')
    
    cursor.close()
    return total_rows


def process_dataset(conn, dataset_info):
    """Process a single dataset: read CSV, truncate table, and insert data."""
    csv_path = os.path.join(DATASETS_PATH, dataset_info['csv_file'])
    table_name = dataset_info['table_name']
    columns = dataset_info['columns']
    
    print(f'\n>> Processing: {dataset_info["csv_file"]}')
    print(f'   Target Table: {table_name}')
    
    # Read CSV file
    print(f'   Reading CSV file...')
    df = pd.read_csv(csv_path)
    
    # Rename columns to match table schema (in case CSV headers differ)
    df.columns = columns
    
    # Convert date column to proper format
    df['date_of_data'] = pd.to_datetime(df['date_of_data'], format='%d-%m-%Y').dt.strftime('%Y-%m-%d')
    
    # Convert numeric columns to appropriate types to avoid type issues
    for col in columns[4:]:  # Skip date, state, district, pincode
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    
    df['pincode'] = pd.to_numeric(df['pincode'], errors='coerce').fillna(0).astype(int)
    
    # Truncate table
    truncate_table(conn, table_name)
    
    # Bulk insert
    print(f'   Inserting {len(df):,} rows using fast_executemany...')
    row_count = bulk_insert_dataframe(conn, df, table_name, columns)
    
    print(f'>> Completed: {table_name} ({row_count:,} rows inserted)')
    return row_count


def main():
    print('=' * 50)
    print('Bulk Insert Script for API Aadhar Data')
    print('=' * 50)
    
    start_time = datetime.now()
    
    try:
        # Connect to database
        print('\nConnecting to SQL Server...')
        conn = get_connection()
        print('Connected successfully!')
        
        # Process each dataset
        results = {}
        for dataset in DATASETS:
            row_count = process_dataset(conn, dataset)
            results[dataset['table_name']] = row_count
        
        # Print summary
        print('\n' + '=' * 50)
        print('Bulk Insert Summary')
        print('=' * 50)
        for table_name, row_count in results.items():
            print(f'  {table_name}: {row_count:,} rows')
        
        total_rows = sum(results.values())
        print(f'\n  Total Rows Inserted: {total_rows:,}')
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f'\n  Start Time: {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'  End Time: {end_time.strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'  Duration: {duration:.2f} seconds')
        print('=' * 50)
        
        # Close connection
        conn.close()
        print('\nBulk Insert Completed Successfully!')
        
    except pyodbc.Error as e:
        print(f'\nDatabase Error: {e}')
        raise
    except Exception as e:
        print(f'\nError: {e}')
        raise


if __name__ == '__main__':
    main()
