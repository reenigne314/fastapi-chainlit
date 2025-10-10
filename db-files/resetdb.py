import os
import sqlite3

# Define the path to the database file
db_path = "example.db"

# --- Reset Logic ---
# Check if the database file already exists
if os.path.exists(db_path):
    # If it exists, remove it
    os.remove(db_path)
    print(f"Database '{db_path}' has been reset (deleted).")
else:
    # If it doesn't exist, there's nothing to reset
    print(f"Database '{db_path}' did not exist. A new one will be created.")

# --- Re-initialize Connection (from your original code) ---
# Now, connect to the database. Sqlite3 will create a new empty file.
conn = sqlite3.connect(db_path, check_same_thread=False)