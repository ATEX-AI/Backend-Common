from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, ConfigDict

from common.pagination.schemas import PagePaginatedResponse


# ==== Relation [start] ==== #
class Relation(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    OVERLAY = "overlay"


# ==== Relation [end] ==== #


# ==== Background Color [start] ==== #
class BgColor(str, Enum):
    TRANSPARENT = "transparent"
    WHITE = "#ffffff"
    BLACK = "#000000"
    RED = "#ff0000"
    GREEN = "#00ff00"
    BLUE = "#0000ff"
    GRAY_LIGHT = "#f5f5f5"
    GRAY_DARK = "#7a7a7a"


# ==== Background Color [end] ==== #


# ==== Font Family [start] ==== #
class FontFamily(str, Enum):
    ARIAL = "Arial, sans-serif"
    ROBOTO = "Roboto, sans-serif"
    TIMES = "'Times New Roman', serif"
    COURIER = "'Courier New', monospace"
    VERDANA = "Verdana, sans-serif"


# ==== Font Family [end] ==== #


# ==== Font Weight [start] ==== #
class FontWeight(str, Enum):
    NORMAL = "normal"
    BOLD = "bold"
    BOLDER = "bolder"
    LIGHTER = "lighter"


# ==== Font Weight [end] ==== #


# ==== Text Align [start] ==== #
class TextAlign(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


# ==== Text Align [end] ==== #


# ==== Vertical Align [start] ==== #
class VerticalAlign(str, Enum):
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


# ==== Vertical Align [end] ==== #


# ==== Image [start] ==== #
class CellImage(BaseModel):
    src: str
    relation: Relation = Relation.LEFT
    width: Optional[int] = None
    height: Optional[int] = None
    alt: Optional[str] = None
    style: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


# ==== Image [end] ==== #


# ==== Cell [start] ==== #
class TableCell(BaseModel):
    text: Optional[str] = None
    images: List[CellImage] = Field(default_factory=list)
    bg_color: Optional[BgColor] = None
    font_family: Optional[FontFamily] = None
    font_weight: Optional[FontWeight] = None
    font_size: Optional[str] = None  # e.g. "[n]px"
    text_align: Optional[TextAlign] = None
    vertical_align: Optional[VerticalAlign] = None
    col_span: int = 1
    row_span: int = 1
    padding: Optional[str] = None  # e.g. "[n]px [k]px"
    style: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


# ==== Cell [end] ==== #


# ==== Row [start] ==== #
class TableRow(BaseModel):
    cells: List[TableCell] = Field(default_factory=list)
    style: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


# ==== Row [end] ==== #


# ==== Section [start] ==== #
class TableSection(BaseModel):
    rows: List[TableRow] = Field(default_factory=list)
    style: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


# ==== Section [end] ==== #


# ==== Table [start] ==== #
class Table(BaseModel):
    thead: Optional[TableSection] = None
    tbody: TableSection
    tfoot: Optional[TableSection] = None
    caption: Optional[str] = None
    style: Dict[str, Any] = Field(default_factory=dict)
    responsive: bool = False

    model_config = ConfigDict(from_attributes=True)


# ==== Table [end] ==== #


# ==== Paginated Table [start] ==== #
class PaginatedTable(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int
    thead: Optional[TableSection] = None
    tbody: TableSection
    tfoot: Optional[TableSection] = None
    caption: Optional[str] = None
    style: Dict[str, Any] = Field(default_factory=dict)
    responsive: bool = False

    model_config = ConfigDict(from_attributes=True)


# ==== Paginated Table [end] ==== #
