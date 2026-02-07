#!/usr/bin/env python3
"""
Schema Validator Script

Validates DataFrame schema against Pydantic models or JSON schema.
Usage: python schema_validator.py <data_file> --schema <schema_file>

Examples:
    python schema_validator.py data.csv --schema schema.json
    python schema_validator.py data.parquet --schema schema.json --format parquet
"""

from __future__ import annotations

import sys
from pathlib import Path

# Adiciona path para encontrar _console.py
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from _console import console, success, error, warning, step, make_table, header

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DataType(str, Enum):
    """Supported data types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    ANY = "any"


@dataclass
class ColumnSchema:
    """Schema definition for a single column."""
    name: str
    dtype: DataType
    nullable: bool = True
    min_value: float | None = None
    max_value: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    allowed_values: list[Any] | None = None
    pattern: str | None = None


@dataclass
class TableSchema:
    """Schema definition for a table/DataFrame."""
    name: str
    columns: list[ColumnSchema]
    strict: bool = False  # If True, extra columns are not allowed
    
    @classmethod
    def from_json(cls, data: dict) -> "TableSchema":
        """Create TableSchema from JSON dict."""
        columns = [
            ColumnSchema(
                name=col["name"],
                dtype=DataType(col.get("dtype", "any")),
                nullable=col.get("nullable", True),
                min_value=col.get("min_value"),
                max_value=col.get("max_value"),
                min_length=col.get("min_length"),
                max_length=col.get("max_length"),
                allowed_values=col.get("allowed_values"),
                pattern=col.get("pattern"),
            )
            for col in data.get("columns", [])
        ]
        return cls(
            name=data.get("name", "unnamed"),
            columns=columns,
            strict=data.get("strict", False),
        )
    
    @classmethod
    def from_json_file(cls, path: Path) -> "TableSchema":
        """Load TableSchema from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_json(data)


@dataclass
class ValidationError:
    """Single validation error."""
    column: str
    error_type: str
    message: str
    row_index: int | None = None
    value: Any = None


