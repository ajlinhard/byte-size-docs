# PyTest Util Packages

## PySpark - testing.utils
The submodule `pyspark.testing.utils` was **introduced officially in PySpark version 3.5.0**, as part of the larger integration of built-in testing utilities in PySpark[1]. Although a `testing` package existed in the source code for prior versions, it was not included in built PySpark distributions before 3.5.0, meaning it could not be imported unless building directly from source[1].

- **Creation (source code presence):** The folder appeared in the PySpark repository prior to 3.5.0, but was not packaged and shipped in published PySpark distributions.
- **Official release (available for import via installation):** PySpark 3.5.0, released in late 2023, was the first version where `pyspark.testing.utils` was available in the standard PySpark distribution[2][1].

This means while the code for `pyspark.testing.utils` predates version 3.5.0, it was only made accessible as an importable module with this official release.

### Documentation
- [Apache Spark Testing Utils Offical Release](https://spark.apache.org/releases/spark-release-3-5-0.html)
- [PySpark Testing Util API](https://spark.apache.org/docs/3.5.1/api/python/_modules/pyspark/testing/utils.html)
- [Github Example](https://github.com/apache/spark/blob/master/python/pyspark/sql/tests/test_dataframe.py)

## Pandas Testing Utils
Yes, there is a similar approach for testing **pandas DataFrames**: the pandas library provides a set of dedicated testing utilities, most notably the function **pandas.testing.assert_frame_equal**[2][6][1]. This is the standard tool used in unit tests to compare two DataFrames and identify any differences.

Key details:
- **assert_frame_equal** checks if two DataFrames are equal across values, types, index, columns, and allows for strictness controls through parameters like `check_dtype`, `check_exact`, etc.[2][1]
- There are analogous functions for Series (**assert_series_equal**) and Indexes (**assert_index_equal**)[1].
- These utilities are intended for use in unit testing and are part of the public pandas API (import from `pandas.testing`).
- For more readable test output, third-party tools like **beavis** exist to supplement pandas' built-in test functions[3][7].

Example usage:
```python
import pandas as pd
from pandas.testing import assert_frame_equal

expected = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
result = your_function_under_test()
assert_frame_equal(result, expected)
```
This ensures strict, reliable testing of DataFrame outputs similar to what `pyspark.testing.utils` provides for PySpark[1][2][3].

[How to Unit Test Pandas Guide](https://dev.to/emotta/pandas-code-testing-101-a-beginners-guide-for-python-developers-449m)
[Pandas Official Docs - assert-data-frame](https://pandas.pydata.org/docs/reference/api/pandas.testing.assert_frame_equal.html)
[Pandas Official Docs](https://pandas.pydata.org/docs/reference/testing.html)
[6] https://pandas.pydata.org/pandas-docs/version/1.4.4/reference/general_utility_functions.html
[7] https://www.mungingdata.com/pandas/unit-testing-pandas/
[8] https://coderbook.com/@marcus/how-to-mock-and-unit-test-with-pandas/
