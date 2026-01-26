use pyo3::prelude::*;
use rand::seq::SliceRandom;
use rand::thread_rng;

#[pyfunction]
fn is_sorted(arr: Vec<i32>) -> bool {
    is_sorted_internal(&arr)
}

#[pyfunction]
fn bogo_batch(mut arr: Vec<i32>, batch_size: usize) -> (Vec<i32>, usize, bool) {
    let mut rng = thread_rng();
    let mut shuffles = 0;

    for _ in 0..batch_size {
        if is_sorted_internal(&arr) {
            return (arr, shuffles, true);
        }
        arr.shuffle(&mut rng);
        shuffles += 1;
    }

    let sorted = is_sorted_internal(&arr);
    (arr, shuffles, sorted)
}

fn is_sorted_internal(arr: &[i32]) -> bool {
    for i in 0..arr.len() - 1 {
        if arr[i] > arr[i + 1] {
            return false;
        }
    }
    true
}

#[pymodule]
fn bogo_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_sorted, m)?)?;
    m.add_function(wrap_pyfunction!(bogo_batch, m)?)?;
    Ok(())
}
