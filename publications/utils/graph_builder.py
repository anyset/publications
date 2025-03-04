import pandas as pd


def is_mentioned(drugs: pd.DataFrame, title: str) -> bool:
    return drugs['drug'].lower() in title.lower()


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
