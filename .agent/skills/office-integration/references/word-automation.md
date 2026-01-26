# Word Automation Patterns

> Deep patterns for Word document automation with python-docx.

---

## 1. Document Structure

### Document Builder

```python
from pathlib import Path
from typing import List, Any, Optional
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE


class WordDocument:
    """Fluent Word document builder."""
    
    def __init__(self, template: Optional[Path] = None) -> None:
        if template:
            self._doc = Document(template)
        else:
            self._doc = Document()
    
    @property
    def doc(self) -> Document:
        return self._doc
    
    def add_heading(
        self,
        text: str,
        level: int = 1
    ) -> "WordDocument":
        """Add heading (level 0-9, 0 = Title)."""
        self._doc.add_heading(text, level=level)
        return self
    
    def add_paragraph(
        self,
        text: str,
        style: Optional[str] = None,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False
    ) -> "WordDocument":
        """Add paragraph with optional formatting."""
        p = self._doc.add_paragraph(style=style)
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.underline = underline
        return self
    
    def add_bullet_list(
        self,
        items: List[str],
        style: str = "List Bullet"
    ) -> "WordDocument":
        """Add bullet list."""
        for item in items:
            self._doc.add_paragraph(item, style=style)
        return self
    
    def add_numbered_list(
        self,
        items: List[str],
        style: str = "List Number"
    ) -> "WordDocument":
        """Add numbered list."""
        for item in items:
            self._doc.add_paragraph(item, style=style)
        return self
    
    def add_table(
        self,
        data: List[List[Any]],
        header: bool = True,
        style: str = "Table Grid"
    ) -> "WordDocument":
        """Add table from 2D data."""
        if not data:
            return self
        
        rows = len(data)
        cols = len(data[0])
        
        table = self._doc.add_table(rows=rows, cols=cols)
        table.style = style
        
        for i, row_data in enumerate(data):
            row = table.rows[i]
            for j, value in enumerate(row_data):
                cell = row.cells[j]
                cell.text = str(value)
                
                # Bold header row
                if header and i == 0:
                    for run in cell.paragraphs[0].runs:
                        run.bold = True
        
        return self
    
    def add_image(
        self,
        path: Path,
        width: Optional[float] = None,
        caption: Optional[str] = None
    ) -> "WordDocument":
        """Add image with optional width (inches) and caption."""
        if width:
            self._doc.add_picture(str(path), width=Inches(width))
        else:
            self._doc.add_picture(str(path))
        
        if caption:
            self._doc.add_paragraph(caption, style="Caption")
        
        return self
    
    def add_page_break(self) -> "WordDocument":
        """Add page break."""
        self._doc.add_page_break()
        return self
    
    def add_section_break(self) -> "WordDocument":
        """Add section break."""
        self._doc.add_section()
        return self
    
    def save(self, path: Path) -> Path:
        """Save document."""
        self._doc.save(path)
        return path


# Usage:
(
    WordDocument()
    .add_heading("Monthly Report", level=0)
    .add_paragraph("Generated: 2025-01-26")
    .add_heading("Summary", level=1)
    .add_paragraph("This report covers Q4 performance metrics.")
    .add_bullet_list([
        "Revenue increased 15%",
        "Customer satisfaction at 92%",
        "New customers: 1,250"
    ])
    .add_page_break()
    .add_heading("Detailed Data", level=1)
    .add_table([
        ["Region", "Sales", "Target", "Variance"],
        ["North", "$125K", "$100K", "+25%"],
        ["South", "$98K", "$100K", "-2%"],
    ])
    .save(Path("report.docx"))
)
```

---

## 2. Styles and Formatting

### Style Manager

```python
from docx.shared import Pt, RGBColor
from docx.enum.style import WD_STYLE_TYPE


class StyleManager:
    """Manage Word document styles."""
    
    def __init__(self, doc: Document) -> None:
        self._doc = doc
    
    def create_paragraph_style(
        self,
        name: str,
        font_name: str = "Calibri",
        font_size: int = 11,
        bold: bool = False,
        italic: bool = False,
        color: Optional[tuple] = None,
        space_before: int = 0,
        space_after: int = 0
    ) -> None:
        """Create or update paragraph style."""
        styles = self._doc.styles
        
        try:
            style = styles[name]
        except KeyError:
            style = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        
        font = style.font
        font.name = font_name
        font.size = Pt(font_size)
        font.bold = bold
        font.italic = italic
        
        if color:
            font.color.rgb = RGBColor(*color)
        
        pf = style.paragraph_format
        pf.space_before = Pt(space_before)
        pf.space_after = Pt(space_after)
    
    def create_heading_style(
        self,
        level: int,
        font_name: str = "Calibri Light",
        font_size: int = 14,
        color: tuple = (0, 0, 0)
    ) -> None:
        """Customize heading style."""
        style = self._doc.styles[f"Heading {level}"]
        font = style.font
        font.name = font_name
        font.size = Pt(font_size)
        font.color.rgb = RGBColor(*color)


# Usage:
manager = StyleManager(doc)
manager.create_paragraph_style(
    "CustomNote",
    font_name="Arial",
    font_size=10,
    italic=True,
    color=(100, 100, 100)
)
```

---

## 3. Template Processing

