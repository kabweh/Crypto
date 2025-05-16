#!/home/ubuntu/crypto_investigator_app/venv/bin/python
import os
import csv

# Path to the local scam database file (e.g., a CSV)
# This file would need to be created and maintained, possibly through scraping or manual updates.
SCAM_DB_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "scam_database.csv") # Assuming a data directory at the root

# In-memory cache of scam addresses for faster lookups
SCAM_ADDRESSES_CACHE = set()
LAST_LOAD_TIME = 0
CACHE_TTL = 3600 # Reload cache every hour, for example

def load_scam_database():
    """Loads scam addresses from the local CSV file into an in-memory set."""
    global SCAM_ADDRESSES_CACHE, LAST_LOAD_TIME
    current_time = time.time()

    if not os.path.exists(SCAM_DB_FILE_PATH):
        print(f"Warning: Scam database file not found at {SCAM_DB_FILE_PATH}")
        SCAM_ADDRESSES_CACHE = set() # Ensure cache is empty if file doesn't exist
        LAST_LOAD_TIME = current_time
        return

    # Reload if cache is empty or TTL has expired
    if not SCAM_ADDRESSES_CACHE or (current_time - LAST_LOAD_TIME > CACHE_TTL):
        print(f"Loading scam database from {SCAM_DB_FILE_PATH}...")
        temp_cache = set()
        try:
            # Ensure the /data directory exists
            data_dir = os.path.dirname(SCAM_DB_FILE_PATH)
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                print(f"Created data directory: {data_dir}")
                # Create an empty scam_database.csv if it doesn't exist after creating the directory
                with open(SCAM_DB_FILE_PATH, "w", newline=
"" ) as f:
                    writer = csv.writer(f)
                    writer.writerow(["address", "chain", "category", "source_url"])
                print(f"Created empty scam database file: {SCAM_DB_FILE_PATH}")

            with open(SCAM_DB_FILE_PATH, "r", newline=
"" ) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    address = row.get("address")
                    if address:
                        temp_cache.add(address.lower()) # Store addresses in lowercase for consistent matching
            SCAM_ADDRESSES_CACHE = temp_cache
            LAST_LOAD_TIME = current_time
            print(f"Scam database loaded: {len(SCAM_ADDRESSES_CACHE)} entries.")
        except FileNotFoundError:
            print(f"Error: Scam database file not found at {SCAM_DB_FILE_PATH}. Creating an empty one.")
            SCAM_ADDRESSES_CACHE = set()
            # Create an empty file with headers if it was not found
            try:
                with open(SCAM_DB_FILE_PATH, "w", newline=
"" ) as f:
                    writer = csv.writer(f)
                    writer.writerow(["address", "chain", "category", "source_url"])
            except Exception as e_create:
                print(f"Could not create empty scam database file: {e_create}")
        except Exception as e:
            print(f"Error loading scam database: {e}")
            # Potentially clear cache or use stale data based on policy
            # SCAM_ADDRESSES_CACHE = set() # Clearing cache on error

def is_address_scam(address, chain=None):
    """
    Checks if a given address is in the loaded scam database.
    Optionally, chain can be used in the future if the DB stores chain-specific scams.
    """
    load_scam_database() # Ensure DB is loaded/updated
    return address.lower() in SCAM_ADDRESSES_CACHE

# --- Functions for managing the scam database (e.g., adding entries) ---
# These would typically be admin functions or part of an update script.

def add_scam_entry(address, chain, category, source_url):
    """Adds a new entry to the scam database CSV file and updates the cache."""
    if not os.path.exists(SCAM_DB_FILE_PATH):
        # Create the file with headers if it doesn't exist
        data_dir = os.path.dirname(SCAM_DB_FILE_PATH)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        with open(SCAM_DB_FILE_PATH, "w", newline=
"" ) as f:
            writer = csv.writer(f)
            writer.writerow(["address", "chain", "category", "source_url"])
    
    try:
        with open(SCAM_DB_FILE_PATH, "a", newline=
"" ) as f:
            writer = csv.writer(f)
            writer.writerow([address, chain, category, source_url])
        SCAM_ADDRESSES_CACHE.add(address.lower()) # Update cache immediately
        print(f"Added scam entry: {address}")
        return True
    except Exception as e:
        print(f"Error adding scam entry {address}: {e}")
        return False

# Initialize by loading the database when the module is first imported
# This ensures the /data directory and the scam_database.csv file are created if they don't exist.
import time # ensure time is imported for LAST_LOAD_TIME
load_scam_database()

