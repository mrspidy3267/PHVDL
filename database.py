import os
from supabase import create_client, Client
from config import *
# Initialize the Supabase client
def connect_to_supabase():
    try:
        url = DATABASE_URL
        key = DATABASE_KEY
        supabase = create_client(url, key)
        print("Connected to Supabase")
        return supabase
    except Exception as e:
        print(f"Error: Could not connect to Supabase.\n{e}")
        return None

# Insert a document (row) into a Supabase table
def insert_document(supabase, table_name, document):
    try:
        data = supabase.table(table_name).insert(document).execute()
        print(f"Inserted document with data: {data.data}")
    except Exception as e:
        print(f"Error: Could not insert document.\n{e}")

# Find documents (rows) from a Supabase table
def find_documents(supabase, table_name, query=None):
    try:
        if query:
            data = supabase.table(table_name).select("*").match(query).execute()
        else:
            data = supabase.table(table_name).select("*").execute()
        
        return data.data
    except Exception as e:
        print(f"Error: Could not retrieve documents.\n{e}")
        return []

# Check if a specific URL exists in the Supabase table
def check_db(supabase, table_name, url):
    documents = find_documents(supabase, table_name)
    urls = [doc["URL"] for doc in documents]
    return url in urls

# Get document info by URL from the Supabase table
def get_info(supabase, table_name, url):
    documents = find_documents(supabase, table_name, {"URL": url})
    if documents:
        return documents[0]
    return None

# Get all URLs from the Supabase table
def get_raw_url(supabase, table_name):
    documents = find_documents(supabase, table_name)
    print(documents)
    urls = [doc["URL"] for doc in documents]
    return urls
