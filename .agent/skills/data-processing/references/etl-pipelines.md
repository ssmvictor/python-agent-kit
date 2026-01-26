# ETL Pipelines

> Enterprise-grade Extract-Transform-Load patterns.
> **Typed, observable, recoverable.**

---

## 1. ETL Architecture Patterns

### Decision Tree

```
What's your ETL complexity?
│
├── Simple script (one-time)
│   └── Functional pipeline with error handling
│
├── Recurring job (daily/hourly)
│   └── Class-based processor + scheduler
│
├── Complex workflow (multi-step, dependencies)
│   └── DAG orchestration (Prefect/Dagster)
│
├── Real-time / streaming
│   └── Event-driven (Kafka/Faust)
│
└── Enterprise (audit, lineage, retries)
    └── Full orchestration framework
```

---

## 2. Base ETL Classes

### Generic ETL Pipeline

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class PipelineResult:
    """Result of ETL pipeline execution."""
    status: PipelineStatus
    started_at: datetime
    ended_at: datetime | None = None
    rows_extracted: int = 0
    rows_transformed: int = 0
    rows_loaded: int = 0
    errors: list[str] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        if self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return 0.0

Source = TypeVar('Source')
Target = TypeVar('Target')
Data = TypeVar('Data')

class ETLPipeline(ABC, Generic[Source, Target, Data]):
    """Generic ETL pipeline with metrics and error handling."""
    
    def __init__(self, name: str) -> None:
        self.name = name
        self._result = PipelineResult(
            status=PipelineStatus.PENDING,
            started_at=datetime.now()
        )
    
    @abstractmethod
    def extract(self, source: Source) -> Data:
        """Extract data from source."""
        ...
    
    @abstractmethod
    def transform(self, data: Data) -> Data:
        """Transform extracted data."""
        ...
    
    @abstractmethod
    def load(self, data: Data, target: Target) -> int:
        """Load data to target, return rows loaded."""
        ...
    
    def run(self, source: Source, target: Target) -> PipelineResult:
        """Execute full ETL pipeline with error handling."""
        self._result = PipelineResult(
            status=PipelineStatus.RUNNING,
            started_at=datetime.now()
        )
        
        try:
            logger.info(f"[{self.name}] Starting extraction")
            raw_data = self.extract(source)
            self._result.rows_extracted = len(raw_data)
            
            logger.info(f"[{self.name}] Extracted {self._result.rows_extracted} rows")
            
            logger.info(f"[{self.name}] Starting transformation")
            transformed = self.transform(raw_data)
            self._result.rows_transformed = len(transformed)
            
            logger.info(f"[{self.name}] Starting load")
            self._result.rows_loaded = self.load(transformed, target)
            
            self._result.status = PipelineStatus.SUCCESS
            logger.info(f"[{self.name}] Pipeline completed successfully")
            
        except Exception as e:
            self._result.status = PipelineStatus.FAILED
            self._result.errors.append(str(e))
            logger.error(f"[{self.name}] Pipeline failed: {e}")
            raise
        
        finally:
            self._result.ended_at = datetime.now()
        
        return self._result
```

---

## 3. Concrete ETL Implementations

### CSV to Database

```python
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, Engine

