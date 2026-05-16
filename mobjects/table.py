from __future__ import annotations

from manimlib.constants import DOWN, FRAME_WIDTH, LEFT, MED_LARGE_BUFF, ORIGIN, RIGHT
from manimlib.constants import GREY_A
from manimlib.mobject.geometry import Line
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence, Union
    from manimlib.typing import ManimColor, Vect3, Self

    CellType = Union[str, VMobject]
    TableDataType = Sequence[Sequence[CellType]]


class Table(VGroup):
    """
    A grid of Text (or other VMobject) entries arranged in rows and columns.

    Pass strings to create Text cells automatically, or pass existing Text /
    VMobject instances for full control.

    Use ``full_width=True`` or ``max_width=...`` to span the frame; long strings
    wrap via Pango's ``line_width`` on each column.

    Example::

        table = Table(
            [["Claim", "%"], ["A long claim ...", "24%"]],
            header_row=True,
            full_width=True,
            column_width_ratios=(4, 1),
        )
    """

    def __init__(
        self,
        table_data: TableDataType,
        v_buff: float = 0.55,
        h_buff: float = 0.8,
        v_cell_buff: float = 0.22,
        h_cell_buff: float = 0.18,
        element_alignment_corner: Vect3 | None = None,
        element_config: dict = dict(),
        header_row: bool = False,
        header_config: dict | None = None,
        max_width: float | None = None,
        full_width: bool = False,
        width_margin: float = MED_LARGE_BUFF,
        column_width_ratios: Sequence[float] | None = None,
        include_outer_lines: bool = True,
        include_horizontal_lines: bool = True,
        include_vertical_lines: bool = True,
        line_config: dict | None = None,
        **kwargs,
    ):
        if not table_data:
            raise ValueError("table_data must contain at least one row")
        if full_width and max_width is not None:
            raise ValueError("Pass only one of full_width or max_width")

        super().__init__(**kwargs)

        self.table_data = self._normalize_table_data(table_data)
        self.v_buff = v_buff
        self.h_buff = h_buff
        self.v_cell_buff = v_cell_buff
        self.h_cell_buff = h_cell_buff
        self.element_config = element_config
        self.header_row = header_row
        self.header_config = header_config or dict()
        self.column_width_ratios = column_width_ratios
        self.max_width = self._resolve_max_width(max_width, full_width, width_margin)
        self.column_widths: list[float] = []

        width_constrained = self.max_width is not None
        if element_alignment_corner is None:
            self.element_alignment_corner = LEFT if width_constrained else ORIGIN
        else:
            self.element_alignment_corner = element_alignment_corner

        self.mob_matrix = self._create_mobject_matrix()
        n_cols = len(self.mob_matrix[0])

        self.elements = [cell for row in self.mob_matrix for cell in row]
        self.columns = VGroup(*(
            VGroup(*(row[j] for row in self.mob_matrix))
            for j in range(n_cols)
        ))
        self.rows = VGroup(*(VGroup(*row) for row in self.mob_matrix))

        self.grid_lines = VGroup()
        if include_outer_lines or include_horizontal_lines or include_vertical_lines:
            self.grid_lines = self._create_grid_lines(
                include_outer_lines=include_outer_lines,
                include_horizontal_lines=include_horizontal_lines,
                include_vertical_lines=include_vertical_lines,
                line_config=dict(line_config or dict()),
            )

        if len(self.grid_lines) > 0:
            self.add(self.grid_lines)
        self.add(*self.elements)
        self.center()

    def _resolve_max_width(
        self,
        max_width: float | None,
        full_width: bool,
        width_margin: float,
    ) -> float | None:
        if full_width:
            return FRAME_WIDTH - 2 * width_margin
        return max_width

    def _normalize_table_data(self, table_data: TableDataType) -> list[list[CellType]]:
        rows = [list(row) for row in table_data]
        n_cols = max(len(row) for row in rows)
        for row in rows:
            while len(row) < n_cols:
                row.append("")
        return rows

    def _cell_config(self, row_index: int) -> dict:
        config = dict(self.element_config)
        if self.header_row and row_index == 0:
            config.update(self.header_config)
        return config

    def _element_to_mobject(
        self,
        element: CellType,
        line_width: float | None = None,
        **config,
    ) -> VMobject:
        if isinstance(element, VMobject):
            return element
        if line_width is not None:
            config["line_width"] = line_width
        return Text(str(element), **config)

    def _measure_natural_column_widths(self, n_cols: int) -> list[float]:
        widths = [0.0] * n_cols
        for i, row in enumerate(self.table_data):
            for j, element in enumerate(row):
                if isinstance(element, VMobject):
                    widths[j] = max(widths[j], element.get_width())
                else:
                    cell = self._element_to_mobject(element, **self._cell_config(i))
                    widths[j] = max(widths[j], cell.get_width())
        return [max(w, 0.01) for w in widths]

    def _compute_column_widths(self, natural_widths: list[float]) -> list[float]:
        n_cols = len(natural_widths)
        available = (
            self.max_width
            - (n_cols - 1) * self.h_buff
            - 2 * self.h_cell_buff
        )
        if available <= 0:
            raise ValueError("max_width is too small for this table")

        if self.column_width_ratios is not None:
            ratios = list(self.column_width_ratios)
            if len(ratios) != n_cols:
                raise ValueError(
                    f"column_width_ratios length ({len(ratios)}) "
                    f"must match number of columns ({n_cols})"
                )
            total = sum(ratios)
            return [available * r / total for r in ratios]

        total_natural = sum(natural_widths)
        scale = available / total_natural
        return [w * scale for w in natural_widths]

    def _create_mobject_matrix(self) -> list[list[VMobject]]:
        if self.max_width is None:
            return self._create_uniform_mobject_matrix()
        return self._create_wrapped_mobject_matrix()

    def _create_uniform_mobject_matrix(self) -> list[list[VMobject]]:
        mob_matrix = []
        for i, row in enumerate(self.table_data):
            mob_matrix.append([
                self._element_to_mobject(element, **self._cell_config(i))
                for element in row
            ])

        max_width = max(cell.get_width() for row in mob_matrix for cell in row)
        max_height = max(cell.get_height() for row in mob_matrix for cell in row)
        x_step = (max_width + self.h_buff) * RIGHT
        y_step = (max_height + self.v_buff) * DOWN

        for i, row in enumerate(mob_matrix):
            for j, cell in enumerate(row):
                cell.move_to(i * y_step + j * x_step, self.element_alignment_corner)

        return mob_matrix

    def _create_wrapped_mobject_matrix(self) -> list[list[VMobject]]:
        n_cols = len(self.table_data[0])
        natural_widths = self._measure_natural_column_widths(n_cols)
        self.column_widths = self._compute_column_widths(natural_widths)

        mob_matrix = []
        for i, row in enumerate(self.table_data):
            row_cells = []
            for j, element in enumerate(row):
                line_width = max(
                    self.column_widths[j] - 2 * self.h_cell_buff,
                    0.1,
                )
                row_cells.append(self._element_to_mobject(
                    element,
                    line_width=line_width if not isinstance(element, VMobject) else None,
                    **self._cell_config(i),
                ))
            mob_matrix.append(row_cells)

        x_starts = [0.0]
        for w in self.column_widths[:-1]:
            x_starts.append(x_starts[-1] + w + self.h_buff)

        y = 0.0
        for row in mob_matrix:
            row_height = max(cell.get_height() for cell in row)
            row_center_y = y - row_height / 2
            for j, cell in enumerate(row):
                anchor = x_starts[j] + self.h_cell_buff
                if self.element_alignment_corner is LEFT:
                    cell.move_to([anchor, row_center_y, 0], LEFT)
                else:
                    cell.move_to(
                        [x_starts[j] + self.column_widths[j] / 2, row_center_y, 0],
                        self.element_alignment_corner,
                    )
            y -= row_height + self.v_buff

        return mob_matrix

    def _create_grid_lines(
        self,
        include_outer_lines: bool,
        include_horizontal_lines: bool,
        include_vertical_lines: bool,
        line_config: dict,
    ) -> VGroup:
        stroke_color = line_config.pop("stroke_color", GREY_A)
        stroke_width = line_config.pop("stroke_width", 1.0)

        h_pad = self.h_cell_buff
        v_pad = self.v_cell_buff

        x_coords = [col.get_left()[0] - h_pad for col in self.columns]
        x_coords.append(self.columns[-1].get_right()[0] + h_pad)

        y_coords = [row.get_top()[1] + v_pad for row in self.rows]
        y_coords.append(self.rows[-1].get_bottom()[1] - v_pad)

        left = x_coords[0]
        right = x_coords[-1]
        top = y_coords[0]
        bottom = y_coords[-1]

        lines = VGroup()
        h_indices = range(len(y_coords))
        v_indices = range(len(x_coords))

        if not include_outer_lines:
            h_indices = range(1, len(y_coords) - 1)
            v_indices = range(1, len(x_coords) - 1)

        if include_horizontal_lines:
            for y in (y_coords[i] for i in h_indices):
                lines.add(Line(
                    [left, y, 0],
                    [right, y, 0],
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                    **line_config,
                ))

        if include_vertical_lines:
            for x in (x_coords[i] for i in v_indices):
                lines.add(Line(
                    [x, top, 0],
                    [x, bottom, 0],
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                    **line_config,
                ))

        return lines

    def get_cell(self, row: int, col: int) -> VMobject:
        n_rows = len(self.mob_matrix)
        n_cols = len(self.mob_matrix[0])
        if not (0 <= row < n_rows):
            raise IndexError(f"Row {row} out of range for table with {n_rows} rows")
        if not (0 <= col < n_cols):
            raise IndexError(f"Column {col} out of range for table with {n_cols} columns")
        return self.mob_matrix[row][col]

    def get_row(self, index: int) -> VGroup:
        if not 0 <= index < len(self.rows):
            raise IndexError(f"Row {index} out of range for table with {len(self.rows)} rows")
        return self.rows[index]

    def get_column(self, index: int) -> VGroup:
        if not 0 <= index < len(self.columns):
            raise IndexError(f"Column {index} out of range for table with {len(self.columns)} columns")
        return self.columns[index]

    def get_rows(self) -> VGroup:
        return self.rows

    def get_columns(self) -> VGroup:
        return self.columns

    def get_entries(self) -> VGroup:
        return VGroup(*self.elements)

    def get_mob_matrix(self) -> list[list[VMobject]]:
        return self.mob_matrix

    def get_column_widths(self) -> list[float]:
        return list(self.column_widths)

    def set_row_colors(self, *colors: ManimColor) -> Self:
        for color, row in zip(colors, self.rows):
            row.set_color(color)
        return self

    def set_column_colors(self, *colors: ManimColor) -> Self:
        for color, column in zip(colors, self.columns):
            column.set_color(color)
        return self
