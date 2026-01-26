# Pandas Patterns

> OOP-first patterns for pandas DataFrame processing.
> **Type-safe, composable, production-ready.**

---

## 1. Typed DataFrame Wrapper

```python
from typing import Generic, TypeVar, Iterator
from dataclasses import dataclass
import pandas as pd
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class TypedDataFrame(Generic[T]):
    """Type-safe wrapper around pandas DataFrame."""
    
    def __init__(self, df: pd.DataFrame, model: type[T]) -> None:
        self._df = df
        self._model = model
        self._validate_columns()
    
    def _validate_columns(self) -> None:
        """Ensure DataFrame has required columns."""
        required = set(self._model.model_fields.keys())
        actual = set(self._df.columns)
        missing = required - actual
        if missing:
            raise ValueError(f"Missing columns: {missing}")
    
    @property
    def df(self) -> pd.DataFrame:
        """Access underlying DataFrame."""
        return self._df
    
    def __len__(self) -> int:
        return len(self._df)
    
    def __iter__(self) -> Iterator[T]:
        """Iterate as typed models."""
        for _, row in self._df.iterrows():
            yield self._model(**row.to_dict())
    
    def filter(self, condition: pd.Series) -> 'TypedDataFrame[T]':
        """Return filtered TypedDataFrame."""
        return TypedDataFrame(self._df[condition], self._model)
    
    def to_models(self) -> list[T]:
        """Convert all rows to Pydantic models."""
        return list(self)


# Usage:
class SalesRecord(BaseModel):
    order_id: str
    amount: float
    status: str

typed_df = TypedDataFrame(raw_df, SalesRecord)
for record in typed_df:
    print(record.amount)  # Fully typed!
```

---

## 2. Column Registry Pattern

```python
from typing import Final, ClassVar
from dataclasses import dataclass
from enum import Enum

class ColumnType(str, Enum):
    STRING = 'string'
    NUMERIC = 'numeric'
    DATETIME = 'datetime'
    CATEGORICAL = 'categorical'

@dataclass(frozen=True)
class Column:
    """Immutable column definition."""
    name: str
    dtype: ColumnType
    nullable: bool = False
    
    def __str__(self) -> str:
        return self.name

class SalesColumns:
    """Centralized column registry for sales data."""
    
    ORDER_ID: ClassVar[Column] = Column('order_id', ColumnType.STRING)
    AMOUNT: ClassVar[Column] = Column('amount', ColumnType.NUMERIC)
    STATUS: ClassVar[Column] = Column('status', ColumnType.CATEGORICAL)
    CREATED_AT: ClassVar[Column] = Column('created_at', ColumnType.DATETIME)
    
    @classmethod
    def all(cls) -> list[Column]:
        return [cls.ORDER_ID, cls.AMOUNT, cls.STATUS, cls.CREATED_AT]
    
    @classmethod
    def names(cls) -> list[str]:
        return [col.name for col in cls.all()]


# Usage:
df[[SalesColumns.ORDER_ID.name, SalesColumns.AMOUNT.name]]
```

---

## 3. Transform Chain Pattern

```python
from typing import Callable, Self
import pandas as pd

TransformFn = Callable[[pd.DataFrame], pd.DataFrame]

class TransformChain:
    """Fluent API for DataFrame transformations."""
    
    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df
        self._steps: list[tuple[str, TransformFn]] = []
    
    def add(self, name: str, fn: TransformFn) -> Self:
        """Add named transformation step."""
        self._steps.append((name, fn))
        return self
    
    def drop_columns(self, columns: list[str]) -> Self:
        """Drop specified columns."""
        return self.add(
            f"drop_{len(columns)}_cols",
            lambda df: df.drop(columns=columns, errors='ignore')
        )
    
    def fill_nulls(self, column: str, value: any) -> Self:
        """Fill nulls in column."""
        return self.add(
            f"fill_{column}",
            lambda df: df.assign(**{column: df[column].fillna(value)})
        )
    
    def filter_rows(self, condition: Callable[[pd.DataFrame], pd.Series]) -> Self:
        """Filter rows by condition."""
        return self.add(
            "filter",
            lambda df: df[condition(df)]
        )
    
    def execute(self, log: bool = False) -> pd.DataFrame:
        """Execute all transformations."""
        result = self._df.copy()
        for name, fn in self._steps:
            if log:
                print(f"Executing: {name}")
            result = fn(result)
        return result


# Usage:
result = (
    TransformChain(df)
    .drop_columns(['temp_col', 'debug_col'])
    .fill_nulls('amount', 0)
    .filter_rows(lambda df: df['status'] == 'active')
    .execute()
)
```

---

## 4. Aggregation Builder

