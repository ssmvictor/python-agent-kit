---
name: office-integration
description: Office file automation principles. Excel, Word, PDF generation and manipulation with OOP patterns and strong typing.
tier: standard
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Office Integration Skill

> Office document automation principles for enterprise environments.
> **OOP-first, strongly-typed, production-ready.**

---

## ⚠️ How to Use This Skill

This skill teaches **decision-making principles** for office automation, not fixed code to copy.

- ASK about file format and operation before choosing library
- Consider template-based vs programmatic generation
- Always use typed data structures

---

## 1. Library Selection (2025)

### Excel Libraries

| Library | Best For | Read | Write | Formatting | COM |
|---------|----------|------|-------|------------|-----|
| **openpyxl** | General use | ✅ | ✅ | ✅ | ❌ |
| **xlsxwriter** | Write-only, performance | ❌ | ✅ | ✅ | ❌ |
| **xlwings** | COM integration | ✅ | ✅ | ✅ | ✅ |
| **pandas** | Data export | ✅ | ✅ | ⚠️ | ❌ |

### Word Libraries

| Library | Best For | Templates | Complex |
|---------|----------|-----------|---------|
| **python-docx** | Document creation | ❌ | ✅ |
| **docxtpl** | Template filling | ✅ | ⚠️ |

### PDF Libraries

| Library | Best For | Generation | Manipulation |
|---------|----------|------------|--------------|
| **reportlab** | Complex generation | ✅ | ❌ |
| **fpdf2** | Simple generation | ✅ | ❌ |
| **PyPDF2** | Manipulation | ❌ | ✅ |
| **pdfplumber** | Extraction | ❌ | ✅ |

---

## 2. Excel Patterns

### Base Excel Writer

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Dict
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter


@dataclass
class ExcelStyle:
    """Excel cell styling configuration."""
    font_name: str = "Calibri"
    font_size: int = 11
    bold: bool = False
    bg_color: str | None = None
    align_h: str = "left"
    align_v: str = "center"
    
    def to_openpyxl(self) -> Dict[str, Any]:
        result = {
            "font": Font(name=self.font_name, size=self.font_size, bold=self.bold),
            "alignment": Alignment(horizontal=self.align_h, vertical=self.align_v),
        }
        if self.bg_color:
            result["fill"] = PatternFill("solid", fgColor=self.bg_color)
        return result


class ExcelWriter:
    """Typed Excel writer with fluent API."""
    
    def __init__(self) -> None:
        self._workbook = openpyxl.Workbook()
        self._active_sheet = self._workbook.active
    
    def set_sheet_name(self, name: str) -> "ExcelWriter":
        self._active_sheet.title = name
        return self
    
    def add_sheet(self, name: str) -> "ExcelWriter":
        self._active_sheet = self._workbook.create_sheet(name)
        return self
    
    def write_cell(
        self, 
        row: int, 
        col: int, 
        value: Any,
        style: ExcelStyle | None = None
    ) -> "ExcelWriter":
        cell = self._active_sheet.cell(row=row, column=col, value=value)
        if style:
            for attr, val in style.to_openpyxl().items():
                setattr(cell, attr, val)
        return self
    
    def write_row(
        self, 
        row: int, 
        values: List[Any],
        start_col: int = 1,
        style: ExcelStyle | None = None
    ) -> "ExcelWriter":
        for i, value in enumerate(values):
            self.write_cell(row, start_col + i, value, style)
        return self
    
    def write_data(
        self,
        data: List[List[Any]],
        start_row: int = 1,
        start_col: int = 1,
        header_style: ExcelStyle | None = None
    ) -> "ExcelWriter":
        for i, row_data in enumerate(data):
            style = header_style if i == 0 and header_style else None
            self.write_row(start_row + i, row_data, start_col, style)
        return self
    
    def auto_width(self) -> "ExcelWriter":
        for column_cells in self._active_sheet.columns:
            max_length = max(
                len(str(cell.value or "")) for cell in column_cells
            )
            col_letter = get_column_letter(column_cells[0].column)
            self._active_sheet.column_dimensions[col_letter].width = max_length + 2
        return self
    
    def save(self, path: Path) -> Path:
        self._workbook.save(path)
        return path


# Usage:
header_style = ExcelStyle(bold=True, bg_color="4472C4")

data = [
    ["Name", "Email", "Amount"],
    ["John Doe", "john@example.com", 1500.00],
    ["Jane Smith", "jane@example.com", 2300.50],
]

