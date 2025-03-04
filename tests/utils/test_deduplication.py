from publications.utils import deduplication
import pandas as pd


def test_deduplicate_group_key_none():
    d = [{
        'id': None,
        'title': 'abcd',
        'date': '2022',
        "col": None
    }]

    df = pd.DataFrame.from_dict(d)
    result = deduplication.deduplicate(df, ['id'])
    assert result.to_dict(orient='records') == d


def test_deduplicate_group_key_multiple_none():
    d = [{
        'id': None,
        'title': 'abcd',
        'date': '2022',
        "col": None
    }, {
        'id': None,
        'title': 'abcd',
        'date': None,
        "col": "value"
    }]
    df = pd.DataFrame.from_dict(d)
    result = deduplication.deduplicate(df, ['id'])
    assert result.to_dict(orient='records') == d


def test_deduplicate_values():
    d = [{
        'id': 1,
        'title': None,
        'date': '2022',
        "col": None
    }, {
        'id': 1,
        'title': 'abcd',
        'date': None,
        "col": "value"
    }]
    df = pd.DataFrame.from_dict(d)
    result = deduplication.deduplicate(df, ['id'])
    print(result)
    assert result.to_dict(orient='records') == [{
        'id': 1,
        'title': 'abcd',
        'date': '2022',
        "col": "value"
    }]

