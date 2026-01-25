from flask import Flask, render_template, jsonify
from datetime import date
from random import shuffle
import threading
import time
import sqlite3
import logging
import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Thread lock for safe concurrent access to shared state
state_lock = threading.Lock()

DEFAULT_ARRAY = [5, 3, 2, 8, 7, 4, 1, 6, 9, 11, 10, 12, 15, 13, 14]

array = DEFAULT_ARRAY.copy()
shuffle_count = 0
sorted_flag = False
start_time = None
db_file = 'progress.db'
sorted_date = None
end_time = None


# Start the database and create table if it doesn't exist
def init_db():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS progress (
                        id INTEGER PRIMARY KEY,
                        shuffle_count INTEGER,
                        start_time REAL,
                        sorted_flag BOOLEAN,
                        sorted_date TEXT,
                        end_time REAL,
                        array_state TEXT
                    )''')
    cursor.execute("PRAGMA table_info(progress)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'sorted_date' not in columns:
        logging.info("Adding sorted_date column to progress table.")
        cursor.execute("ALTER TABLE progress ADD COLUMN sorted_date TEXT")
    if 'end_time' not in columns:
        logging.info("Adding end_time column to progress table.")
        cursor.execute("ALTER TABLE progress ADD COLUMN end_time REAL")
    if 'array_state' not in columns:
        logging.info("Adding array_state column to progress table.")
        cursor.execute("ALTER TABLE progress ADD COLUMN array_state TEXT")
    conn.commit()
    conn.close()
    logging.info("Database initialized/table created or updated.")


# Load progress from the database
def load_progress():
    global array, shuffle_count, start_time, sorted_flag, sorted_date, end_time
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT shuffle_count, start_time, sorted_flag, sorted_date, end_time, array_state FROM progress WHERE id = 1")
    row = cursor.fetchone()
    if row:
        shuffle_count, start_time, sorted_flag, sorted_date, end_time, array_state_json = row
        sorted_flag = bool(sorted_flag)
        # Load array state from database, or use default if not saved
        if array_state_json:
            array = json.loads(array_state_json)
            logging.info(f"Loaded array state from DB: {array}")
        else:
            array = DEFAULT_ARRAY.copy()
            logging.info(f"No array state in DB, using default: {array}")
        logging.info(f"Loaded progress from DB: shuffle_count={shuffle_count}, start_time={start_time}, sorted_flag={sorted_flag}, sorted_date={sorted_date}, end_time={end_time}")
    else:
        # Initialize start time if no record exists
        logging.info("No existing progress found in DB, initializing new record.")
        array = DEFAULT_ARRAY.copy()
        start_time = time.time()
        array_state_json = json.dumps(array)
        cursor.execute("INSERT INTO progress (id, shuffle_count, start_time, sorted_flag, sorted_date, end_time, array_state) VALUES (1, 0, ?, 0, ?, ?, ?)", 
                       (start_time, sorted_date, end_time, array_state_json))
        conn.commit()
    conn.close()


# Save progress to the database
def save_progress():
    with state_lock:
        array_state_json = json.dumps(array)
        logging.info(f"SAVE_PROGRESS: Attempting to save with values: shuffle_count={shuffle_count}, start_time={start_time}, sorted_flag={sorted_flag}, sorted_date={sorted_date}, end_time={end_time}, array={array}")
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("UPDATE progress SET shuffle_count = ?, start_time = ?, sorted_flag = ?, sorted_date = ?, end_time = ?, array_state = ? WHERE id = 1",
                       (shuffle_count, start_time, sorted_flag, sorted_date, end_time, array_state_json))
        conn.commit()
        conn.close()


# Check if array is sorted
def isSorted(arr):
    for index in range(len(arr) - 1):
        if arr[index] > arr[index + 1]:
            return False
    return True


# BOGO Sort (shuffling and checking)
def bogo():
    global shuffle_count, sorted_flag, sorted_date, end_time
    while not sorted_flag:
        with state_lock:
            if not isSorted(array):
                shuffle(array)
                shuffle_count += 1
            else:
                if not sorted_flag:
                    today = date.today()
                    sorted_date = today.strftime("%d/%m/%Y")
                    end_time = time.time()
                    sorted_flag = True  # Stop when sorted
        
        # Save immediately when sorted (outside lock to avoid deadlock with save_progress lock)
        if sorted_flag:
            save_progress()
            logging.info(f"Array sorted on {sorted_date}. Progress saved to DB.")
            break
        
        time.sleep(0.1)  # shuffle frequency -> every 0.1s


# Saving to the database every 2 minutes
def savingDB():
    while True:
        time.sleep(120)
        with state_lock:
            is_sorted = sorted_flag
        if is_sorted:
            break
        save_progress()


# Starting the BogoSort in a background thread
def start_bogo_sort():
    logging.info("Starting Bogo Sort process and database initialization...")
    init_db()
    load_progress()
    
    # Checking if already sorted - if so, don't start the sorting threads
    if sorted_flag:
        logging.info(f"Array already sorted on {sorted_date}. No sorting threads started. Array state: {array}")
        return
    
    # Starting the bogo thread
    logging.info("Starting Bogo Sort background thread...")
    thread = threading.Thread(target=bogo)
    thread.daemon = True
    thread.start()
    # Starting the saving to database thread
    logging.info("Starting database saving background thread...")
    thread_save = threading.Thread(target=savingDB)
    thread_save.daemon = True
    thread_save.start()
    logging.info("Bogo Sort process and threads started successfully.")


# Home page
@app.route('/')
def index():
    return render_template('index.html')


# Shuffle array endpoint
@app.route('/shuffle_array')
def shuffle_array():
    with state_lock:
        # Copying values while holding lock for thread-safe read
        current_array = array.copy()
        current_sorted_flag = sorted_flag
        current_shuffle_count = shuffle_count
        current_sorted_date = sorted_date
        current_start_time = start_time
        current_end_time = end_time

    calculated_elapsed_time = 0
    if current_start_time is not None:
        if current_sorted_flag:
            if current_end_time is not None:
                calculated_elapsed_time = current_end_time - current_start_time
            else:
                calculated_elapsed_time = 0
                logging.warning("Array is sorted, but end_time was not found in the database. Elapsed time is shown as 0.")
        else:
            calculated_elapsed_time = time.time() - current_start_time
    
    # Sending the data to the client
    return jsonify({
        'array': current_array,
        'sorted': current_sorted_flag,
        'shuffle_count': current_shuffle_count,
        'elapsed_time': calculated_elapsed_time,
        'sorted_date': current_sorted_date
    })


# Local development server (deployed app is not running this)
if __name__ == '__main__':
    start_bogo_sort()
    app.run(debug=True, use_reloader=True)
