from flask import Flask, render_template, jsonify
from random import shuffle
import threading
import time

app = Flask(__name__)

array = [5, 3, 2, 8, 7, 4, 1, 6, 9, 0, 11, 10]
shuffle_count = 0
sorted_flag = False
start_time = None

# Check if array is sorted
def isSorted(arr):
    for index in range(len(arr) - 1):
        if arr[index] > arr[index + 1]:
            return False
    return True

# BOGO Sort (shuffling and checking)
def bogo():
    global array, shuffle_count, sorted_flag, start_time
    start_time = time.time()  # start time
    while not sorted_flag:
        if not isSorted(array):
            shuffle(array)
            shuffle_count += 1
            time.sleep(0.2)  # shuffle frequency -> every 0.2s
        else:
            sorted_flag = True  # Stop when sorted

# Start the BogoSort in a background thread
def start_bogo_sort():
    thread = threading.Thread(target=bogo)
    thread.daemon = True
    thread.start()

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

if __name__ == '__main__':
    start_bogo_sort()
    app.run(debug=True, host='0.0.0.0')