(
    ExcelWriter()
    .set_sheet_name("Sales Report")
    .write_data(data, header_style=header_style)
    .auto_width()
    .save(Path("report.xlsx"))
)
```

### Excel Reader

```python
from pathlib import Path
from typing import List, Any, Iterator, Dict
import openpyxl


class ExcelReader:
    """Typed Excel reader."""
    
    def __init__(self, path: Path) -> None:
        self._workbook = openpyxl.load_workbook(path, data_only=True)
        self._active_sheet = self._workbook.active
    
    def select_sheet(self, name: str) -> "ExcelReader":
        self._active_sheet = self._workbook[name]
        return self
    
    @property
    def sheet_names(self) -> List[str]:
        return self._workbook.sheetnames
    
    def read_cell(self, row: int, col: int) -> Any:
        return self._active_sheet.cell(row=row, column=col).value
    
    def read_row(self, row: int, start_col: int = 1, end_col: int | None = None) -> List[Any]:
        end = end_col or self._active_sheet.max_column
        return [self.read_cell(row, c) for c in range(start_col, end + 1)]
    
    def read_all(self, has_header: bool = True) -> List[Dict[str, Any]] | List[List[Any]]:
        rows = list(self._active_sheet.iter_rows(values_only=True))
        
        if has_header and rows:
            headers = [str(h) for h in rows[0]]
            return [dict(zip(headers, row)) for row in rows[1:]]
        
        return [list(row) for row in rows]
    
    def iter_rows(
        self, 
        start_row: int = 1,
        has_header: bool = True
    ) -> Iterator[Dict[str, Any] | List[Any]]:
        if has_header:
            headers = self.read_row(start_row)
            for row in range(start_row + 1, self._active_sheet.max_row + 1):
                yield dict(zip(headers, self.read_row(row)))
        else:
            for row in range(start_row, self._active_sheet.max_row + 1):
                yield self.read_row(row)
```

---

## 3. Word Patterns

### Document Builder

```python
from pathlib import Path
from typing import List, Any
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH


class WordDocumentBuilder:
    """Fluent Word document builder."""
    
    def __init__(self) -> None:
        self._doc = Document()
    
    def add_heading(
        self, 
        text: str, 
        level: int = 1
    ) -> "WordDocumentBuilder":
        self._doc.add_heading(text, level=level)
        return self
    
    def add_paragraph(
        self, 
        text: str,
        bold: bool = False,
        italic: bool = False,
        alignment: str = "left"
    ) -> "WordDocumentBuilder":
        p = self._doc.add_paragraph()
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        
        align_map = {
            "left": WD_ALIGN_PARAGRAPH.LEFT,
            "center": WD_ALIGN_PARAGRAPH.CENTER,
            "right": WD_ALIGN_PARAGRAPH.RIGHT,
        }
        p.alignment = align_map.get(alignment, WD_ALIGN_PARAGRAPH.LEFT)
        
        return self
    
    def add_table(
        self,
        data: List[List[Any]],
        has_header: bool = True
    ) -> "WordDocumentBuilder":
        if not data:
            return self
        
        rows = len(data)
        cols = len(data[0])
        
        table = self._doc.add_table(rows=rows, cols=cols)
        table.style = 'Table Grid'
        
        for i, row_data in enumerate(data):
            row = table.rows[i]
            for j, value in enumerate(row_data):
                cell = row.cells[j]
                cell.text = str(value)
                
                if has_header and i == 0:
                    cell.paragraphs[0].runs[0].bold = True
        
        return self
    
    def add_image(
        self,
        path: Path,
        width_inches: float | None = None
    ) -> "WordDocumentBuilder":
        if width_inches:
            self._doc.add_picture(str(path), width=Inches(width_inches))
        else:
            self._doc.add_picture(str(path))
        return self
    
    def add_page_break(self) -> "WordDocumentBuilder":
        self._doc.add_page_break()
        return self
    
    def save(self, path: Path) -> Path:
        self._doc.save(path)
        return path


# Usage:
(
    WordDocumentBuilder()
    .add_heading("Monthly Report", level=1)
    .add_paragraph("Generated automatically on 2025-01-26")
    .add_heading("Sales Summary", level=2)
    .add_table([
        ["Region", "Sales", "Target"],
        ["North", "$125,000", "$100,000"],
        ["South", "$98,500", "$100,000"],
    ])
    .add_page_break()
    .add_heading("Charts", level=2)
    .save(Path("report.docx"))
)
```

### Template Processor

```python
from pathlib import Path
from typing import Dict, Any, List
from docxtpl import DocxTemplate


