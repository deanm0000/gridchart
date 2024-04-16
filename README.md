# GridChart

## What is it?

It's a library built from scratch on top of polars to create graphs and tables (grids) for notebooks with interactivity in mind.

## Why make another graphing library?

This is really a case of a lot of little things. plotly, holoviz, and whatever else are all fine. My two motivations to making yet another graphing library for python is to have it be entirely based on polars (no pandas) and that I just like the look of [Chart.js](https://www.chartjs.org/) graphs more than other D3 abstractions. Since I use Chart.js in React dashboards, it would make my notebook based static reports look more consistent if they both used Chart.js. 

## Why make another grid library?

I was using the pandas styler for a while which was always a struggle as the syntax is foreign to me as I don't use pandas for anything else. I found Great Tables which was a huge improvement over using pandas styler. They're even working to remove the pandas' dependencies so it would seem I should just love it. There are a couple things I don't like. They seem to try very hard to keep from exposing users from javascript which is nice for the functions that they've built in but for simple things like adjusting the row height or merging cells, it's just not possible. I'd also like for my output tables to have simple interactivity like resizing columns or sorting but they don't have that interactivity.

## Why [Grid.js](https://gridjs.io/)

I really wanted something that wasn't a freemium offering and that was updated within the last month. I didn't do a ton of research on grid.js but it seemed decent enough. It doesn't have row grouping built in which is the biggest downside for me. One alternative is [TanStack Table](https://github.com/tanstack/table). My initial reluctance is I'm not sure to what extent it's freemium since it seems so intertwined with Ag-Grid. I like the novelty of [Glide Data Grid](https://grid.glideapps.com/) since it uses the canvas but it doesn't have row grouping and I'm not sure the novelty is worth it. Another library that looks good because of its MIT license and inclusion of row grouping is [react-data-grid](https://github.com/adazzle/react-data-grid/tree/main) but it hasn't been updated for 7 months.

# How to use it

## The simplest usage is

```
from gridchart import js, Grid
import polars as pl

df = pl.DataFrame(
    {
        "a": [-3, -2, -1, 0, 1, 2, 3],
        "b": ["apple", "banana", "carrot", "date", "eggplant", "fig", "grape"],
        "c": [1.12, 2.9495043, 1545.0, 1.0, 232, -494.9, 9],
        "d": ["ant", "ant", "clown", "darts", "elephant", "elephant", "clown"],
    }
)

df_grid=Grid(df)
```

When using `Grid` the only required input is a polars dataframe. Most of the parameters from [grid.js](https://gridjs.io/docs/config/columns) are passed through. Of course, the data parameter is missing as the dataframe is the data source. Also `from` and `server` have no place but all the other inputs are passed through to grid.js. If you want to use a js function then wrap it in `js()`. Under the hood, gridchart converts all the parameter inputs into json. When one or more of those inputs was wrapped with `js()` then it will remove the quotes from it so that js will interpret it as a function. When you call `Grid(df)` whether you assign it to a variable or not, it will invoke `IPython.display.display` immediately. The benefit of assigning it to a variable is the availability of the `update_in_place()` method where the parameters can be changed and the original grid will get those updates rather than rerendering the whole grid. For instance, from the previous example if you later wanted to rename the columns, color code the 2nd column based on the value of the first, decimal align the third, make the columns resizable, and apply borders then you could do

```
df_grid.update_in_place(
    resizable=True,
    columns=[
        {"name": "Num"},
        {
            "name": "Fruit",
            "formatter": js(
                "(cell, row)=>gridjs.html(`<span style=\"color:${row.cells[0].data>0?'black':'green'}\">${cell}</span>`)"
            ),
        },
        {
            "name": "Floats",
            "formatter": js("""(cell, row) => {
                console.log(row)
                let [i,f] = cell.toString().split('.');
                if (f==undefined) {
                    f=''
                } else {
                    i=i.concat('.')
                }
                return gridjs.html(`<span style=\"display:inline-block;width:30px;text-align:right\">${i}</span><span style=\"display:inline-block;width:40px;text-align:left\">${f}</span>`)
             }"""),
        },
    ],
    style={"table": {"border": "8px solid #ccc"}, "td": {"border": "3px solid #ccc"}},
)
```

Notice that to rename columns, it is sufficient to merely provide a list of strings where each element of the list will be a new column name. If providing a list of dicts then the columns can be customized. In the above case it uses the formatter key of the column dict. That takes a js function which is a string wrapped in js. Another note is that gridjs is imported as gridjs and its functions are callable as `gridjs.html` as seen above. 

## How it works under the hood.

When you import gridchart, it using IPython to display and run javascript code to download the js libraries from a CDN. When you create a table, it sends the data to a js object and then it calls the grid (or chart) library to access the data and build the output. That allows for the data to be sent to JS once and then you can fine tune the settings of the output without resending the data. That has an extra benefit in that if a table and a graph is of the same data, it doesn't need to serialize and send the data over and over. 

## What it doesn't do.

It doesn't have two-way communication from the js layer back to python so any changes made aren't extractable to the python variable.

## What's next (not in strict order)

### Chart.js

1. Add it to this library
2. Start from graph primitives such as bars and scatters and build up to histograms, eCDFs, and others.

### Grid.js
1. Make convenience options for grid so that the user doesn't need to use (as much) javascript
2. Either build row grouping that works with grid.js or switch libraries for row grouping

### Together
1. Do better with docstrings and CI/CD pipelines.
2. Make a data only class that allows for the creation of either grid or chart
3. Make a connector to cloud files and/or api so that data is downloaded async and isn't embedded in output html files
