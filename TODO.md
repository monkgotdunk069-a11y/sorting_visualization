# TODO for Adding Timing and Comparison to Sorting Visualizer

- [x] Add a time label to the control panel UI to display the time taken for the current sort.
- [x] Modify the `__init__` method to initialize timing variables and store the original array.
- [x] Update `load_data` and `generate_random` to save a copy of the original array.
- [x] Modify `start_sorting` to record the start time before beginning the sort.
- [x] Modify `animate` to calculate and update the time label when sorting completes.
- [x] Add a "Compare All" button to the control panel next to the "SORT" button.
- [x] Implement the `compare_all` method to run all algorithms sequentially on the original array, collect their execution times (without animation delays for speed), and display a comparison in a messagebox.
- [x] Test the individual sort timing and comparison feature to ensure accuracy.
