## Sample API return format required for the front-end panel

### 1.1 `load_data(file_path: str) -> dict`

Loads and preprocesses the input CSV file.

*   **Parameters:**
    *   `file_path`: The absolute path to the input CSV file.
*   **Returns:**
    *   A dictionary containing the preprocessed data and metadata:
        ```json
        {
          "status": "success" or "error",
          "message": "A message indicating the status.",
          "data": {
            "jobs": 40,
            "nvar": 100,
            "column_titles": ["col1", "col2", ...],
            "row_titles": ["row1", "row2", ...],
          }
        }
        ```
*   **Error Handling:**
    *   If the file is not found, returns a status of "error" with an appropriate message.
    *   If the file format is invalid, returns a status of "error" with a message detailing the issue.

### 1.2 `run_analysis(data: dict, options: dict) -> dict`

Runs the entropy analysis on the loaded data with the specified options.

*   **Parameters:**
    *   `data` (dict): The data dictionary returned by `load_data`.
    *   `options` (dict): A dictionary of processing options. The `min_groups` and `max_groups` values are user-configurable, with a supported range of 2 to 84.
        
        ```json
        {
          "min_groups": 2,
          "max_groups": 20,
          "permutations": True,
          "row_proportions": True
        }
        ```
*   **Returns:**
    *   A dictionary containing the analysis results:
        ```json
        {
          "status": "success" or "error",
          "message": "A message indicating the status.",
          "results": [
            {
              "group_number": 2,
              "ch_statistic": 123.45,
              "rs_statistic": 85.67,
              "group_means": [[...], [...]],
              "group_members": [1, 2, 1, ...],
              "output_files": {
                "composite": "/path/to/2_groups.csv",
                "individual": "/path/to/2_groups_detail.csv"
              }
            },
            ...
          ]
        }
        ```

### 1.3 `get_default_options() -> dict`

Returns the default processing options.

*   **Returns:**
    *   A dictionary of default options:
        ```json
        {
          "min_groups": 2,
          "max_groups": 20,
          "permutations": True,
          "row_proportions": True
        }
        ```
