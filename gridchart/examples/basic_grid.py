try:
    from gridchart import js, Grid
except ModuleNotFoundError:
    import os

    os.chdir("../..")
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


abc = Grid(df, resizable=True)

abc.update_in_place(
    resizable=True,
    columns=[
        {"name": "Num"},
        {
            "name": "Fruit",
            "formatter": js(
                """(cell, row)=>gridjs.html(`<span style="color:${row.cells[0].data>0?'black':'green'}">${cell}</span>`)"""
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


# The following example shows how to merge cells. I would like to incorporate
# that functionality directl
df2 = (
    df.with_row_index("__i")
    .join_asof(
        df.with_row_index("__i")
        .group_by("d", rle=pl.col("d").rle_id(), maintain_order=True)
        .agg(min=pl.col("__i").min(), max=pl.col("__i").max())
        .filter(pl.col("min") != pl.col("max")),
        left_on="__i",
        right_on="min",
        by="d",
    )
    .with_columns(
        d_merge_map=(
            pl.when(pl.col("__i") == pl.col("min"))
            .then(
                pl.lit("rowspan=") + (pl.col("max") - pl.col("min") + 1).cast(pl.String)
            )
            .when(pl.col("rle").is_not_null())
            .then(pl.lit("hide"))
        )
    )
    .drop("__i", "rle", "min", "max")
    .with_columns(pl.col("d_merge_map").fill_null(""))
)

xy = Grid(
    df2,
    columns=[
        "a",
        "b",
        "c",
        {
            "name": "d",
            "attributes": js(
                """(_, row) => {
                if (row !=null) {
                    const split = row._cells[4].data.split('=');
                    if (split.length>1) {
                        return {
                            rowspan:split[1]
                        }
                    } else if (row._cells[4].data.search('hide')!=-1) {
                        return {
                            style:'display:none'
                        }
                    } else {
                        return {}
                    }
                }
                }"""
            ),
        },
        {"name": "d_merge_map", "hidden": 1},
    ],
)
