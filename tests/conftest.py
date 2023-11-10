import pytest
import pandas as pd
import polars as pl

from etlrules.backends import pandas as pd_rules
from etlrules.backends import polars as pl_rules


TYPE_MAPPING = {
    "pl": {
        "string": pl.Utf8,
        "int64": pl.Int64,
        "Int64": pl.Int64,
        "object": pl.Object,
        "float64": pl.Float64,
        "list_strings": pl.List(pl.Utf8),
        "datetime": pl.Datetime,
        "timedelta": pl.Duration,
    },
    "pd": {
        "datetime": "datetime64[ns]",
        "list_strings": "object",
        "timedelta": "timedelta64[ns]",
    }
}

class BackendFixture:
    def __init__(self, name, impl_pckg, rules_pckgs):
        self.name = name
        self.impl_pckg = impl_pckg
        self.rules_pckgs = rules_pckgs

    @property
    def impl(self):
        return self.impl_pckg

    @property
    def rules(self):
        return self.rules_pckgs

    def __str__(self):
        return self.name

    def DataFrame(self, data, dtype=None, astype=None):

        def get_data_keys(ddata):
            keys = []
            if isinstance(ddata, list):
                for elem in ddata:
                    assert isinstance(elem, dict)
                    for k in elem.keys():
                        if k not in keys:
                            keys.append(k)
            elif isinstance(ddata, dict):
                keys = list(ddata.keys())
            return keys

        if self.impl_pckg == pd:
            df = pd.DataFrame(data, dtype=TYPE_MAPPING["pd"].get(dtype, dtype))
            if astype is not None:
                df = df.astype({k: TYPE_MAPPING["pd"].get(v, v) for k, v in astype.items()})
        elif self.impl_pckg == pl:
            schema = None
            if dtype is not None:
                keys = get_data_keys(data)
                if keys:
                    schema = {k: TYPE_MAPPING["pl"][dtype] for k in keys}
            elif astype is not None:
                assert isinstance(astype, dict)
                keys = get_data_keys(data)
                schema = {
                    col: TYPE_MAPPING["pl"][astype[col]] if col in astype else None for col in keys
                }
            df = pl.DataFrame(data, schema)
        else:
            assert False, f"unknown impl_pckg: {self.impl_pckg}"
        return df

    def astype(self, df, astype):
        if self.impl_pckg == pd:
            astype = {
                col: TYPE_MAPPING["pd"][dtype] for col, dtype in astype.items()
            }
            return df.astype(astype)
        elif self.impl_pckg == pl:
            return df.with_columns(
                *[pl.col(col).cast(TYPE_MAPPING["pl"][dtype]) for col, dtype in astype.items()]
            )
        assert False, f"unknown impl_pckg: {self.impl_pckg}"

    def rename(self, df, rename_dict):
        if self.impl_pckg == pd:
            return df.rename(columns=rename_dict)
        elif self.impl_pckg == pl:
            columns = list(df.columns)
            if all(isinstance(key, int) and 0 <= key < len(columns) for key in rename_dict.keys()):
                rename_dict = {
                    columns[key]: val for key, val in rename_dict.items()
                }
            return df.rename(rename_dict)
        assert False, f"unknown impl_pckg: {self.impl_pckg}"

@pytest.fixture(params=[('pandas', pd, pd_rules), ('polars', pl, pl_rules)])
def backend(request):
    return BackendFixture(*request.param)