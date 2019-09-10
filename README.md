# bts | better than seaborn
A Python wrapper library for generation visualisations using Plot.ly.

Plot.ly is a visualisation library that allows you to build fancy charts on your Jupyter Notebook. It also comes with alot of customisation, and lots of code to write before you can see the chart.

BTS aims to make visualisation quicker and easier.


## Usage

Example

```
# your data.
raw = np.array(1, 2, 3, 4, 5)
data = pd.DataFrame(raw)

# build a bar chart.
v = BTS(data)
v.bar()
```