class WordTemplateProcessor:
    """Process Word templates with Jinja2."""
    
    def __init__(self, template_path: Path) -> None:
        self._template_path = template_path
    
    def render(
        self,
        output_path: Path,
        context: Dict[str, Any]
    ) -> Path:
        """Render template with context."""
        doc = DocxTemplate(self._template_path)
        doc.render(context)
        doc.save(output_path)
        return output_path
    
    def render_batch(
        self,
        output_dir: Path,
        contexts: List[Dict[str, Any]],
        filename_key: str = "id"
    ) -> List[Path]:
        """Render template for multiple contexts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        outputs = []
        
        for ctx in contexts:
            filename = f"{ctx.get(filename_key, len(outputs))}.docx"
            output_path = output_dir / filename
            self.render(output_path, ctx)
            outputs.append(output_path)
        
        return outputs
```

---

## 4. PDF Patterns

### PDF Generator

```python
from pathlib import Path
from typing import List, Any, Tuple
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors


class PDFGenerator:
    """Fluent PDF generator with reportlab."""
    
    def __init__(
        self,
        output_path: Path,
        page_size: Tuple[float, float] = A4,
        margins: Tuple[float, float, float, float] = (72, 72, 72, 72)
    ) -> None:
        self._output_path = output_path
        self._doc = SimpleDocTemplate(
            str(output_path),
            pagesize=page_size,
            leftMargin=margins[0],
            rightMargin=margins[1],
            topMargin=margins[2],
            bottomMargin=margins[3]
        )
        self._elements: List = []
        self._styles = getSampleStyleSheet()
    
    def add_title(self, text: str) -> "PDFGenerator":
        self._elements.append(Paragraph(text, self._styles['Title']))
        self._elements.append(Spacer(1, 12))
        return self
    
    def add_heading(self, text: str, level: int = 1) -> "PDFGenerator":
        style = self._styles.get(f'Heading{level}', self._styles['Heading1'])
        self._elements.append(Paragraph(text, style))
        self._elements.append(Spacer(1, 6))
        return self
    
    def add_paragraph(self, text: str) -> "PDFGenerator":
        self._elements.append(Paragraph(text, self._styles['Normal']))
        self._elements.append(Spacer(1, 6))
        return self
    
    def add_spacer(self, height: float = 12) -> "PDFGenerator":
        self._elements.append(Spacer(1, height))
        return self
    
    def add_table(
        self,
        data: List[List[Any]],
        col_widths: List[float] | None = None,
        header_bg: str = "#4472C4"
    ) -> "PDFGenerator":
        table = Table(data, colWidths=col_widths)
        
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_bg)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)
        
        self._elements.append(table)
        self._elements.append(Spacer(1, 12))
        return self
    
    def add_image(
        self,
        path: Path,
        width: float | None = None,
        height: float | None = None
    ) -> "PDFGenerator":
        img = Image(str(path), width=width, height=height)
        self._elements.append(img)
        self._elements.append(Spacer(1, 12))
        return self
    
    def build(self) -> Path:
        self._doc.build(self._elements)
        return self._output_path


# Usage:
(
    PDFGenerator(Path("report.pdf"))
    .add_title("Quarterly Report")
    .add_heading("Executive Summary", level=1)
    .add_paragraph("This report summarizes Q4 2025 performance...")
    .add_spacer(20)
    .add_heading("Sales Data", level=2)
    .add_table([
        ["Region", "Q3", "Q4", "Growth"],
        ["North", "$100K", "$125K", "+25%"],
        ["South", "$90K", "$98K", "+9%"],
    ])
    .build()
)
```

---

## 📚 References

See detailed patterns in:
- [excel-automation.md](./references/excel-automation.md)
- [word-automation.md](./references/word-automation.md)
- [pdf-generation.md](./references/pdf-generation.md)

---

## ✅ Decision Checklist

Before implementing document automation:

- [ ] Chose library based on requirements?
- [ ] Using typed dataclasses for configuration?
- [ ] Template-based or programmatic generation?
- [ ] Proper file path handling?
- [ ] Error handling for IO operations?
- [ ] Output validation?

---

> **Remember**: Document generation should be repeatable and consistent. Use templates and typed builders.