class CSVToDBPipeline(ETLPipeline[Path, str, pd.DataFrame]):
    """ETL: CSV file to database table."""
    
    def __init__(
        self,
        name: str,
        connection_string: str,
        if_exists: str = 'append'
    ) -> None:
        super().__init__(name)
        self._engine: Engine = create_engine(connection_string)
        self._if_exists = if_exists
    
    def extract(self, source: Path) -> pd.DataFrame:
        """Read CSV file."""
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        return pd.read_csv(source)
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply transformations."""
        # Override in subclass for specific transforms
        return data.dropna()
    
    def load(self, data: pd.DataFrame, target: str) -> int:
        """Insert into database table."""
        data.to_sql(
            target,
            self._engine,
            if_exists=self._if_exists,
            index=False
        )
        return len(data)


# Usage:
pipeline = CSVToDBPipeline(
    name="sales_import",
    connection_string="postgresql://user:pass@host/db"
)
result = pipeline.run(
    source=Path("data/sales.csv"),
    target="sales_staging"
)
print(f"Loaded {result.rows_loaded} rows in {result.duration_seconds:.2f}s")
```

### Database to Database

```python
from dataclasses import dataclass

@dataclass
class DBSource:
    """Database source configuration."""
    connection_string: str
    query: str

@dataclass
class DBTarget:
    """Database target configuration."""
    connection_string: str
    table: str
    if_exists: str = 'append'

class DBToDBPipeline(ETLPipeline[DBSource, DBTarget, pd.DataFrame]):
    """ETL: Database query to database table."""
    
    def __init__(self, name: str) -> None:
        super().__init__(name)
    
    def extract(self, source: DBSource) -> pd.DataFrame:
        """Execute query on source database."""
        engine = create_engine(source.connection_string)
        return pd.read_sql(source.query, engine)
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Override for transformations."""
        return data
    
    def load(self, data: pd.DataFrame, target: DBTarget) -> int:
        """Insert into target database."""
        engine = create_engine(target.connection_string)
        data.to_sql(
            target.table,
            engine,
            if_exists=target.if_exists,
            index=False
        )
        return len(data)
```

---

## 4. Transform Patterns

### Strategy Pattern for Transforms

```python
from abc import ABC, abstractmethod
from typing import Protocol
import pandas as pd

class TransformStrategy(Protocol):
    """Protocol for transform strategies."""
    def apply(self, df: pd.DataFrame) -> pd.DataFrame: ...

class CleansingTransform:
    """Remove nulls and duplicates."""
    
    def __init__(self, subset: list[str] | None = None) -> None:
        self._subset = subset
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.dropna(subset=self._subset)
        result = result.drop_duplicates(subset=self._subset)
        return result

class EnrichmentTransform:
    """Add computed columns."""
    
    def __init__(self, computations: dict[str, str]) -> None:
        self._computations = computations  # col_name: expression
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        for col_name, expr in self._computations.items():
            result[col_name] = result.eval(expr)
        return result

class CompositeTransform:
    """Compose multiple transforms."""
    
    def __init__(self, *transforms: TransformStrategy) -> None:
        self._transforms = list(transforms)
    
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df
        for transform in self._transforms:
            result = transform.apply(result)
        return result


# Usage:
transform = CompositeTransform(
    CleansingTransform(subset=['order_id']),
    EnrichmentTransform({'total': 'amount * quantity'})
)

cleaned_data = transform.apply(raw_data)
```

---

## 5. Error Handling & Recovery

### Typed Exceptions

```python
from dataclasses import dataclass

class ETLError(Exception):
    """Base ETL exception."""
    pass

@dataclass
class ExtractionError(ETLError):
    """Failed to extract data."""
    source: str
    reason: str
    
    def __str__(self) -> str:
        return f"Extraction failed from {self.source}: {self.reason}"

@dataclass
class TransformationError(ETLError):
    """Failed to transform data."""
    step: str
    row_index: int | None
    reason: str
    
    def __str__(self) -> str:
        location = f" at row {self.row_index}" if self.row_index else ""
        return f"Transform '{self.step}' failed{location}: {self.reason}"

@dataclass
class LoadError(ETLError):
    """Failed to load data."""
    target: str
    rows_attempted: int
    reason: str
    
    def __str__(self) -> str:
        return f"Load to {self.target} failed ({self.rows_attempted} rows): {self.reason}"
```

### Retry Logic

```python
from typing import Callable, TypeVar
from functools import wraps
import time

T = TypeVar('T')

def retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_multiplier: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,)
) -> Callable:
    """Decorator for retry logic."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            delay = delay_seconds
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_multiplier
            
            raise last_exception
        
        return wrapper
    return decorator


# Usage:
class ReliableLoader:
    @retry(max_attempts=3, delay_seconds=2.0)
    def load(self, data: pd.DataFrame, table: str) -> int:
        # May fail due to transient DB issues
        data.to_sql(table, self._engine, if_exists='append')
        return len(data)
```

---

## 6. Orchestration with Prefect

```python
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta
import pandas as pd

@task(
    retries=3,
    retry_delay_seconds=60,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1)
)
def extract_sales(path: str) -> pd.DataFrame:
    """Extract sales data with caching."""
    return pd.read_csv(path)

@task
def transform_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich sales data."""
    return (
        df
        .dropna(subset=['order_id'])
        .assign(total=lambda x: x['amount'] * x['quantity'])
    )

@task(retries=3)
def load_sales(df: pd.DataFrame, table: str) -> int:
    """Load to database with retries."""
    from sqlalchemy import create_engine
    engine = create_engine("postgresql://...")
    df.to_sql(table, engine, if_exists='append')
    return len(df)

@flow(name="Sales ETL Pipeline")
def sales_etl_flow(source_path: str, target_table: str) -> int:
    """Orchestrated sales ETL pipeline."""
    raw = extract_sales(source_path)
    transformed = transform_sales(raw)
    rows_loaded = load_sales(transformed, target_table)
    return rows_loaded


# Run:
if __name__ == "__main__":
    result = sales_etl_flow(
        source_path="/data/sales.csv",
        target_table="sales_staging"
    )
    print(f"Loaded {result} rows")
```

---

## 7. Incremental Loading

```python
from datetime import datetime
import pandas as pd

class IncrementalLoader:
    """Load only new/modified records."""
    
    def __init__(
        self,
        connection_string: str,
        table: str,
        key_column: str,
        timestamp_column: str
    ) -> None:
        self._engine = create_engine(connection_string)
        self._table = table
        self._key_column = key_column
        self._timestamp_column = timestamp_column
    
    def get_last_loaded(self) -> datetime | None:
        """Get max timestamp from target table."""
        query = f"SELECT MAX({self._timestamp_column}) FROM {self._table}"
        result = pd.read_sql(query, self._engine)
        return result.iloc[0, 0]
    
    def load_incremental(self, df: pd.DataFrame) -> int:
        """Load only records newer than last loaded."""
        last_loaded = self.get_last_loaded()
        
        if last_loaded:
            df = df[df[self._timestamp_column] > last_loaded]
        
        if len(df) == 0:
            logger.info("No new records to load")
            return 0
        
        df.to_sql(self._table, self._engine, if_exists='append', index=False)
        logger.info(f"Loaded {len(df)} new records")
        return len(df)
```

---

## 8. Data Quality Gates

```python
from dataclasses import dataclass
from typing import Callable
import pandas as pd

@dataclass
class QualityCheck:
    """Data quality check definition."""
    name: str
    check: Callable[[pd.DataFrame], bool]
    severity: str  # 'warning' or 'error'
    message: str

class QualityGate:
    """Gate to validate data quality before loading."""
    
    def __init__(self) -> None:
        self._checks: list[QualityCheck] = []
    
    def add_check(self, check: QualityCheck) -> 'QualityGate':
        self._checks.append(check)
        return self
    
    def validate(self, df: pd.DataFrame) -> tuple[bool, list[str]]:
        """Run all checks, return (passed, messages)."""
        messages = []
        has_errors = False
        
        for check in self._checks:
            passed = check.check(df)
            if not passed:
                msg = f"[{check.severity.upper()}] {check.name}: {check.message}"
                messages.append(msg)
                if check.severity == 'error':
                    has_errors = True
        
        return not has_errors, messages


# Usage:
gate = (
    QualityGate()
    .add_check(QualityCheck(
        name="no_null_keys",
        check=lambda df: df['order_id'].notna().all(),
        severity="error",
        message="Primary key contains nulls"
    ))
    .add_check(QualityCheck(
        name="positive_amounts",
        check=lambda df: (df['amount'] > 0).all(),
        severity="warning",
        message="Some amounts are not positive"
    ))
)

passed, messages = gate.validate(data)
if not passed:
    raise ValueError(f"Quality gate failed: {messages}")
```

---

> **Remember**: Production ETL needs observability (logging), recoverability (retries), and auditability (metrics). Build these in from the start.
