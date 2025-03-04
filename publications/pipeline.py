import pandas as pd
import json
from publications.utils.deduplication import deduplicate
from publications.utils.validation import validate_publication_date, validate_journal
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


def is_mentioned(drugs: pd.DataFrame, title: str) -> bool:
    return drugs['drug'].lower() in title.lower()


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


def build_nodes(pubs: pd.DataFrame, drugs: pd.DataFrame):
    nodes = {}
    for i in pubs.index:
        row = pubs.loc[i].to_dict()
        nodes[row["uid"]] = {
            "label": row["title"],
            "metadata": row
        }
    for i in drugs.index:
        row = drugs.loc[i].to_dict()
        nodes[row["atccode"]] = {
            "label": row["drug"],
            "metadata": {
                "type": "drug"
            }
        }
    journals = pubs['journal'].drop_duplicates()
    for i in journals.index:
        journal = journals.loc[i]
        nodes[journal] = {
            "label": journal,
            "metadata": {
                "type": "journal"
            }
        }
    return nodes


def build_edges(publications: pd.DataFrame, drugs: pd.DataFrame):
    edges = []
    for i in publications.index:
        row = publications.loc[i]
        drug_refs = drugs[drugs.apply(is_mentioned, title=row['title'], axis=1)]['atccode']
        for drug_ref in drug_refs:
            # drugs by publication
            edge = {
                'source': drug_ref,
                'target': row['uid'],
                "relation": "is_referenced",
                "metadata": {
                    "date": row["date"],
                    "type": row['type']
                }
            }
            edges.append(edge)
        # publication by journal
        edge = {
            'source': row['uid'],
            'target': row['journal'],
            "relation": "is_mentioned",
            "metadata": {
                "date": row["date"],
                "type": row['type']
            }
        }
        edges.append(edge)
    return edges


def build_graph(nodes: dict, edges: list) -> dict:
    return {
        "graph": {
            "id": "Publications",
            "type": "drugs references by publications and journals",
            "label": "Publications",
            "nodes": nodes,
            "edges": edges

        }
    }
