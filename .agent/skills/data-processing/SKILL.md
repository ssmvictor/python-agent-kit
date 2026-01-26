---
name: data-processing
description: Python data processing principles and patterns. pandas, polars, ETL pipelines, data validation. Teaches OOP-first approach with strong typing.
tier: standard
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Data Processing Skill

> Python data processing principles for enterprise environments.
> **OOP-first, strongly-typed, production-ready.**

---

## ⚠️ How to Use This Skill

This skill teaches **decision-making principles** for data processing, not fixed code to copy.

- ASK about data scale before choosing library
- Choose pandas vs polars based on CONTEXT
- Always enforce type hints and Pydantic models

---

## 1. Library Selection (2025)

### Decision Tree

```
What's your data size and use case?
│
├── < 1GB, exploratory / ad-hoc
│   └── pandas (familiar, rich ecosystem)
│
├── 1GB - 100GB, performance critical
│   └── polars (fast, memory efficient)
│
├── > 100GB, distributed
│   └── dask / spark (parallel processing)
│
├── Real-time streaming
│   └── faust / kafka-python
│
└── ML feature engineering
    └── polars (lazy eval) → pandas (sklearn compat)
```

### Comparison Principles

| Factor | pandas | polars | dask |
|--------|--------|--------|------|
| **Best for** | General analysis | Performance | Scale-out |
| **Memory** | High (copies) | Low (zero-copy) | Distributed |
| **API style** | Mutable | Immutable | pandas-like |
| **Lazy eval** | No | Yes | Yes |
| **Type safety** | Weak | Strong | Weak |
| **Learning curve** | Low | Medium | Medium |

### Selection Questions to Ask:

1. How large is the dataset? (rows × columns)
2. Is this a one-time script or recurring pipeline?
3. What's the target environment? (local / server / cloud)
4. Does the team know polars?

---

## 2. OOP Patterns for Data Processing

### Pattern Philosophy

```
Every data operation should be:
├── Encapsulated in a class
├── Typed with generics where applicable
├── Testable in isolation
├── Composable with other operations
└── Logged for observability
```

### Base Processor Pattern

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProcessingMetrics:
    """Metrics from a processing run."""
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: datetime | None = None
    rows_input: int = 0
    rows_output: int = 0
    errors: list[str] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        if self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return 0.0

T = TypeVar('T', pd.DataFrame, 'pl.DataFrame')

class BaseProcessor(ABC, Generic[T]):
    """Abstract base for all data processors."""
    
    def __init__(self, name: str) -> None:
        self.name = name
        self._metrics = ProcessingMetrics()
    
    @abstractmethod
    def _transform(self, data: T) -> T:
        """Core transformation logic."""
        ...
    
    def process(self, data: T) -> tuple[T, ProcessingMetrics]:
        """Execute processing with metrics collection."""
        self._metrics = ProcessingMetrics()
        self._metrics.rows_input = len(data)
        
        logger.info(f"[{self.name}] Starting processing of {len(data)} rows")
        
        try:
            result = self._transform(data)
            self._metrics.rows_output = len(result)
        except Exception as e:
            self._metrics.errors.append(str(e))
            raise
        finally:
            self._metrics.ended_at = datetime.now()
            logger.info(f"[{self.name}] Completed in {self._metrics.duration_seconds:.2f}s")
        
        return result, self._metrics
```

### Pipeline Composition Pattern

```python
from typing import Callable, Sequence
import pandas as pd

class DataPipeline:
    """Composable pipeline of processors."""
    
    def __init__(self, name: str) -> None:
        self.name = name
        self._processors: list[BaseProcessor] = []
    
    def add(self, processor: BaseProcessor) -> 'DataPipeline':
        """Add processor to pipeline (fluent API)."""
        self._processors.append(processor)
        return self
    
    def execute(self, data: pd.DataFrame) -> pd.DataFrame:
        """Execute all processors in sequence."""
        result = data.copy()
        for proc in self._processors:
            result, _ = proc.process(result)
        return result


# Usage:
pipeline = (
    DataPipeline("sales_etl")
    .add(CleansingProcessor())
    .add(EnrichmentProcessor())
    .add(AggregationProcessor())
)

output = pipeline.execute(raw_data)
```

---

## 3. Type Hints Strategy

### DataFrame Typing

```python
from typing import TypedDict, Literal
import pandas as pd

# Option 1: TypedDict for row structure
class SalesRow(TypedDict):
    order_id: str
    amount: float
    status: Literal['pending', 'completed', 'cancelled']

# Option 2: Pydantic for validation
from pydantic import BaseModel, Field

class SalesRecord(BaseModel):
    order_id: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    status: Literal['pending', 'completed', 'cancelled']

