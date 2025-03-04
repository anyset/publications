"""
Some publication entries are considered duplicates when IDs are identical, or when (title, date) are identical.
Moreover, some entries will be incomplete (missing id, or other attributes).
Rules for deduplication:
 - group by given columns
 - aggregate on a list of value for all other columns
 - keep first non-blank value in list
 - Never deduplicate on null key
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def deduplicate(df: pd.DataFrame, group_columns: list[str]) -> pd.DataFrame:
    # Do not deduplicate on group by null
    for col in group_columns:
        if df[col].isnull().all():
            return df
    groups = df.groupby(group_columns, as_index=False).agg(list)
    cols = [col for col in list(df.columns) if col not in group_columns]
    for col in cols:
        groups[col] = groups[col].apply(first_non_blank)
    return groups


def first_non_blank(values: list):
    res = [val for val in values if val]
    if len(values) > 1:
        logger.info("found duplicate values: " + str(values) + str(res))
    return res.pop() if res else None
