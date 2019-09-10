import numpy as np
import plotly.graph_objs as go

HEIGHT = 500
WIDTH = HEIGHT * (1.5 + np.sqrt(5)) / 2  # golden ratio.
MARGIN = dict(l=80, r=80, t=100, b=80)

# fonts
FONT_FAMILY = "Trebuchet MS"
FONT_SIZE = 16
TITLE_SIZE = FONT_SIZE + 8

# color pallete
GREY_BACKGROUND = "#EFECEA"
WHITE_BACKGROUND = "#FFFFFF"
DARK_TEXT = "#635F5D"
LIGHT_TEXT = "#8E8883"

PALETTE = [
    '#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f',
    '#edc948', '#b07aa1', '#ff9da7', '#9c755f', '#bab0ac'
]


def palette(n=1, theme=PALETTE):
    """Cycle through color palette and return a color."""

    color_length = len(theme)

    if n > len(theme):
        color = theme[n - color_length - 1]
    else:
        color = theme[n - 1]

    return color


class Layout():
    """Set of default parameteres for the chart layout."""

    def __init__(self, chart_title, xlabel, ylabel, y2label=None):

        self.title = chart_title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.y2label = y2label

    def _annotations(self):
        """Build xlabel, ylabel, title using annotations."""

        y_tilt = 0  # y-label tilt.
        vertical_space = HEIGHT - MARGIN['t'] - MARGIN['b']
        horizontal_space = WIDTH - MARGIN['l'] - MARGIN['r']

        title = dict(
            x=-(MARGIN['l'] - 20) / horizontal_space,
            y=1 + (MARGIN['t'] - 10) / vertical_space,
            font=dict(size=TITLE_SIZE, color=DARK_TEXT),
            xref="paper",
            xanchor="left",
            yref="paper",
            yanchor="top",
            text=self.title,
            showarrow=False,
        )

        ylabel = dict(
            x=-(MARGIN['l'] - 20) / horizontal_space,
            y=1 + (MARGIN['t'] - 20 - TITLE_SIZE - y_tilt) / vertical_space,
            font=dict(size=FONT_SIZE, color=LIGHT_TEXT),
            xref="paper",
            xanchor="left",
            yref="paper",
            yanchor="top",
            text=self.ylabel,
            showarrow=False,
        )

        xlabel = dict(
            x=0.5,
            y=-(MARGIN['b'] - 10) / vertical_space,
            font=dict(size=FONT_SIZE, color=LIGHT_TEXT),
            xref="paper",
            xanchor="center",
            yref="paper",
            yanchor="bottom",
            text=self.xlabel,
            showarrow=False,
        )

        return (title, ylabel, xlabel)

    def _canvas_white(self):
        """Generate visualisation with white canvas, grey grid layout."""

        font_dict = dict(family=FONT_FAMILY)

        canvas_layout = dict(
            width=WIDTH,
            height=HEIGHT,
            font=font_dict,
            hoverlabel=dict(font=font_dict),
            plot_bgcolor=WHITE_BACKGROUND,
            paper_bgcolor=WHITE_BACKGROUND,
            margin=MARGIN,
            annotations=self._annotations()
        )

        return canvas_layout

    def _axis_no_titles(self, axis_args=None):
        """Generate visualisation default axis layout."""

        grid_width = 2

        axis_layout = dict(
            tickfont=dict(size=FONT_SIZE),
            ticklen=5,
            tickwidth=grid_width,
            showgrid=True,
            gridcolor=WHITE_BACKGROUND,
            gridwidth=grid_width,
            zeroline=False,
            linewidth=6,
            linecolor=GREY_BACKGROUND,
        )

        if axis_args is not None:
            axis_layout.update(**axis_args)

        return axis_layout

    def _white_axis_no_titles(self, axis_args, **kwargs):
        """Generate visualisation white axis layout."""

        grid_width = 2

        axis_layout = dict(
            tickfont=dict(size=FONT_SIZE),
            ticklen=5,
            tickwidth=grid_width,
            showgrid=True,
            gridcolor=GREY_BACKGROUND,
            gridwidth=grid_width,
            zeroline=False,
            linewidth=6,
            linecolor=WHITE_BACKGROUND,
        )

        if axis_args:
            axis_layout.update(**axis_args)

        # update other axis arguments.
        axis_layout.update(**kwargs)

        return axis_layout

    def _legend_grey(self):
        """Generate visualisation default legend layout."""

        legend_background = '#E5E2E0'
        # legend_border = '#C0C0BB'

        legend = dict(
            bgcolor=legend_background,
            bordercolor=legend_background,
            borderwidth=1,
            font=dict(size=FONT_SIZE, color=DARK_TEXT),
            xanchor="left",
            x=1.08,  # legend X position
            yanchor="bottom",
            y=0.  # legend Y position
        )

        return legend

    def _format_to_y2(self, axis):
        """Format this axis (default left-side) to right-side axis.

        Args:
            axis (dict): Y-axis arguments in dict.
        Return:
            formatted_axis (dict): Formatted Y-axis argument in dict.
        """

        y2_args = axis

        if "overlaying" not in y2_args:
            y2_args['overlaying'] = "y"

        if "side" not in y2_args:
            y2_args['side'] = "right"
        y2_args
        return y2_args

    def default(self, axis_args=None, **kwargs):
        """Generate default chart layout and style.

        Args:
            axis_args (dict): Arguments for x/y axes.
        """

        canvas = self._canvas_white()
        canvas.update(**kwargs)

        # separate x and y-axis arguments.
        if axis_args is not None:
            xaxis_args = axis_args['x'] if 'x' in axis_args.keys() else None
            yaxis_args = axis_args['y'] if 'y' in axis_args.keys() else None
        else:
            xaxis_args = None
            yaxis_args = None

        default_layout = go.Layout(
            xaxis=self._axis_no_titles(xaxis_args),
            yaxis=self._axis_no_titles(yaxis_args),
            legend=self._legend_grey(),
            **canvas
        )

        return default_layout

    def two_y_axes(self, axis_args, **kwargs):
        """Generate chart layout with two y-axis.

        Args:
            axis_args (dict): Arguments for x/y axes.
        """

        canvas = self._canvas_white()
        canvas.update(**kwargs)

        # include necessary arguments for y2-axis.
        y2_args = self._format_to_y2(axis_args['y2'])

        axis_layout = go.Layout(
            xaxis=self._white_axis_no_titles(axis_args['x']),
            yaxis=self._white_axis_no_titles(axis_args['y']),
            yaxis2=self._white_axis_no_titles(y2_args),
            legend=self._legend_grey(),
            **canvas
        )

        return axis_layout

    def two_columns_subplot(self, axis_args, **kwargs):
        """Generate chart layout with side-by-side subplots.

        Args:
            axis_args (dict): Arguments for x/y axes.
        """

        canvas = self._canvas_white()
        canvas.update(**kwargs)

        subplot_layout = go.Layout(
            xaxis=self._white_axis_no_titles(axis_args['x'], domain=[0, .4]),
            yaxis=self._white_axis_no_titles(axis_args['y']),
            xaxis2=self._white_axis_no_titles(axis_args['x'], domain=[.5, .9]),
            yaxis2=self._white_axis_no_titles(axis_args['x'], anchor='x2'),
            **canvas
        )

        return subplot_layout
