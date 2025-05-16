import pytest
import threading
import main

# Resetting global states in main.py that are relevant to bogo sort
def reset_globals_for_test(test_array_content, initial_sorted_flag=False, initial_shuffle_count=0):
    main.array = list(test_array_content) 
    main.shuffle_count = initial_shuffle_count
    main.sorted_flag = initial_sorted_flag

@pytest.mark.timeout(30)
def test_bogo_sort_basic(mocker): # Added 'mocker' fixture from pytest-mock
    initial_test_array = [3, 1, 2]
    reset_globals_for_test(initial_test_array)

    mock_sleep = mocker.patch('main.time.sleep', return_value=None)

    bogo_thread = threading.Thread(target=main.bogo)
    bogo_thread.daemon = True
    bogo_thread.start()

    # Waiting for the bogo_thread to complete.
    # If it takes longer than 30s, the timeout will stop the thread.
    bogo_thread.join()

    # Assertions:
    assert main.sorted_flag, "sorted_flag should be True after bogo sort completes."
    assert main.isSorted(main.array), f"Array {main.array} should be sorted after bogo sort."
    assert main.shuffle_count > 0, "Shuffle count should have increased."
    assert mock_sleep.call_count > 0, "time.sleep should have been called at least once, indicating shuffling occurred."

# Testing if the sorted array correctly flags isSorted as True
def test_isSorted_sorted_array():
    assert main.isSorted([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]) == True, "Sorted array should return True."

# Testing if the unsorted array correctly flags isSorted as False
def test_isSorted_unsorted_array():
    assert main.isSorted([1, 3, 2, 5, 4, 6, 12, 8, 9, 10, 11, 7]) == False, "Unsorted array should return False."
    