# PDF Generation Patterns

> Deep patterns for PDF generation with reportlab and manipulation with PyPDF2.

---

## 1. ReportLab Basics

### Document Builder

```python
from pathlib import Path
from typing import List, Any, Tuple
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch, cm, mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether
)


class PDFDocument:
    """Fluent PDF document builder."""
    
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
        self._setup_custom_styles()
    
    def _setup_custom_styles(self) -> None:
        """Setup custom paragraph styles."""
        self._styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self._styles['Title'],
            fontSize=24,
            spaceAfter=30
        ))
        
        self._styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self._styles['Heading1'],
            fontSize=16,
            spaceBefore=12,
            spaceAfter=6
        ))
    
    def add_title(self, text: str) -> "PDFDocument":
        self._elements.append(
            Paragraph(text, self._styles['CustomTitle'])
        )
        return self
    
    def add_heading(self, text: str, level: int = 1) -> "PDFDocument":
        style_name = f'Heading{min(level, 6)}'
        self._elements.append(
            Paragraph(text, self._styles.get(style_name, self._styles['Heading1']))
        )
        self._elements.append(Spacer(1, 6))
        return self
    
    def add_paragraph(self, text: str, style: str = 'Normal') -> "PDFDocument":
        self._elements.append(
            Paragraph(text, self._styles.get(style, self._styles['Normal']))
        )
        self._elements.append(Spacer(1, 6))
        return self
    
    def add_bullet_list(self, items: List[str]) -> "PDFDocument":
        for item in items:
            bullet_text = f"• {item}"
            self._elements.append(
                Paragraph(bullet_text, self._styles['Normal'])
            )
        self._elements.append(Spacer(1, 12))
        return self
    
    def add_spacer(self, height: float = 12) -> "PDFDocument":
        self._elements.append(Spacer(1, height))
        return self
    
    def add_page_break(self) -> "PDFDocument":
        self._elements.append(PageBreak())
        return self
    
    def add_table(
        self,
        data: List[List[Any]],
        col_widths: List[float] | None = None,
        header_bg: str = "#4472C4",
        header_text_color: str = "#FFFFFF"
    ) -> "PDFDocument":
        table = Table(data, colWidths=col_widths)
        
        style = TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(header_bg)),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor(header_text_color)),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), HexColor("#FFFFFF")),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternating rows
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor("#FFFFFF"), HexColor("#F2F2F2")]),
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
    ) -> "PDFDocument":
        img = Image(str(path), width=width, height=height)
        self._elements.append(img)
        self._elements.append(Spacer(1, 12))
        return self
    
    def build(self) -> Path:
        self._doc.build(self._elements)
        return self._output_path


# Usage:
(
    PDFDocument(Path("report.pdf"))
    .add_title("Quarterly Report Q4 2025")
    .add_heading("Executive Summary")
    .add_paragraph("This report summarizes the key metrics for Q4 2025.")
    .add_bullet_list([
        "Revenue increased by 15%",
        "Customer satisfaction at 92%",
        "Market share grew to 23%"
    ])
    .add_page_break()
    .add_heading("Sales Data")
    .add_table([
        ["Region", "Q3 Sales", "Q4 Sales", "Growth"],
        ["North", "$100,000", "$125,000", "+25%"],
        ["South", "$90,000", "$98,000", "+9%"],
        ["East", "$85,000", "$92,000", "+8%"],
    ])
    .build()
)
```

---

## 2. Advanced Tables

### Table with Spans

```python
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


class AdvancedTableBuilder:
    """Build complex tables with spans and styles."""
    
    def __init__(self, data: List[List[Any]]) -> None:
        self._data = data
        self._spans: List[Tuple] = []
        self._styles: List[Tuple] = []
    
    def merge_cells(
        self,
        start_row: int,
        start_col: int,
        end_row: int,
        end_col: int
    ) -> "AdvancedTableBuilder":
        self._spans.append(
            ('SPAN', (start_col, start_row), (end_col, end_row))
        )
        return self
    
    def set_cell_background(
        self,
        row: int,
        col: int,
        color: str
    ) -> "AdvancedTableBuilder":
        self._styles.append(
            ('BACKGROUND', (col, row), (col, row), HexColor(color))
        )
        return self
    
    def set_cell_font(
        self,
        row: int,
        col: int,
        font_name: str = "Helvetica-Bold",
        font_size: int = 11
    ) -> "AdvancedTableBuilder":
        self._styles.extend([
            ('FONTNAME', (col, row), (col, row), font_name),
            ('FONTSIZE', (col, row), (col, row), font_size),
        ])
        return self
    
    def build(
        self,
        col_widths: List[float] | None = None
    ) -> Table:
        table = Table(self._data, colWidths=col_widths)
        
        base_style = [
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]
        
        all_styles = base_style + self._spans + self._styles
        table.setStyle(TableStyle(all_styles))
        
        return table
```

---

## 3. Charts in PDF

