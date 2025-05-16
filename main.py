from flask import Flask, render_template, jsonify
from random import shuffle
import threading
import time
import sqlite3

app = Flask(__name__)

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


# Load progress from the database
def load_progress():
    global shuffle_count, start_time, sorted_flag
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT shuffle_count, start_time, sorted_flag FROM progress WHERE id = 1")
    row = cursor.fetchone()
    if row:
        shuffle_count, start_time, sorted_flag = row
    else:
        # Initialize start time if no record exists
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
    init_db()
    load_progress()
    # Starting the bogo thread
    thread = threading.Thread(target=bogo)
    thread.daemon = True
    thread.start()
    # Starting the saving to database thread
    thread_save = threading.Thread(target=savingDB)
    thread_save.daemon = True
    thread_save.start()

if __name__ == '__main__':
    start_bogo_sort()


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