```python
from typing import Literal
from dataclasses import dataclass, field
import pandas as pd

AggFunc = Literal['sum', 'mean', 'count', 'min', 'max', 'std']

@dataclass
class AggSpec:
    """Aggregation specification."""
    column: str
    function: AggFunc
    alias: str | None = None
    
    @property
    def output_name(self) -> str:
        return self.alias or f"{self.column}_{self.function}"

class AggregationBuilder:
    """Build complex aggregations with fluent API."""
    
    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df
        self._group_cols: list[str] = []
        self._aggs: list[AggSpec] = []
    
    def group_by(self, *columns: str) -> 'AggregationBuilder':
        """Set grouping columns."""
        self._group_cols = list(columns)
        return self
    
    def agg(self, column: str, func: AggFunc, alias: str | None = None) -> 'AggregationBuilder':
        """Add aggregation."""
        self._aggs.append(AggSpec(column, func, alias))
        return self
    
    def sum(self, column: str, alias: str | None = None) -> 'AggregationBuilder':
        return self.agg(column, 'sum', alias)
    
    def mean(self, column: str, alias: str | None = None) -> 'AggregationBuilder':
        return self.agg(column, 'mean', alias)
    
    def count(self, column: str, alias: str | None = None) -> 'AggregationBuilder':
        return self.agg(column, 'count', alias)
    
    def execute(self) -> pd.DataFrame:
        """Execute aggregation."""
        agg_dict = {
            spec.column: spec.function 
            for spec in self._aggs
        }
        
        result = self._df.groupby(self._group_cols).agg(agg_dict).reset_index()
        
        # Rename columns
        rename_map = {
            spec.column: spec.output_name 
            for spec in self._aggs 
            if spec.alias
        }
        return result.rename(columns=rename_map)


# Usage:
summary = (
    AggregationBuilder(sales_df)
    .group_by('region', 'product')
    .sum('amount', alias='total_sales')
    .mean('amount', alias='avg_sale')
    .count('order_id', alias='num_orders')
    .execute()
)
```

---

## 5. Merge/Join Builder

```python
from typing import Literal
import pandas as pd

JoinType = Literal['inner', 'left', 'right', 'outer']

class JoinBuilder:
    """Type-safe DataFrame join builder."""
    
    def __init__(self, left: pd.DataFrame) -> None:
        self._left = left
        self._right: pd.DataFrame | None = None
        self._on: list[str] = []
        self._how: JoinType = 'inner'
        self._suffixes: tuple[str, str] = ('_left', '_right')
    
    def with_df(self, right: pd.DataFrame) -> 'JoinBuilder':
        """Set right DataFrame."""
        self._right = right
        return self
    
    def on(self, *columns: str) -> 'JoinBuilder':
        """Set join columns."""
        self._on = list(columns)
        return self
    
    def how(self, join_type: JoinType) -> 'JoinBuilder':
        """Set join type."""
        self._how = join_type
        return self
    
    def suffixes(self, left: str, right: str) -> 'JoinBuilder':
        """Set column suffixes for overlapping names."""
        self._suffixes = (left, right)
        return self
    
    def execute(self) -> pd.DataFrame:
        """Execute join."""
        if self._right is None:
            raise ValueError("Right DataFrame not set. Call with_df() first.")
        
        return pd.merge(
            self._left,
            self._right,
            on=self._on,
            how=self._how,
            suffixes=self._suffixes
        )


# Usage:
result = (
    JoinBuilder(orders_df)
    .with_df(customers_df)
    .on('customer_id')
    .how('left')
    .execute()
)
```

---

## 6. IO Operations Pattern

```python
from pathlib import Path
from typing import Protocol
import pandas as pd

class DataReader(Protocol):
    """Protocol for data readers."""
    def read(self) -> pd.DataFrame: ...

class DataWriter(Protocol):
    """Protocol for data writers."""
    def write(self, df: pd.DataFrame) -> int: ...

class CSVReader:
    """Read CSV files with configuration."""
    
    def __init__(
        self,
        path: Path,
        encoding: str = 'utf-8',
        separator: str = ',',
        parse_dates: list[str] | None = None
    ) -> None:
        self._path = path
        self._encoding = encoding
        self._separator = separator
        self._parse_dates = parse_dates or []
    
    def read(self) -> pd.DataFrame:
        """Read CSV to DataFrame."""
        return pd.read_csv(
            self._path,
            encoding=self._encoding,
            sep=self._separator,
            parse_dates=self._parse_dates
        )

class ExcelWriter:
    """Write DataFrames to Excel."""
    
    def __init__(
        self,
        path: Path,
        sheet_name: str = 'Sheet1',
        index: bool = False
    ) -> None:
        self._path = path
        self._sheet_name = sheet_name
        self._index = index
    
    def write(self, df: pd.DataFrame) -> int:
        """Write DataFrame to Excel, return rows written."""
        df.to_excel(
            self._path,
            sheet_name=self._sheet_name,
            index=self._index
        )
        return len(df)
```

---

## 7. Performance Tips

### Memory Optimization

```python
import pandas as pd

def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Reduce memory by optimizing dtypes."""
    result = df.copy()
    
    for col in result.select_dtypes(include=['int64']).columns:
        result[col] = pd.to_numeric(result[col], downcast='integer')
    
    for col in result.select_dtypes(include=['float64']).columns:
        result[col] = pd.to_numeric(result[col], downcast='float')
    
    for col in result.select_dtypes(include=['object']).columns:
        num_unique = result[col].nunique()
        if num_unique / len(result) < 0.5:  # < 50% unique
            result[col] = result[col].astype('category')
    
    return result
```

### Chunked Processing

```python
from typing import Iterator, Callable
import pandas as pd

def process_in_chunks(
    path: Path,
    chunk_size: int,
    processor: Callable[[pd.DataFrame], pd.DataFrame]
) -> Iterator[pd.DataFrame]:
    """Process large file in chunks."""
    reader = pd.read_csv(path, chunksize=chunk_size)
    for chunk in reader:
        yield processor(chunk)
```

---

> **Remember**: pandas is powerful but can be memory-hungry. Use typed wrappers and chunked processing for production workloads.
