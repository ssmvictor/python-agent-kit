# Polars Patterns

> High-performance DataFrame processing with polars.
> **Rust-powered, lazy evaluation, type-safe by design.**

---

## 1. Why Polars?

| Aspect | Polars Advantage |
|--------|------------------|
| **Performance** | 10-100x faster than pandas for large datasets |
| **Memory** | Zero-copy, columnar storage |
| **Lazy Eval** | Query optimization before execution |
| **Type Safety** | Rust backend enforces types |
| **Parallelism** | Multi-threaded by default |

### When to Use Polars

```
Use polars when:
├── Dataset > 1GB
├── Complex aggregations
├── Performance critical
├── Lazy evaluation beneficial
└── Type safety desired

Stick with pandas when:
├── Quick exploratory analysis
├── sklearn integration needed
├── Team familiarity matters
└── Rich ecosystem required
```

---

## 2. Lazy vs Eager Mode

### Understanding Lazy Evaluation

```python
import polars as pl

# Lazy mode - builds query plan, optimizes, then executes
lazy_result = (
    pl.scan_csv("large_file.csv")  # Returns LazyFrame
    .filter(pl.col("status") == "active")
    .group_by("region")
    .agg(pl.col("amount").sum().alias("total"))
    .collect()  # Execute optimized query
)

# Eager mode - executes immediately
eager_result = (
    pl.read_csv("large_file.csv")  # Returns DataFrame
    .filter(pl.col("status") == "active")
    .group_by("region")
    .agg(pl.col("amount").sum().alias("total"))
)
```

### Lazy Pipeline Pattern

```python
from typing import Self
import polars as pl

class LazyPipeline:
    """Type-safe lazy query builder."""
    
    def __init__(self, source: str | pl.LazyFrame) -> None:
        if isinstance(source, str):
            self._lf = pl.scan_csv(source)
        else:
            self._lf = source
    
    @property
    def lazy_frame(self) -> pl.LazyFrame:
        return self._lf
    
    def filter(self, expr: pl.Expr) -> Self:
        """Add filter expression."""
        self._lf = self._lf.filter(expr)
        return self
    
    def select(self, *columns: str | pl.Expr) -> Self:
        """Select columns."""
        self._lf = self._lf.select(columns)
        return self
    
    def with_column(self, expr: pl.Expr) -> Self:
        """Add computed column."""
        self._lf = self._lf.with_columns(expr)
        return self
    
    def group_by(self, *columns: str) -> 'GroupedPipeline':
        """Start groupby operation."""
        return GroupedPipeline(self._lf, list(columns))
    
    def collect(self) -> pl.DataFrame:
        """Execute query."""
        return self._lf.collect()
    
    def explain(self) -> str:
        """Show query plan."""
        return self._lf.explain()


class GroupedPipeline:
    """Grouped aggregation builder."""
    
    def __init__(self, lf: pl.LazyFrame, group_cols: list[str]) -> None:
        self._lf = lf
        self._group_cols = group_cols
        self._aggs: list[pl.Expr] = []
    
    def agg(self, *exprs: pl.Expr) -> 'GroupedPipeline':
        """Add aggregation expressions."""
        self._aggs.extend(exprs)
        return self
    
    def collect(self) -> pl.DataFrame:
        """Execute grouped query."""
        return (
            self._lf
            .group_by(self._group_cols)
            .agg(self._aggs)
            .collect()
        )


# Usage:
result = (
    LazyPipeline("sales.csv")
    .filter(pl.col("amount") > 100)
    .with_column(
        (pl.col("amount") * pl.col("quantity")).alias("total")
    )
    .group_by("region")
    .agg(
        pl.col("total").sum().alias("revenue"),
        pl.col("order_id").count().alias("num_orders")
    )
    .collect()
)
```

---

## 3. Expression Patterns

### Column Expressions