```python
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart


class ChartBuilder:
    """Build charts for PDF documents."""
    
    @staticmethod
    def bar_chart(
        data: List[List[float]],
        categories: List[str],
        width: int = 400,
        height: int = 200
    ) -> Drawing:
        drawing = Drawing(width, height)
        
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.width = width - 100
        chart.height = height - 80
        
        chart.data = data
        chart.categoryAxis.categoryNames = categories
        chart.categoryAxis.labels.boxAnchor = 'n'
        
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(max(d) for d in data) * 1.1
        
        drawing.add(chart)
        return drawing
    
    @staticmethod
    def pie_chart(
        data: List[float],
        labels: List[str],
        width: int = 300,
        height: int = 200
    ) -> Drawing:
        drawing = Drawing(width, height)
        
        chart = Pie()
        chart.x = width // 2 - 50
        chart.y = height // 2 - 50
        chart.width = 100
        chart.height = 100
        
        chart.data = data
        chart.labels = labels
        chart.slices.strokeWidth = 0.5
        
        drawing.add(chart)
        return drawing


# Usage:
chart = ChartBuilder.bar_chart(
    data=[[10, 20, 30, 40], [15, 25, 35, 45]],
    categories=['Q1', 'Q2', 'Q3', 'Q4']
)
elements.append(chart)
```

---

## 4. PDF Manipulation with PyPDF2

### PDF Merger

```python
from pathlib import Path
from typing import List
from PyPDF2 import PdfReader, PdfWriter, PdfMerger


class PDFManipulator:
    """Manipulate existing PDF files."""
    
    @staticmethod
    def merge(
        input_files: List[Path],
        output_file: Path
    ) -> Path:
        """Merge multiple PDFs into one."""
        merger = PdfMerger()
        
        for pdf_file in input_files:
            merger.append(str(pdf_file))
        
        merger.write(str(output_file))
        merger.close()
        
        return output_file
    
    @staticmethod
    def split(
        input_file: Path,
        output_dir: Path,
        pages_per_file: int = 1
    ) -> List[Path]:
        """Split PDF into multiple files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        reader = PdfReader(str(input_file))
        outputs = []
        
        for i in range(0, len(reader.pages), pages_per_file):
            writer = PdfWriter()
            
            for j in range(pages_per_file):
                if i + j < len(reader.pages):
                    writer.add_page(reader.pages[i + j])
            
            output_path = output_dir / f"{input_file.stem}_{i // pages_per_file + 1}.pdf"
            with open(output_path, "wb") as f:
                writer.write(f)
            outputs.append(output_path)
        
        return outputs
    
    @staticmethod
    def extract_pages(
        input_file: Path,
        output_file: Path,
        page_numbers: List[int]
    ) -> Path:
        """Extract specific pages from PDF."""
        reader = PdfReader(str(input_file))
        writer = PdfWriter()
        
        for page_num in page_numbers:
            if 0 <= page_num < len(reader.pages):
                writer.add_page(reader.pages[page_num])
        
        with open(output_file, "wb") as f:
            writer.write(f)
        
        return output_file
    
    @staticmethod
    def add_watermark(
        input_file: Path,
        watermark_file: Path,
        output_file: Path
    ) -> Path:
        """Add watermark to all pages."""
        reader = PdfReader(str(input_file))
        watermark = PdfReader(str(watermark_file)).pages[0]
        writer = PdfWriter()
        
        for page in reader.pages:
            page.merge_page(watermark)
            writer.add_page(page)
        
        with open(output_file, "wb") as f:
            writer.write(f)
        
        return output_file


# Usage:
# Merge PDFs
PDFManipulator.merge(
    [Path("file1.pdf"), Path("file2.pdf")],
    Path("merged.pdf")
)

# Split PDF
PDFManipulator.split(
    Path("large_document.pdf"),
    Path("output/"),
    pages_per_file=10
)
```

---

## 5. PDF Text Extraction

```python
from pathlib import Path
from typing import List, Optional
from PyPDF2 import PdfReader


class PDFExtractor:
    """Extract content from PDF files."""
    
    def __init__(self, path: Path) -> None:
        self._reader = PdfReader(str(path))
    
    @property
    def page_count(self) -> int:
        return len(self._reader.pages)
    
    def extract_text(
        self,
        page_numbers: Optional[List[int]] = None
    ) -> str:
        """Extract text from PDF."""
        pages = page_numbers or range(len(self._reader.pages))
        
        text_parts = []
        for i in pages:
            if 0 <= i < len(self._reader.pages):
                text_parts.append(self._reader.pages[i].extract_text())
        
        return "\n\n".join(text_parts)
    
    def extract_page(self, page_number: int) -> str:
        """Extract text from single page."""
        if 0 <= page_number < len(self._reader.pages):
            return self._reader.pages[page_number].extract_text()
        return ""
    
    def get_metadata(self) -> dict:
        """Get PDF metadata."""
        meta = self._reader.metadata
        if meta:
            return {
                "title": meta.title,
                "author": meta.author,
                "subject": meta.subject,
                "creator": meta.creator,
                "producer": meta.producer,
            }
        return {}


# Usage:
extractor = PDFExtractor(Path("document.pdf"))
print(f"Pages: {extractor.page_count}")
print(extractor.extract_text())
```

---

> **Remember**: PDF generation should produce consistent, professional output. Use structured builders and validate the result.
