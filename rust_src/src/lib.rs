use pyo3::prelude::*;
use rand::rngs::SmallRng;
use rand::seq::SliceRandom;
use rand::SeedableRng;

#[pyfunction]
fn is_sorted(arr: Vec<i32>) -> bool {
    is_sorted_internal(&arr)
}

#[pyfunction]
fn bogo_batch(py: Python<'_>, mut arr: Vec<i32>, batch_size: usize) -> (Vec<i32>, usize, bool) {
    py.allow_threads(move || {
        let mut rng = SmallRng::from_entropy();
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
    })
}

#[inline]
fn is_sorted_internal(arr: &[i32]) -> bool {
    arr.windows(2).all(|w| w[0] <= w[1])
}

#[pymodule]
fn bogo_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_sorted, m)?)?;
    m.add_function(wrap_pyfunction!(bogo_batch, m)?)?;
    Ok(())
}
