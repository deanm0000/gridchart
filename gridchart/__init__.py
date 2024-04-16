import polars as pl
from IPython.display import HTML, Javascript, display
from uuid import uuid4
from typing import Tuple, TypeAlias, Literal


try:
    import orjson

    def dumps(py):
        return orjson.dumps(py).decode("utf-8").replace("\\n", "\n")
except ModuleNotFoundError:
    import json

    dumps = json.dumps

JS_DELIM = "48c086af"


def _js_dumps(py):
    return dumps(py).replace(f'"{JS_DELIM}', "").replace(f'{JS_DELIM}"', "")


def _try_getattr(obj, key):
    try:
        return getattr(obj, key)
    except AttributeError:
        return None


display(
    HTML("""
    <link href="https://unpkg.com/gridjs/dist/theme/mermaid.min.css" rel="stylesheet" />
    <script type="module">
        import * as gridjs from 'https://cdnjs.cloudflare.com/ajax/libs/gridjs/6.2.0/gridjs.production.es.min.js';
        window.gridjs = gridjs

        
    </script>
    <script>
        const waitForGridjs = new Promise((resolve) => {
            const checkGridjs = () => {
                if (window.gridjs) {
                    resolve(window.gridjs);
                } else {
                    setTimeout(checkGridjs, 50);
                }
            };
            checkGridjs();
        });
        const waitForVar = (varName)=> {
            return new Promise((resolve) => {
                const checkElement = () => {
                    if (window[varName]) {
                        resolve(window[varName]);
                    } else {
                        setTimeout(checkElement, 50);
                    }
                };
                checkElement();
            });
        }
    </script>
""")
)

Mode: TypeAlias = Literal["init", "update"]


def _make_config_str_and_uuid(Grid_obj, mode: Mode = "init") -> Tuple[str, str]:
    param_types = {
        "columns": (dict, list),
        "style": (dict, list),
        "className": (dict, list),
        "language": (dict, list),
        "width": str,
        "height": str,
        "autoWidth": bool,
        "fixedHeader": bool,
        "search": bool,
        "sort": bool,
        "pagination": (bool | dict | list),
        "resizable": bool,
    }
    if mode == "init":
        grid_uuid = str(uuid4())
        config_str = [f"data: window['data_{grid_uuid}'],"]
    elif mode == "update":
        grid_uuid = Grid_obj._grid_uuid
        config_str = []
    else:
        raise TypeError("mode is init or update")
    for ke, dtype in param_types.items():
        key = "_" + ke
        if (key != "_columns" or mode == "update") and _try_getattr(
            Grid_obj, key
        ) is None:
            continue
        elif (
            key == "_columns"
            and _try_getattr(Grid_obj, "_columns") is None
            and mode == "init"
        ):
            config_str.append(
                f"{ke}: {_js_dumps([{'name':x} for x in _try_getattr(Grid_obj, '_df').columns])},"
            )
        elif isinstance(_try_getattr(Grid_obj, key), dtype):
            config_str.append(f"{ke}: {_js_dumps(_try_getattr(Grid_obj, key))},")
        else:
            raise TypeError(f"{key} should be dict or list")
    config_str = "\n".join(config_str)
    return config_str, grid_uuid


def js(js_func_in_quotes):
    return JS_DELIM + js_func_in_quotes + JS_DELIM


class Grid:
    def __init__(
        self,
        df: pl.DataFrame,
        columns: dict | list = None,
        style: dict | list = None,
        className: dict | list = None,
        language: dict | list = None,
        width: str = None,
        height: str = None,
        autoWidth: bool = None,
        fixedHeader: bool = None,
        search: bool = None,
        sort: bool = None,
        pagination: bool | dict | list = None,
        resizable: bool = None,
    ):
        self._df = df
        if columns is None:
            columns = [{"name": x} for x in df.columns]
        self._columns = columns
        self._style = style
        self._className = className
        self._language = language
        self._width = width
        self._height = height
        self._autoWidth = autoWidth
        self._fixedHeader = fixedHeader
        self._search = search
        self._sort = sort
        self._pagination = pagination
        self._resizable = resizable

        self._config_str, self._grid_uuid = _make_config_str_and_uuid(self)
        display(
            HTML(f"""<div id="{self._grid_uuid}"/>"""),
            Javascript(
                f"""
                window['data_{self._grid_uuid}'] = {str([list(x) for x in df.iter_rows()])};
                window['grid_{self._grid_uuid}'] = undefined;
                waitForGridjs.then((gridjs) => {{
                    window['grid_{self._grid_uuid}'] = new gridjs.Grid({{
                        {self._config_str}
                    }})
                    window['grid_{self._grid_uuid}'].render(document.getElementById('{self._grid_uuid}'));
                    }}
                ).catch((error) => {{
                        console.error('Error loading gridjs:', error);
                }});
                """
            ),
        )

    def __repr__(self):
        ret_list = []
        for param in dir(self):
            if not (
                param[0] == "_"
                and param[1] != "_"
                and param not in ["_df", "_config_str", "_grid_uuid"]
                and (param_val := getattr(self, param)) is not None
            ):
                continue
            if isinstance(param_val, list):
                ret_list.append(f"{param[1:]} = [")
                spaces = " " * (len(ret_list[-1]) - 3)
                for val in param_val:
                    ret_list.append(f"{spaces}{val},")
                ret_list.append(f"{spaces}]")
            else:
                ret_list.append(f"{param[1:]} = {param_val}")
        return (
            "\n".join(ret_list)
            .replace(f"'{JS_DELIM}", 'js("""')
            .replace(f'"{JS_DELIM}', 'js("""')
            .replace(f"{JS_DELIM}'", '""")')
            .replace(f'{JS_DELIM}"', '""")')
            .replace("\\n", "\n")
            .replace("\\'", "'")
        )

    def update_in_place(
        self,
        columns: dict | list = None,
        style: dict | list = None,
        className: dict | list = None,
        language: dict | list = None,
        width: str = None,
        height: str = None,
        autoWidth: bool = None,
        fixedHeader: bool = None,
        search: bool = None,
        sort: bool = None,
        pagination: bool | dict | list = None,
        resizable: bool = None,
    ):
        self._columns = columns or self._columns
        self._style = style or self._style
        self._className = className or self._className
        self._language = language or self._language
        self._width = width or self._width
        self._height = height or self._height
        self._autoWidth = autoWidth or self._autoWidth
        self._fixedHeader = fixedHeader or self._fixedHeader
        self._search = search or self._search
        self._sort = sort or self._sort
        self._pagination = pagination or self._pagination
        self._resizable = resizable or self._resizable

        self._config_str, self._grid_uuid = _make_config_str_and_uuid(self, "update")
        # print(config_str)
        full_js_str = f"""
            waitForVar('grid_{self._grid_uuid}')
            .then(grid_elem => grid_elem.updateConfig({{{self._config_str}}}).forceRender())
            .catch(error=>console.error("error:", error))
            """
        # print(full_js_str)
        display(Javascript(full_js_str))