@dataclass
class ValidationResult:
    """Result of schema validation."""
    schema_name: str
    file_path: str
    validated_at: datetime
    is_valid: bool
    total_rows: int
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON."""
        return {
            "schema_name": self.schema_name,
            "file_path": self.file_path,
            "validated_at": self.validated_at.isoformat(),
            "is_valid": self.is_valid,
            "total_rows": self.total_rows,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": [
                {
                    "column": e.column,
                    "error_type": e.error_type,
                    "message": e.message,
                    "row_index": e.row_index,
                }
                for e in self.errors[:50]  # Limit to first 50
            ],
            "warnings": self.warnings,
        }


class SchemaValidator:
    """Validates DataFrames against schema definitions."""
    
    def __init__(self, schema: TableSchema) -> None:
        self._schema = schema
        self._column_map = {col.name: col for col in schema.columns}
    
    def validate(self, df: Any, file_path: str = "") -> ValidationResult:
        """Validate DataFrame against schema."""
        result = ValidationResult(
            schema_name=self._schema.name,
            file_path=file_path,
            validated_at=datetime.now(),
            is_valid=True,
            total_rows=len(df),
        )
        
        # Check required columns
        self._check_required_columns(df, result)
        
        # Check extra columns (if strict mode)
        if self._schema.strict:
            self._check_extra_columns(df, result)
        
        # Check data types
        self._check_data_types(df, result)
        
        # Check nullable constraints
        self._check_nullable(df, result)
        
        # Check value constraints
        self._check_value_constraints(df, result)
        
        # Set final validity
        result.is_valid = len(result.errors) == 0
        
        return result
    
    def _check_required_columns(self, df: Any, result: ValidationResult) -> None:
        """Check that all required columns exist."""
        df_columns = set(df.columns)
        for col_schema in self._schema.columns:
            if col_schema.name not in df_columns:
                result.errors.append(ValidationError(
                    column=col_schema.name,
                    error_type="missing_column",
                    message=f"Required column '{col_schema.name}' is missing",
                ))
    
    def _check_extra_columns(self, df: Any, result: ValidationResult) -> None:
        """Check for extra columns in strict mode."""
        expected = {col.name for col in self._schema.columns}
        actual = set(df.columns)
        extra = actual - expected
        if extra:
            result.warnings.append(f"Extra columns found (strict mode): {extra}")
    
    def _check_data_types(self, df: Any, result: ValidationResult) -> None:
        """Check column data types."""
        import pandas as pd
        
        dtype_mapping = {
            DataType.STRING: ["object", "string"],
            DataType.INTEGER: ["int64", "int32", "Int64", "Int32"],
            DataType.FLOAT: ["float64", "float32", "Float64"],
            DataType.BOOLEAN: ["bool", "boolean"],
            DataType.DATETIME: ["datetime64[ns]", "datetime64"],
        }
        
        for col_schema in self._schema.columns:
            if col_schema.name not in df.columns:
                continue
            
            if col_schema.dtype == DataType.ANY:
                continue
            
            actual_dtype = str(df[col_schema.name].dtype)
            expected_dtypes = dtype_mapping.get(col_schema.dtype, [])
            
            if not any(expected in actual_dtype for expected in expected_dtypes):
                result.warnings.append(
                    f"Column '{col_schema.name}' has dtype '{actual_dtype}', "
                    f"expected one of {expected_dtypes}"
                )
    
    def _check_nullable(self, df: Any, result: ValidationResult) -> None:
        """Check nullable constraints."""
        for col_schema in self._schema.columns:
            if col_schema.name not in df.columns:
                continue
            
            if not col_schema.nullable:
                null_count = df[col_schema.name].isnull().sum()
                if null_count > 0:
                    result.errors.append(ValidationError(
                        column=col_schema.name,
                        error_type="null_not_allowed",
                        message=f"Column '{col_schema.name}' has {null_count} null values but is not nullable",
                    ))
    
    def _check_value_constraints(self, df: Any, result: ValidationResult) -> None:
        """Check min/max and allowed value constraints."""
        for col_schema in self._schema.columns:
            if col_schema.name not in df.columns:
                continue
            
            col = df[col_schema.name]
            
            # Min value check
            if col_schema.min_value is not None:
                violations = (col < col_schema.min_value).sum()
                if violations > 0:
                    result.errors.append(ValidationError(
                        column=col_schema.name,
                        error_type="min_value_violation",
                        message=f"{violations} values below minimum ({col_schema.min_value})",
                    ))
            
            # Max value check
            if col_schema.max_value is not None:
                violations = (col > col_schema.max_value).sum()
                if violations > 0:
                    result.errors.append(ValidationError(
                        column=col_schema.name,
                        error_type="max_value_violation",
                        message=f"{violations} values above maximum ({col_schema.max_value})",
                    ))
            
            # Allowed values check
            if col_schema.allowed_values is not None:
                invalid = ~col.isin(col_schema.allowed_values) & col.notna()
                violations = invalid.sum()
                if violations > 0:
                    result.errors.append(ValidationError(
                        column=col_schema.name,
                        error_type="invalid_value",
                        message=f"{violations} values not in allowed list",
                    ))


def load_dataframe(path: Path, format: str) -> Any:
    """Load DataFrame from file."""
    try:
        import pandas as pd
    except ImportError:
        error("pandas is required. Install with: pip install pandas")
        sys.exit(1)
    
    if format == "csv":
        return pd.read_csv(path)
    elif format == "parquet":
        return pd.read_parquet(path)
    elif format == "json":
        return pd.read_json(path)
    else:
        raise ValueError(f"Unsupported format: {format}")


def print_result(result: ValidationResult, json_output: bool = False) -> None:
    """Print validation result with Rich formatting."""
    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return
    
    header("SCHEMA VALIDATION REPORT")
    
    console.print(f"[b]Schema:[/b] {result.schema_name}")
    console.print(f"[b]File:[/b] {result.file_path}")
    console.print(f"[b]Rows:[/b] {result.total_rows:,}")
    console.print(f"[b]Validated:[/b] {result.validated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    console.print()
    
    if result.warnings:
        warning("Warnings:")
        for warn in result.warnings:
            console.print(f"  - {warn}")
        console.print()
    
    if result.errors:
        error("Errors:")
        table = make_table("Column", "Error Type", "Message")
        for err in result.errors[:20]:  # Show first 20
            table.add_row(err.column, err.error_type, err.message)
        console.print(table)
        if len(result.errors) > 20:
            console.print(f"... and {len(result.errors) - 20} more errors")
        console.print()
    
    if result.is_valid:
        success(f"VALID - Errors: {len(result.errors)} | Warnings: {len(result.warnings)}")
    else:
        error(f"INVALID - Errors: {len(result.errors)} | Warnings: {len(result.warnings)}")


def generate_sample_schema() -> None:
    """Generate a sample schema file."""
    sample = {
        "name": "sales_data",
        "strict": False,
        "columns": [
            {
                "name": "order_id",
                "dtype": "string",
                "nullable": False,
            },
            {
                "name": "amount",
                "dtype": "float",
                "nullable": False,
                "min_value": 0,
            },
            {
                "name": "quantity",
                "dtype": "integer",
                "nullable": False,
                "min_value": 1,
            },
            {
                "name": "status",
                "dtype": "string",
                "allowed_values": ["pending", "completed", "cancelled"],
            },
        ],
    }
    print(json.dumps(sample, indent=2))


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Schema Validator - Validate data against schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("data", type=Path, nargs="?", help="Path to data file")
    parser.add_argument(
        "--schema", "-s",
        type=Path,
        help="Path to schema JSON file"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["csv", "parquet", "json"],
        default="csv",
        help="Data file format (default: csv)"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output result as JSON"
    )
    parser.add_argument(
        "--generate-sample",
        action="store_true",
        help="Generate a sample schema file and exit"
    )
    
    args = parser.parse_args()
    
    # Generate sample schema if requested
    if args.generate_sample:
        generate_sample_schema()
        return 0
    
    # Validate arguments
    if not args.data:
        parser.error("data file path is required")
    
    if not args.schema:
        parser.error("--schema is required")
    
    if not args.data.exists():
        error(f"Data file not found: {args.data}")
        return 1
    
    if not args.schema.exists():
        error(f"Schema file not found: {args.schema}")
        return 1
    
    # Load schema
    try:
        schema = TableSchema.from_json_file(args.schema)
    except Exception as e:
        error(f"Failed to load schema: {e}")
        return 1
    
    # Load data
    try:
        df = load_dataframe(args.data, args.format)
    except Exception as e:
        error(f"Failed to load data: {e}")
        return 1
    
    # Validate
    validator = SchemaValidator(schema)
    result = validator.validate(df, str(args.data))
    
    # Output
    print_result(result, args.json)
    
    return 0 if result.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
