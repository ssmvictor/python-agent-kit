# Excel Automation Patterns

> Deep patterns for Excel automation with openpyxl and xlwings.

---

## 1. openpyxl Patterns

### Workbook Operations

```python
from pathlib import Path
from typing import Optional
import openpyxl
from openpyxl import Workbook


class WorkbookManager:
    """Manage Excel workbook lifecycle."""
    
    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path
        self._workbook: Workbook | None = None
    
    def __enter__(self) -> Workbook:
        if self._path and self._path.exists():
            self._workbook = openpyxl.load_workbook(self._path)
        else:
            self._workbook = Workbook()
        return self._workbook
    
    def __exit__(self, *args) -> None:
        if self._workbook and self._path:
            self._workbook.save(self._path)
        self._workbook = None


# Usage:
with WorkbookManager(Path("data.xlsx")) as wb:
    ws = wb.active
    ws['A1'] = "Hello"
```

### Styling

```python
from openpyxl.styles import (
    Font, Alignment, Border, Side, PatternFill, NamedStyle
)


class ExcelStyles:
    """Predefined Excel styles."""
    
    @staticmethod
    def header() -> NamedStyle:
        style = NamedStyle(name="header")
        style.font = Font(bold=True, color="FFFFFF")
        style.fill = PatternFill("solid", fgColor="4472C4")
        style.alignment = Alignment(horizontal="center", vertical="center")
        style.border = Border(
            bottom=Side(style="thin", color="000000")
        )
        return style
    
    @staticmethod
    def currency() -> NamedStyle:
        style = NamedStyle(name="currency")
        style.number_format = '$#,##0.00'
        style.alignment = Alignment(horizontal="right")
        return style
    
    @staticmethod
    def date() -> NamedStyle:
        style = NamedStyle(name="date")
        style.number_format = 'YYYY-MM-DD'
        style.alignment = Alignment(horizontal="center")
        return style


def register_styles(workbook: Workbook) -> None:
    """Register all custom styles."""
    for style in [ExcelStyles.header(), ExcelStyles.currency(), ExcelStyles.date()]:
        if style.name not in workbook.named_styles:
            workbook.add_named_style(style)
```

### Charts

```python
from openpyxl.chart import BarChart, Reference, LineChart


class ChartBuilder:
    """Build Excel charts."""
    
    @staticmethod
    def bar_chart(
        sheet,
        data_range: str,
        categories_range: str,
        title: str = "",
        position: str = "E2"
    ) -> BarChart:
        chart = BarChart()
        chart.title = title
        chart.type = "col"
        
        data = Reference(sheet, range_string=data_range)
        categories = Reference(sheet, range_string=categories_range)
        
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(categories)
        
        sheet.add_chart(chart, position)
        return chart
    
    @staticmethod
    def line_chart(
        sheet,
        data_range: str,
        categories_range: str,
        title: str = "",
        position: str = "E2"
    ) -> LineChart:
        chart = LineChart()
        chart.title = title
        
        data = Reference(sheet, range_string=data_range)
        categories = Reference(sheet, range_string=categories_range)
        
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(categories)
        
        sheet.add_chart(chart, position)
        return chart
```

---

## 2. xlwings Patterns (COM)

### Excel App Manager

```python
import xlwings as xw
from pathlib import Path
from typing import Optional


class XLWingsManager:
    """xlwings Excel manager with COM."""
    
    def __init__(self, visible: bool = False) -> None:
        self._app: Optional[xw.App] = None
        self._visible = visible
    
    def __enter__(self) -> xw.App:
        self._app = xw.App(visible=self._visible)
        self._app.display_alerts = False
        return self._app
    
    def __exit__(self, *args) -> None:
        if self._app:
            self._app.quit()
            self._app = None


# Usage:
with XLWingsManager(visible=False) as app:
    wb = app.books.add()
    ws = wb.sheets[0]
    ws.range("A1").value = "Hello xlwings"
    wb.save(Path("output.xlsx"))
```

### Data Transfer

```python
import xlwings as xw
import pandas as pd
from typing import List, Any


class XLWingsDataTransfer:
    """Transfer data between Python and Excel."""
    
    def __init__(self, sheet: xw.Sheet) -> None:
        self._sheet = sheet
    
    def write_dataframe(
        self,
        df: pd.DataFrame,
        start_cell: str = "A1",
        index: bool = False,
        header: bool = True
    ) -> None:
        """Write DataFrame to Excel."""
        self._sheet.range(start_cell).options(
            pd.DataFrame, 
            index=index, 
            header=header
        ).value = df
    
    def read_dataframe(
        self,
        range_addr: str,
        header: bool = True
    ) -> pd.DataFrame:
        """Read DataFrame from Excel range."""
        return self._sheet.range(range_addr).options(
            pd.DataFrame,
            header=header
        ).value
    
    def write_list(
        self,
        data: List[List[Any]],
        start_cell: str = "A1"
    ) -> None:
        """Write 2D list to Excel."""
        self._sheet.range(start_cell).value = data
    
    def read_list(self, range_addr: str) -> List[List[Any]]:
        """Read 2D list from Excel range."""
        return self._sheet.range(range_addr).value
```

