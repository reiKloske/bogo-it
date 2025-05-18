from flask import Flask, render_template, jsonify
from datetime import date
from random import shuffle
import threading
import time
import sqlite3
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

array = [5, 3, 2, 8, 7, 4, 1, 6, 9, 11, 10, 12]
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
                        end_time REAL
                    )''')
    cursor.execute("PRAGMA table_info(progress)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'sorted_date' not in columns:
        logging.info("Adding sorted_date column to progress table.")
        cursor.execute("ALTER TABLE progress ADD COLUMN sorted_date TEXT")
    if 'end_time' not in columns:
        logging.info("Adding end_time column to progress table.")
        cursor.execute("ALTER TABLE progress ADD COLUMN end_time REAL")
    conn.commit()
    conn.close()
    logging.info("Database initialized/table created or updated.")


# Load progress from the database
def load_progress():
    global shuffle_count, start_time, sorted_flag, sorted_date, end_time
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT shuffle_count, start_time, sorted_flag, sorted_date, end_time FROM progress WHERE id = 1")
    row = cursor.fetchone()
    if row:
        shuffle_count, start_time, sorted_flag, sorted_date, end_time = row
        sorted_flag = bool(sorted_flag)
        logging.info(f"Loaded progress from DB: shuffle_count={shuffle_count}, start_time={start_time}, sorted_flag={sorted_flag}, sorted_date={sorted_date}, end_time={end_time}")
    else:
        # Initialize start time if no record exists
        logging.info("No existing progress found in DB, initializing new record.")
        start_time = time.time()
        cursor.execute("INSERT INTO progress (id, shuffle_count, start_time, sorted_flag, sorted_date, end_time) VALUES (1, 0, ?, 0, ?, ?)", (start_time, sorted_date, end_time))
        conn.commit()
    conn.close()


# Saving progress to the database
def save_progress():
    global shuffle_count, start_time, sorted_flag, sorted_date, end_time
    logging.info(f"SAVE_PROGRESS: Attempting to save with values: shuffle_count={shuffle_count}, start_time={start_time}, sorted_flag={sorted_flag}, sorted_date={sorted_date}, end_time={end_time}")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("UPDATE progress SET shuffle_count = ?, start_time = ?, sorted_flag = ?, sorted_date = ?, end_time = ? WHERE id = 1",
                   (shuffle_count, start_time, sorted_flag, sorted_date, end_time))
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
    global shuffle_count, sorted_flag, sorted_date, start_time, end_time
    while not sorted_flag:
        if not isSorted(array):
            shuffle(array)
            shuffle_count += 1
            time.sleep(0.1)  # shuffle frequency -> every 0.1s
        else:
            if not sorted_flag:
                today = date.today()
                sorted_date = today.strftime("%d/%m/%Y")
                end_time = time.time()
                sorted_flag = True  # Stop when sorted
                save_progress()
                logging.info(f"Array sorted on {sorted_date}. Progress saved to DB.")


# Saving to the database every 2 minutes
def savingDB():
    while not sorted_flag:
        time.sleep(120)
        save_progress()


# Starting the BogoSort in a background thread
def start_bogo_sort():
    logging.info("Starting Bogo Sort process and database initialization...")
    init_db()
    load_progress()
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
    global array, sorted_flag, shuffle_count, start_time, end_time, sorted_date

    calculated_elapsed_time = 0
    if start_time is not None:
        if sorted_flag:
            if end_time is not None:
                calculated_elapsed_time = end_time - start_time
            else:
                calculated_elapsed_time = 0
                logging.warning("Array is sorted, but end_time was not found in the database. Elapsed time is shown as 0.")
        else:
            calculated_elapsed_time = time.time() - start_time
    
    # Sending the data to the client
    return jsonify({
        'array': array,
        'sorted': sorted_flag,
        'shuffle_count': shuffle_count,
        'elapsed_time': calculated_elapsed_time,
        'sorted_date': sorted_date
    })


# Local development server (deployed app is not running this)
if __name__ == '__main__':
    start_bogo_sort()
    app.run(debug=True, use_reloader=True)
