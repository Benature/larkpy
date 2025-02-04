from larkpy import LarkBitTable
import pandas as pd

CONFIG = {}

table = LarkBitTable(app_id=CONFIG["app_id"],
                     app_secret=CONFIG["app_secret"],
                     wiki_token="xxx",
                     table_id="xxx")

df = table.search(
    view_id="xxx",
    filter=dict(conjunction="and",
                conditions=[table._cond("key", "is", "last_update_time")]),
    out=pd.DataFrame)
