from main import isSorted

# Testing if the sorted array correctly flags isSorted as True
def test_isSorted_sorted_array():
    assert isSorted([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]) == True

# Testing if the unsorted array correctly flags isSorted as False
def test_isSorted_unsorted_array():
    assert isSorted([1, 3, 2, 5, 4, 6, 12, 8, 9, 10, 11, 7]) == False