# Function signatures
def process_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Process sales DataFrame."""
    ...

def validate_rows(df: pd.DataFrame, model: type[BaseModel]) -> list[BaseModel]:
    """Validate rows against Pydantic model."""
    ...
```

### Column Constants

```python
from typing import Final

class SalesColumns:
    """Column names as typed constants."""
    ORDER_ID: Final[str] = 'order_id'
    AMOUNT: Final[str] = 'amount'
    STATUS: Final[str] = 'status'
    CREATED_AT: Final[str] = 'created_at'
    
    @classmethod
    def required(cls) -> list[str]:
        return [cls.ORDER_ID, cls.AMOUNT, cls.STATUS]
```

---

## 4. Data Validation Patterns

### Schema Validation with Pandera

```python
import pandera as pa
from pandera.typing import DataFrame, Series

class SalesSchema(pa.DataFrameModel):
    """Validated sales DataFrame schema."""
    
    order_id: Series[str] = pa.Field(str_length={'min_value': 1})
    amount: Series[float] = pa.Field(gt=0)
    status: Series[str] = pa.Field(isin=['pending', 'completed', 'cancelled'])
    
    class Config:
        strict = True
        coerce = True

@pa.check_types
def process_sales(df: DataFrame[SalesSchema]) -> DataFrame[SalesSchema]:
    """Process validated sales data."""
    return df[df['status'] == 'completed']
```

### Custom Validator Class

```python
from dataclasses import dataclass
from typing import Callable
import pandas as pd

@dataclass
class ValidationRule:
    """Single validation rule."""
    name: str
    check: Callable[[pd.DataFrame], bool]
    error_message: str

class DataValidator:
    """Validate DataFrame against rules."""
    
    def __init__(self) -> None:
        self._rules: list[ValidationRule] = []
    
    def add_rule(self, rule: ValidationRule) -> 'DataValidator':
        self._rules.append(rule)
        return self
    
    def validate(self, df: pd.DataFrame) -> tuple[bool, list[str]]:
        """Run all validations, return (is_valid, errors)."""
        errors = []
        for rule in self._rules:
            if not rule.check(df):
                errors.append(f"[{rule.name}] {rule.error_message}")
        return len(errors) == 0, errors


# Usage:
validator = (
    DataValidator()
    .add_rule(ValidationRule(
        name="no_nulls",
        check=lambda df: df['order_id'].notna().all(),
        error_message="order_id contains null values"
    ))
    .add_rule(ValidationRule(
        name="positive_amounts",
        check=lambda df: (df['amount'] > 0).all(),
        error_message="amount must be positive"
    ))
)

is_valid, errors = validator.validate(sales_df)
```

---

## 5. ETL Pipeline Patterns

### Extract-Transform-Load Class

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from pathlib import Path
import pandas as pd

Source = TypeVar('Source')
Target = TypeVar('Target')

class ETLPipeline(ABC, Generic[Source, Target]):
    """Generic ETL pipeline base."""
    
    @abstractmethod
    def extract(self, source: Source) -> pd.DataFrame:
        """Extract data from source."""
        ...
    
    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transform extracted data."""
        ...
    
    @abstractmethod
    def load(self, data: pd.DataFrame, target: Target) -> int:
        """Load data to target, return rows loaded."""
        ...
    
    def run(self, source: Source, target: Target) -> int:
        """Execute full ETL pipeline."""
        raw = self.extract(source)
        transformed = self.transform(raw)
        return self.load(transformed, target)


class FileToDBPipeline(ETLPipeline[Path, str]):
    """Concrete ETL: CSV file to database table."""
    
    def __init__(self, connection_string: str) -> None:
        self._conn_str = connection_string
    
    def extract(self, source: Path) -> pd.DataFrame:
        return pd.read_csv(source)
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        # Add transformations
        return data.dropna()
    
    def load(self, data: pd.DataFrame, target: str) -> int:
        # Load to database
        from sqlalchemy import create_engine
        engine = create_engine(self._conn_str)
        data.to_sql(target, engine, if_exists='append', index=False)
        return len(data)
```

---

## 6. Error Handling

### Typed Exceptions

```python
from dataclasses import dataclass

class DataProcessingError(Exception):
    """Base exception for data processing."""
    pass

@dataclass
class ValidationError(DataProcessingError):
    """Data validation failed."""
    column: str
    message: str
    
    def __str__(self) -> str:
        return f"Validation failed on '{self.column}': {self.message}"

@dataclass  
class SchemaError(DataProcessingError):
    """Schema mismatch."""
    expected: list[str]
    actual: list[str]
    
    def __str__(self) -> str:
        missing = set(self.expected) - set(self.actual)
        return f"Missing columns: {missing}"
```

---

## 7. Anti-Patterns to Avoid

### ❌ DON'T:

```python
# Chained operations without intermediate variables
df = df.drop('col1').fillna(0).groupby('id').sum().reset_index().rename(...)

# Magic column names scattered everywhere
df['ordem_id']  # Typo risk
df['ORDEM_ID']  # Case mismatch

# Unhandled exceptions
df = pd.read_csv(path)  # File might not exist

# Global DataFrames
raw_data = pd.read_csv('data.csv')  # Module-level state
```

### ✅ DO:

```python
# Clear step-by-step with named results
cleaned = df.drop(columns=['col1'])
filled = cleaned.fillna(0)
grouped = filled.groupby('id').sum()
result = grouped.reset_index()

# Type-safe column constants
from constants import Columns
df[Columns.ORDER_ID]

# Explicit error handling
try:
    df = pd.read_csv(path)
except FileNotFoundError as e:
    logger.error(f"File not found: {path}")
    raise DataProcessingError(f"Source file missing: {path}") from e

# Encapsulated in classes
class SalesProcessor:
    def __init__(self, raw_data: pd.DataFrame) -> None:
        self._data = raw_data.copy()
```

---

## 📚 References

See detailed patterns in:
- [pandas-patterns.md](./references/pandas-patterns.md)
- [polars-patterns.md](./references/polars-patterns.md)
- [etl-pipelines.md](./references/etl-pipelines.md)

---

## ✅ Decision Checklist

Before implementing data processing:

- [ ] Chose library based on data size and context?
- [ ] Defined column constants (no magic strings)?
- [ ] Created Pydantic/Pandera schemas for validation?
- [ ] Encapsulated logic in classes?
- [ ] Added type hints to all functions?
- [ ] Implemented error handling with typed exceptions?
- [ ] Added logging for observability?
- [ ] Wrote tests for transformations?

---

> **Remember**: Data processing code runs in production. Make it typed, tested, and maintainable.