```python
import polars as pl

# Basic expressions
amount = pl.col("amount")
status = pl.col("status")
created = pl.col("created_at")

# Arithmetic
total = amount * pl.col("quantity")
with_tax = amount * 1.1

# String operations
upper_name = pl.col("name").str.to_uppercase()
email_domain = pl.col("email").str.split("@").list.get(1)

# Conditional
status_flag = pl.when(status == "active").then(1).otherwise(0)

# Date operations
year = created.dt.year()
month = created.dt.month()
days_ago = (pl.lit(datetime.now()) - created).dt.total_days()
```

### Reusable Expression Builders

```python
from typing import Literal
import polars as pl

class Expressions:
    """Factory for common expressions."""
    
    @staticmethod
    def is_null(column: str) -> pl.Expr:
        """Check if column is null."""
        return pl.col(column).is_null()
    
    @staticmethod
    def is_not_null(column: str) -> pl.Expr:
        """Check if column is not null."""
        return pl.col(column).is_not_null()
    
    @staticmethod
    def in_list(column: str, values: list) -> pl.Expr:
        """Check if column value in list."""
        return pl.col(column).is_in(values)
    
    @staticmethod
    def between(column: str, low: float, high: float) -> pl.Expr:
        """Check if value between range."""
        col = pl.col(column)
        return (col >= low) & (col <= high)
    
    @staticmethod
    def percentile(column: str, pct: float, alias: str | None = None) -> pl.Expr:
        """Calculate percentile."""
        expr = pl.col(column).quantile(pct)
        return expr.alias(alias) if alias else expr


# Usage:
(
    df.lazy()
    .filter(Expressions.is_not_null("order_id"))
    .filter(Expressions.between("amount", 100, 1000))
    .collect()
)
```

---

## 4. Schema Definition

```python
from dataclasses import dataclass
from typing import ClassVar
import polars as pl

@dataclass(frozen=True)
class ColumnDef:
    """Column definition with polars dtype."""
    name: str
    dtype: pl.DataType
    nullable: bool = True

class SalesSchema:
    """Schema definition for sales data."""
    
    ORDER_ID: ClassVar[ColumnDef] = ColumnDef("order_id", pl.Utf8, nullable=False)
    AMOUNT: ClassVar[ColumnDef] = ColumnDef("amount", pl.Float64)
    QUANTITY: ClassVar[ColumnDef] = ColumnDef("quantity", pl.Int32)
    STATUS: ClassVar[ColumnDef] = ColumnDef("status", pl.Utf8)
    CREATED_AT: ClassVar[ColumnDef] = ColumnDef("created_at", pl.Datetime)
    
    @classmethod
    def columns(cls) -> list[ColumnDef]:
        return [cls.ORDER_ID, cls.AMOUNT, cls.QUANTITY, cls.STATUS, cls.CREATED_AT]
    
    @classmethod
    def to_schema(cls) -> dict[str, pl.DataType]:
        """Get polars schema dict."""
        return {col.name: col.dtype for col in cls.columns()}
    
    @classmethod
    def validate(cls, df: pl.DataFrame) -> tuple[bool, list[str]]:
        """Validate DataFrame against schema."""
        errors = []
        for col in cls.columns():
            if col.name not in df.columns:
                errors.append(f"Missing column: {col.name}")
            elif df[col.name].dtype != col.dtype:
                errors.append(
                    f"Type mismatch in {col.name}: "
                    f"expected {col.dtype}, got {df[col.name].dtype}"
                )
        return len(errors) == 0, errors


# Usage with schema validation:
df = pl.read_csv("sales.csv", schema=SalesSchema.to_schema())
is_valid, errors = SalesSchema.validate(df)
```

---

## 5. Transform Patterns

### Method Chaining with Types

