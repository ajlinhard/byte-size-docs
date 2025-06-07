# PySpark Sub-Package Imports Cheat Sheet
Help for quickly remembering which packages have what in pyspark

## Core Spark Session & Context
```python
from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf
```

## DataFrame & SQL Operations
```python
from pyspark.sql import DataFrame, Row
from pyspark.sql.types import *  # All data types
from pyspark.sql.functions import *  # All built-in functions
```

## Specific Data Types
```python
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, 
    DoubleType, BooleanType, TimestampType, DateType,
    ArrayType, MapType, DecimalType, LongType
)
```

## Common Functions
```python
from pyspark.sql.functions import (
    col, lit, when, otherwise, concat, split, regexp_replace,
    sum, count, avg, max, min, first, last,
    collect_list, collect_set, explode, array_contains,
    date_format, current_timestamp, datediff, to_date,
    row_number, rank, dense_rank, lag, lead
)
```

## Window Functions
```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, rank, dense_rank, lag, lead
```

## Streaming
```python
from pyspark.streaming import StreamingContext
from pyspark.sql.streaming import DataStreamReader, DataStreamWriter
```

## Machine Learning
```python
# MLlib (RDD-based)
from pyspark.mllib.classification import LogisticRegressionWithLBFGS
from pyspark.mllib.regression import LinearRegressionWithSGD
from pyspark.mllib.clustering import KMeans

# ML (DataFrame-based)
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import VectorAssembler, StringIndexer, OneHotEncoder
from pyspark.ml.classification import LogisticRegression, RandomForestClassifier
from pyspark.ml.regression import LinearRegression, RandomForestRegressor
from pyspark.ml.clustering import KMeans as MLKMeans
from pyspark.ml.evaluation import BinaryClassificationEvaluator, RegressionEvaluator
```

## Configuration & Utilities
```python
from pyspark.sql.utils import AnalysisException
from pyspark.sql.catalog import Catalog
from pyspark.serializers import MarshalSerializer, PickleSerializer
```

## Broadcast & Accumulators
```python
from pyspark.broadcast import Broadcast
from pyspark.util import AccumulatorParam
```

## Resource Management
```python
from pyspark.resource import ResourceProfile, TaskResourceRequests, ExecutorResourceRequests
```

## Common Import Patterns

### Minimal Setup
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit
from pyspark.sql.types import StringType, IntegerType
```

### Data Analysis Setup
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
```

### ML Pipeline Setup
```python
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
```

### Complete Import (Development/Testing)
```python
from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.ml import *
from pyspark.ml.feature import *
from pyspark.ml.classification import *
from pyspark.ml.regression import *
```
