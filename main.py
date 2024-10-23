from flask import Flask, render_template
from random import shuffle

app = Flask(__name__)


# Verifying if array is sorted
def isSorted(arr):
    for index in range(len(arr) - 1):
        if arr[index] > arr[index + 1]:
            return False
    return True


# BOGO Sort
def bogo(arr):
    shuffle(arr)
    return arr


@app.route('/')
def home():
    wallahi = [4, 2, 3, 1]
    return render_template('index.html', bogo=bogo(wallahi), luck=isSorted(wallahi))