### Template Processor with docxtpl

```python
from pathlib import Path
from typing import Dict, Any, List
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm


class TemplateProcessor:
    """Process Word templates with Jinja2."""
    
    def __init__(self, template_path: Path) -> None:
        self._template_path = template_path
    
    def render(
        self,
        context: Dict[str, Any],
        output_path: Path
    ) -> Path:
        """Render template with context."""
        doc = DocxTemplate(self._template_path)
        doc.render(context)
        doc.save(output_path)
        return output_path
    
    def render_with_images(
        self,
        context: Dict[str, Any],
        images: Dict[str, Path],
        output_path: Path,
        image_width_mm: int = 100
    ) -> Path:
        """Render template with inline images."""
        doc = DocxTemplate(self._template_path)
        
        # Add images to context
        for key, path in images.items():
            context[key] = InlineImage(
                doc,
                str(path),
                width=Mm(image_width_mm)
            )
        
        doc.render(context)
        doc.save(output_path)
        return output_path
    
    def batch_render(
        self,
        contexts: List[Dict[str, Any]],
        output_dir: Path,
        filename_key: str = "id"
    ) -> List[Path]:
        """Batch render for multiple contexts."""
        output_dir.mkdir(parents=True, exist_ok=True)
        outputs = []
        
        for ctx in contexts:
            filename = f"{ctx.get(filename_key, len(outputs))}.docx"
            output_path = output_dir / filename
            self.render(ctx, output_path)
            outputs.append(output_path)
        
        return outputs


# Template example (template.docx):
# """
# Dear {{ customer_name }},
#
# Thank you for your order #{{ order_id }}.
#
# Order Details:
# {% for item in items %}
# - {{ item.name }}: ${{ item.price }}
# {% endfor %}
#
# Total: ${{ total }}
# """

# Usage:
processor = TemplateProcessor(Path("template.docx"))

context = {
    "customer_name": "John Doe",
    "order_id": "ORD-2025-001",
    "items": [
        {"name": "Product A", "price": "29.99"},
        {"name": "Product B", "price": "49.99"},
    ],
    "total": "79.98"
}

processor.render(context, Path("order_confirmation.docx"))
```

---

## 4. Table Operations

### Table Builder

```python
from docx.table import Table
from docx.shared import Inches, Pt
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml


class TableBuilder:
    """Advanced Word table builder."""
    
    def __init__(self, table: Table) -> None:
        self._table = table
    
    def set_column_widths(self, widths: List[float]) -> "TableBuilder":
        """Set column widths in inches."""
        for i, width in enumerate(widths):
            for row in self._table.rows:
                row.cells[i].width = Inches(width)
        return self
    
    def set_header_background(self, color: str = "4472C4") -> "TableBuilder":
        """Set header row background color."""
        for cell in self._table.rows[0].cells:
            shading = parse_xml(
                f'<w:shd {nsdecls("w")} w:fill="{color}"/>'
            )
            cell._tc.get_or_add_tcPr().append(shading)
        return self
    
    def set_cell_alignment(
        self,
        row: int,
        col: int,
        alignment: str = "center"
    ) -> "TableBuilder":
        """Set cell text alignment."""
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        align_map = {
            "left": WD_ALIGN_PARAGRAPH.LEFT,
            "center": WD_ALIGN_PARAGRAPH.CENTER,
            "right": WD_ALIGN_PARAGRAPH.RIGHT,
        }
        
        cell = self._table.rows[row].cells[col]
        for p in cell.paragraphs:
            p.alignment = align_map.get(alignment, WD_ALIGN_PARAGRAPH.LEFT)
        
        return self
    
    def merge_cells(
        self,
        start_row: int,
        start_col: int,
        end_row: int,
        end_col: int
    ) -> "TableBuilder":
        """Merge cell range."""
        start_cell = self._table.rows[start_row].cells[start_col]
        end_cell = self._table.rows[end_row].cells[end_col]
        start_cell.merge(end_cell)
        return self


# Usage:
table = doc.add_table(rows=5, cols=4)
(
    TableBuilder(table)
    .set_column_widths([1.5, 2.0, 1.5, 1.5])
    .set_header_background("1F4E79")
)
```

---

## 5. Document Properties

```python
from docx.opc.coreprops import CoreProperties
from datetime import datetime


class DocumentProperties:
    """Manage Word document properties."""
    
    def __init__(self, doc: Document) -> None:
        self._props: CoreProperties = doc.core_properties
    
    def set_author(self, author: str) -> "DocumentProperties":
        self._props.author = author
        return self
    
    def set_title(self, title: str) -> "DocumentProperties":
        self._props.title = title
        return self
    
    def set_subject(self, subject: str) -> "DocumentProperties":
        self._props.subject = subject
        return self
    
    def set_keywords(self, keywords: str) -> "DocumentProperties":
        self._props.keywords = keywords
        return self
    
    def set_created(self, dt: datetime) -> "DocumentProperties":
        self._props.created = dt
        return self


# Usage:
(
    DocumentProperties(doc)
    .set_author("Automation System")
    .set_title("Monthly Report")
    .set_keywords("report, monthly, Q4")
)
```

---

> **Remember**: Word automation should preserve document structure. Use styles, templates, and consistent formatting.