```python
from typing import Callable
import polars as pl

TransformFn = Callable[[pl.LazyFrame], pl.LazyFrame]

class DataTransformer:
    """Composable transformations for polars."""
    
    def __init__(self) -> None:
        self._transforms: list[tuple[str, TransformFn]] = []
    
    def add(self, name: str, fn: TransformFn) -> 'DataTransformer':
        """Add named transformation."""
        self._transforms.append((name, fn))
        return self
    
    def apply(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        """Apply all transformations."""
        result = lf
        for name, fn in self._transforms:
            result = fn(result)
        return result


# Common transforms as functions
def drop_nulls(columns: list[str]) -> TransformFn:
    """Create null-drop transform."""
    return lambda lf: lf.drop_nulls(columns)

def add_computed(name: str, expr: pl.Expr) -> TransformFn:
    """Create computed column transform."""
    return lambda lf: lf.with_columns(expr.alias(name))

def filter_by(expr: pl.Expr) -> TransformFn:
    """Create filter transform."""
    return lambda lf: lf.filter(expr)


# Usage:
transformer = (
    DataTransformer()
    .add("remove_nulls", drop_nulls(["order_id"]))
    .add("add_total", add_computed("total", pl.col("amount") * pl.col("qty")))
    .add("active_only", filter_by(pl.col("status") == "active"))
)

result = transformer.apply(df.lazy()).collect()
```

---

## 6. IO Operations

### Typed Reader/Writer

```python
from pathlib import Path
from typing import Protocol
import polars as pl

class PolarsReader(Protocol):
    """Protocol for data readers."""
    def read(self) -> pl.LazyFrame: ...

class CSVSource:
    """Lazy CSV reader with configuration."""
    
    def __init__(
        self,
        path: Path,
        schema: dict[str, pl.DataType] | None = None,
        skip_rows: int = 0,
        n_rows: int | None = None
    ) -> None:
        self._path = path
        self._schema = schema
        self._skip_rows = skip_rows
        self._n_rows = n_rows
    
    def read(self) -> pl.LazyFrame:
        """Scan CSV lazily."""
        return pl.scan_csv(
            self._path,
            schema=self._schema,
            skip_rows=self._skip_rows,
            n_rows=self._n_rows
        )

class ParquetSink:
    """Write DataFrame to Parquet."""
    
    def __init__(
        self,
        path: Path,
        compression: str = "zstd"
    ) -> None:
        self._path = path
        self._compression = compression
    
    def write(self, df: pl.DataFrame) -> int:
        """Write to parquet, return rows."""
        df.write_parquet(self._path, compression=self._compression)
        return len(df)
```

---

## 7. Pandas Interop

```python
import polars as pl
import pandas as pd

# From pandas to polars
pandas_df = pd.read_csv("data.csv")
polars_df = pl.from_pandas(pandas_df)

# From polars to pandas (when needed for sklearn, etc.)
pandas_result = polars_df.to_pandas()

# Best practice: Process in polars, export to pandas only when needed
class HybridProcessor:
    """Process in polars, export to pandas for ML."""
    
    def __init__(self, df: pl.DataFrame) -> None:
        self._df = df
    
    def transform(self) -> pl.DataFrame:
        """Heavy transformations in polars."""
        return (
            self._df.lazy()
            .filter(pl.col("status") == "active")
            .with_columns([
                (pl.col("a") * pl.col("b")).alias("product"),
                pl.col("date").dt.year().alias("year")
            ])
            .collect()
        )
    
    def to_sklearn_ready(self) -> pd.DataFrame:
        """Export to pandas for sklearn."""
        processed = self.transform()
        return processed.to_pandas()
```

---

## 8. Performance Tips

### Memory Management

```python
import polars as pl

# Use lazy mode for large files
lf = pl.scan_csv("huge_file.csv")  # No memory until collect()

# Select only needed columns early
lf = lf.select(["order_id", "amount"])  # Reduces memory

# Use streaming for very large files
result = (
    pl.scan_csv("huge_file.csv")
    .filter(pl.col("status") == "active")
    .collect(streaming=True)  # Process in chunks
)

# Check memory usage
print(df.estimated_size("mb"))
```

### Query Optimization

```python
# View optimized query plan
lf = (
    pl.scan_csv("data.csv")
    .filter(pl.col("a") > 10)
    .select(["a", "b"])
)

print(lf.explain())  # Shows optimized plan
print(lf.explain(optimized=False))  # Shows original plan
```

---

> **Remember**: Polars shines with lazy evaluation. Build your query, let the optimizer work, then collect once.
