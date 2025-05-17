from flask import Flask, render_template, jsonify
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


# Start the database and create table if it doesn't exist
def init_db():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS progress (
                        id INTEGER PRIMARY KEY,
                        shuffle_count INTEGER,
                        start_time REAL,
                        sorted_flag BOOLEAN
                    )''')
    conn.commit()
    conn.close()
    logging.info("Database initialized/table created.")


# Load progress from the database
def load_progress():
    global shuffle_count, start_time, sorted_flag
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT shuffle_count, start_time, sorted_flag FROM progress WHERE id = 1")
    row = cursor.fetchone()
    if row:
        shuffle_count, start_time, sorted_flag = row
        logging.info(f"Loaded progress from DB: shuffle_count={shuffle_count}, start_time={start_time}, sorted_flag={sorted_flag}")
    else:
        # Initialize start time if no record exists
        logging.info("No existing progress found in DB, initializing new record.")
        start_time = time.time()
        cursor.execute("INSERT INTO progress (id, shuffle_count, start_time, sorted_flag) VALUES (1, 0, ?, 0)", (start_time,))
        conn.commit()
    conn.close()


# Saving progress to the database
def save_progress():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("UPDATE progress SET shuffle_count = ?, start_time = ?, sorted_flag = ? WHERE id = 1",
                   (shuffle_count, start_time, sorted_flag))
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
    global shuffle_count, sorted_flag
    while not sorted_flag:
        if not isSorted(array):
            shuffle(array)
            shuffle_count += 1
            time.sleep(0.2)  # shuffle frequency -> every 0.2s
        else:
            sorted_flag = True  # Stop when sorted


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

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/shuffle_array')
def shuffle_array():
    # Calculate the elapsed time
    elapsed_time = time.time() - start_time if start_time else 0
    return jsonify({
        'array': array,
        'sorted': sorted_flag,
        'shuffle_count': shuffle_count,
        'elapsed_time': elapsed_time  # Send elapsed time to client
    })

# Local development server (deployed app is not running this)
if __name__ == '__main__':
    start_bogo_sort()
    app.run(debug=True, use_reloader=True)
