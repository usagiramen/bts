import pandas as pd
import plotly as py
import plotly.graph_objs as go
import re

from src.data.google_sheet import Gsheet
from src.visualization.chart_layout import Layout, palette

# initialize plotly offline mode.
py.offline.init_notebook_mode(connected=True)

# initialise logging
log = make_logger()


class Visualize():
    """Generic tool for visualization in Jupyter Notebooks.

    This class allow users to generate great looking visualizations quickly.
    It takes in data from CSV files, Google Sheets, BigQuery as sources,
    converts it to pandas DataFrame, and build the visualization based on
    prefix template.

    Attributes:
        self.df (pd.DataFrame): raw data in DataFrame type.
        self.x (str): x-axis column name.
        self.y (str/list): y-axis column name(s). Use list of str for
            multiple columns.
    """

    def __init__(self, data):

        self.project_id = "woven-bonbon-90705"  # set default GBQ project ID.
        self.df = self._to_dataframe(data)

        self.annotations = {}
        self.barmode = None

    def _to_dataframe(self, raw):
        """Convert data source to pandas dataframe.

        Args:
            raw (obj): CSV filepath.
        Returns:
            raw (pd.DataFrame): Dataset in DataFrame type.
        """

        if isinstance(raw, pd.DataFrame):
            return raw

        if isinstance(raw, str):
            raw_string = raw.replace('\n', ' ')
            print(raw_string)
            if re.match(r'(|.+)SELECT.+FROM.+', raw_string):
                return self._process_bigquery(raw_string)

            if re.match(r'https://docs.google.com\/spreadsheets', raw_string):
                return self._process_gsheet(raw_string)

            if raw_string[-4:] == '.csv':
                return pd.read_csv(raw_string)

        # unknown data type.
        log.error("Unknown data type. Please ping weijian.")
        return None

    def _format_labels(self, column_name, label=None):
        """Format x and y labels.

        Args:
            column_name (str): Column name.
            label (str): Axis label.
        Return:
            label (str): Formatted Axis label.
        """

        if label is None:
            return column_name.replace('_', ' ')
        else:
            return label

    def _make_hbar_plot(self, x, y, n, **kwargs):
        """Build data plots for horizontal bar.

        Args:
            x (str): X-axis column a.k.a dimension.
            y (str): Y-axis column a.k.a measures.
            n (int): Sequence.
        Returns:
            hbar (dict): data for horizontal bar plot.
        """

        y_values = [float(v) for v in self.df[y]]
        hbar = go.Bar(
            x=y_values,
            y=self.df[x],
            name=y,
            marker=dict(color=palette(n)),
            orientation='h',
            **kwargs
        )

        return hbar

    def _make_vbar_plot(self, x, y, n, **kwargs):
        """Build data plots for vertical bar.

        Args:
            x (str): X-axis column a.k.a dimension.
            y (str): Y-axis column a.k.a measures.
            n (int): Sequence.
        Returns:
            vbar (dict): Data for vertical bar plot.
        """

        y_values = [float(v) for v in self.df[y]]
        vbar = go.Bar(
            x=self.df[x],
            y=y_values,
            name=y,
            marker=dict(color=palette(n)),
            **kwargs
        )

        return vbar

    def _make_dist_plot(
        self, column_name, n, overlay=False, prob=False, cumsum=False,
        **kwargs
    ):
        """Build data plots for distribution.

        Args:
            values (list):
            n (int): Sequence.
        Returns:
            dist (dict): Data for distribution plot.
        """

        opacity = .5 if overlay else None
        histogram_mode = 'probability' if prob else None

        values = [float(v) for v in self.df[column_name]]
        dist = go.Histogram(
            x=values,
            opacity=opacity,
            name=column_name,
            marker=dict(color=palette(n)),
            histnorm=histogram_mode,
            cumulative=dict(enabled=cumsum),
            **kwargs
        )

        return dist

    def _make_scatter_plot(self, x, y, n, mode, **kwargs):
        """Build data plots for scatter.

        Args:
            x (str): X-axis column a.k.a dimension.
            y (str): Y-axis column a.k.a measures.
            n (int): Sequence.
            mode (str): Lines/Scatter mode.
        Returns:
            scatter (dict): Data for scatter plot.

        """

        y_values = [float(v) for v in self.df[y]]
        scatter = go.Scatter(
            x=self.df[x],
            y=y_values,
            name=y,
            mode=mode,
            marker=dict(color=palette(n)),
        )

        return scatter

    def bar(
        self, x, y, title, stack=False, horizontal=False,
        x_range=None, y_range=None, xlabel=None, ylabel=None
    ):
        """Generate bar chart.

        Args:
            x (str): X-axis column, a.k.a dimension.
            y (str/list): Y-axis column, a.k.a measures.
            title (str): Chart title.
            xlabel (str): Label for x-axis (optional).
            ylabel (str): Label for y-axis (optional).
            stack (bool): Convert to stacked bar chart.
            horizontal (bool): Convert to horizontal chart.
        Returns:
            status (bool): Visualization success.
        """

        data = []
        y = y if isinstance(y, list) else [y]

        for n, value_name in enumerate(y):
            if horizontal:
                bar = self._make_hbar_plot(x, value_name, n)
            else:
                bar = self._make_vbar_plot(x, value_name, n)

            data.append(bar)

        # set title, xlabel, and ylabels.
        annotations = dict(
            chart_title=title,
            xlabel=self._format_labels(x, xlabel),
            ylabel=self._format_labels(y[0], ylabel),
        )
        style = Layout(**annotations)

        layout = style.default(
            axis_args={
                'x': dict(range=x_range),
                'y': dict(range=y_range),
            },
            barmode='stack' if stack else None,
        )
        figure = go.Figure(data=data, layout=layout)
        py.offline.iplot(figure, show_link=False)

        return True

    def combo(
        self, x, bars, lines, title, x_range=None, bar_range=None,
        line_range=None, xlabel=None, bar_label=None, line_label=None,
        stack=None
    ):
        """Generate combo bar and line chart.

        Args:
            x (str): Column name for X-axis.
            bar (str/list): Column name(s) for bar chart.
            line (str/list): Column name(s) for line chart.
            title (str): Chart title.
            x_range (list): Limit range for x-axis in [min, max] format.
            bar_range (list): Limit range for bar (left-side) y-axis.
            line_range (list): Limit range for line (right-side) y-axis.
            bar_label (str): Custom label name for bar chart (left side).
            line_label (str): Custom label name for line chart (right side).
        Returns:
            status (bool): Visualization success.
        """

        data = []
        bars = bars if isinstance(bars, list) else [bars]
        lines = lines if isinstance(lines, list) else [lines]

        for n, bar_name in enumerate(bars):
            bar = self._make_vbar_plot(x, bar_name, n)

            data.append(bar)

        for n, line_name in enumerate(lines):
            line = go.Scatter(
                x=self.df[x],
                y=[float(v) for v in self.df[line_name]],
                name=line_name,
                mode="lines+markers",
                marker=dict(color=palette(n + 1)),
                yaxis="y2",
            )
            data.append(line)

        # set title, xlabel, and ylabels.
        annotations = dict(
            chart_title=title,
            xlabel=self._format_labels(x, xlabel),
            ylabel=self._format_labels(bars[0], bar_label),
            y2label=self._format_labels(lines[0], line_label),
        )
        style = Layout(**annotations)

        layout = style.two_y_axes(
            axis_args={
                'x': {'range': x_range},
                'y': {'range': bar_range},
                'y2': {'range': line_range},
            },
            barmode='stack' if stack else None,
        )
        figure = go.Figure(data=data, layout=layout)
        py.offline.iplot(figure, show_link=False)

        return True

    def dist(
        self, values, title, x_range=None, y_range=None, label=None,
        overlay=False, prob=False, cumsum=False
    ):
        """Generate distribution.

        Args:
            values (str/list): Distribution values column name(s).
            title (str): Chart title.
            x_range (list): Min and max range values for X-axis.
            y_range (list): Min and max range values for Y-axis.
            label (str): Label for distribution values (optional).
            overlay (bool): Overlay multiple distributions.
            prob (bool): Convert values to probability.
            cumsum (bool): Convert to cumulative sum.
        Returns:
            status (bool): Visualization success.
        """

        data = []
        y = values if isinstance(values, list) else [values]

        for n, column_name in enumerate(y):
            histogram = self._make_dist_plot(
                column_name=column_name,
                n=n,
                overlay=overlay,
                prob=prob,
                cumsum=cumsum,
            )
            data.append(histogram)

        # set title, xlabel, ylabels.
        annotations = dict(
            chart_title=title,
            xlabel=self._format_labels(values, label),
            ylabel="Probability (%)" if prob else "Count",
        )
        style = Layout(**annotations)

        layout = style.default(
            axis_args={
                'x': dict(range=x_range),
                'y': dict(range=y_range),
            },
            barmode='overlay' if overlay else None
        )
        figure = go.Figure(data=data, layout=layout)
        py.offline.iplot(figure, show_link=False)

        return True

    def line(
        self, x, y, title=None, x_range=None, y_range=None,
        xlabel=None, ylabel=None
    ):
        """Generate line chart."""

        data = []
        y = y if isinstance(y, list) else [y]

        for n, value_name in enumerate(y):
            line = self._make_scatter_plot(
                x=x, y=value_name, n=n,
                mode="lines+markers",
            )
            data.append(line)

        annotations = dict(
            chart_title=title,
            xlabel=self._format_labels(x, xlabel),
            ylabel=self._format_labels(y[0], ylabel),
        )
        style = Layout(**annotations)

        layout = style.default(
            axis_args={
                'x': dict(range=x_range),
                'y': dict(range=y_range),
            }
        )
        figure = go.Figure(data=data, layout=layout)
        py.offline.iplot(figure, show_link=False)

    def scatter(
        self, x, y, title=None, x_range=None, y_range=None,
        xlabel=None, ylabel=None
    ):
        """Generate scatter plot."""

        data = []
        y = y if isinstance(y, list) else [y]

        for n, value_name in enumerate(y):
            line = self._make_scatter_plot(
                x=x,
                y=value_name,
                n=n,
                mode="markers",
            )
            data.append(line)

        annotations = dict(
            chart_title=title,
            xlabel=self._format_labels(x, xlabel),
            ylabel=self._format_labels(y[0], ylabel),
        )
        style = Layout(**annotations)

        layout = style.default(
            axis_args={
                'x': dict(range=x_range),
                'y': dict(range=y_range),
            }
        )
        figure = go.Figure(data=data, layout=layout)
        py.offline.iplot(figure, show_link=False)

    def pie(self, x, y, title=None, xlabel=None, ylabel=None):
        """Generate pie chart."""

        pie = go.Pie(
            labels=self.df[x],
            values=[float(v) for v in self.df[y]],
            name=x,
            hole=.4,
            marker=dict(colors=palette(as_list=True)),
        )

        annotations = dict(
            chart_title=title,
            xlabel=self._format_labels(x, xlabel),
            ylabel=self._format_labels(y[0], ylabel),
        )
        style = Layout(**annotations)
        layout = style.default()
        figure = go.Figure(data=[pie], layout=layout)
        py.offline.iplot(figure, show_link=False)