---

## 3. Formulas and Calculations

### Formula Builder

```python
from typing import List


class FormulaBuilder:
    """Build Excel formulas programmatically."""
    
    @staticmethod
    def sum(range_addr: str) -> str:
        return f"=SUM({range_addr})"
    
    @staticmethod
    def average(range_addr: str) -> str:
        return f"=AVERAGE({range_addr})"
    
    @staticmethod
    def vlookup(
        lookup_value: str,
        table_range: str,
        col_index: int,
        exact_match: bool = True
    ) -> str:
        match = 0 if exact_match else 1
        return f"=VLOOKUP({lookup_value},{table_range},{col_index},{match})"
    
    @staticmethod
    def if_formula(condition: str, true_value: str, false_value: str) -> str:
        return f"=IF({condition},{true_value},{false_value})"
    
    @staticmethod
    def sumif(
        range_addr: str,
        criteria: str,
        sum_range: str | None = None
    ) -> str:
        if sum_range:
            return f'=SUMIF({range_addr},"{criteria}",{sum_range})'
        return f'=SUMIF({range_addr},"{criteria}")'
    
    @staticmethod
    def countif(range_addr: str, criteria: str) -> str:
        return f'=COUNTIF({range_addr},"{criteria}")'


# Usage:
ws['B10'] = FormulaBuilder.sum("B2:B9")
ws['C10'] = FormulaBuilder.average("C2:C9")
ws['D2'] = FormulaBuilder.vlookup("A2", "Data!A:C", 3)
```

---

## 4. Data Validation

```python
from openpyxl.worksheet.datavalidation import DataValidation


class ValidationBuilder:
    """Build Excel data validations."""
    
    @staticmethod
    def dropdown(options: List[str], allow_blank: bool = True) -> DataValidation:
        """Create dropdown list validation."""
        formula = '"' + ','.join(options) + '"'
        dv = DataValidation(
            type="list",
            formula1=formula,
            allow_blank=allow_blank
        )
        dv.error = "Please select from the list"
        dv.errorTitle = "Invalid Entry"
        return dv
    
    @staticmethod
    def number_range(
        minimum: float,
        maximum: float,
        allow_blank: bool = True
    ) -> DataValidation:
        """Create number range validation."""
        dv = DataValidation(
            type="decimal",
            operator="between",
            formula1=str(minimum),
            formula2=str(maximum),
            allow_blank=allow_blank
        )
        dv.error = f"Value must be between {minimum} and {maximum}"
        dv.errorTitle = "Invalid Number"
        return dv
    
    @staticmethod
    def date_range(
        start_date: str,
        end_date: str
    ) -> DataValidation:
        """Create date range validation."""
        dv = DataValidation(
            type="date",
            operator="between",
            formula1=start_date,
            formula2=end_date
        )
        dv.error = f"Date must be between {start_date} and {end_date}"
        return dv


# Usage:
status_dropdown = ValidationBuilder.dropdown(["Active", "Inactive", "Pending"])
status_dropdown.add("C2:C100")
ws.add_data_validation(status_dropdown)
```

---

## 5. Conditional Formatting

```python
from openpyxl.formatting.rule import (
    ColorScaleRule, FormulaRule, CellIsRule
)
from openpyxl.styles import PatternFill


class ConditionalFormatting:
    """Excel conditional formatting rules."""
    
    @staticmethod
    def color_scale(
        start_color: str = "F8696B",
        mid_color: str = "FFEB84",
        end_color: str = "63BE7B"
    ) -> ColorScaleRule:
        """Red-Yellow-Green color scale."""
        return ColorScaleRule(
            start_type="min", start_color=start_color,
            mid_type="percentile", mid_value=50, mid_color=mid_color,
            end_type="max", end_color=end_color
        )
    
    @staticmethod
    def highlight_greater_than(
        value: float,
        fill_color: str = "63BE7B"
    ) -> CellIsRule:
        """Highlight cells greater than value."""
        return CellIsRule(
            operator="greaterThan",
            formula=[str(value)],
            fill=PatternFill("solid", fgColor=fill_color)
        )
    
    @staticmethod
    def highlight_less_than(
        value: float,
        fill_color: str = "F8696B"
    ) -> CellIsRule:
        """Highlight cells less than value."""
        return CellIsRule(
            operator="lessThan",
            formula=[str(value)],
            fill=PatternFill("solid", fgColor=fill_color)
        )


# Usage:
ws.conditional_formatting.add(
    "D2:D100",
    ConditionalFormatting.color_scale()
)
```

---

> **Remember**: Excel automation should be reproducible. Use typed builders, apply consistent styles, and validate output.
