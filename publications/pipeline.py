import pandas as pd
import json
from publications.utils.deduplication import deduplicate
from publications.utils.validation import validate_publication_date, validate_journal
from publications.utils.graph_builder import build_nodes, build_edges, build_graph
from publications.utils.loader import FileLoader
from publications.utils import config


def run():
    pubs = load_publications()
    pubs = validate_publication(pubs)
    pubs = deduplicate_publication(pubs)
    pubs = add_unique_id(pubs)

    drugs = load_drugs()

    nodes = build_nodes(pubs, drugs)
    edges = build_edges(pubs, drugs)
    graph = build_graph(nodes, edges)
    write(graph, config.graph["file"])


def load_publications():
    frames = []
    for publication in config.publications:
        loader = FileLoader(
            file_path=publication["file"],
            file_format= publication["format"],
            column_mapping=publication.get("columns_mapping")
        )
        df = loader.load()
        df["type"] = publication["type"]
        frames.append(df)
    return pd.concat(frames,  ignore_index=True)


def load_drugs():
    loader = FileLoader(config.drugs["file"], config.drugs["format"])
    return loader.load()


def deduplicate_publication(df: pd.DataFrame):
    df = deduplicate(df, ['title', 'date'])
    df = deduplicate(df, ['id'])
    return df


def validate_publication(df):
    df["date"] = df.apply(lambda x: validate_publication_date(x.date, x.journal), axis=1)
    df["journal"] = df["journal"].apply(validate_journal)
    return df


def add_unique_id(df):
    df['uid'] = df['type'].astype(str) + '_' + df['id'].astype(str)
    return df


def write(file: dict, path: str):
    with open(path, 'w') as fp:
        json.dump(file, fp, ensure_ascii=False, indent=2)

