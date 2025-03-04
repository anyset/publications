"""
helper methods to query a graph document
"""
from publications.utils.logging import logger


class GraphHelper:
    def __init__(self, nodes: dict, edges: dict):
        self.nodes = nodes
        self.edges = edges

    def query(self, relations: list, group_by='source', **filters) -> dict:
        """
        Transitive query on graph edges, aggregates results either on source or target.
        Example :
        ```
            drugs_by_journal_filtered_by_pubmed = graph_helper.query(
                    relations=['is_mentioned', 'is_referenced'],
                    group_by='target',
                    type="pubmed")
        ```
        :param relations: List of transitive relations to apply sequentially
        :param group_by: Must be one of 'source' or 'target'
        :param filters: All filters to apply on edges metadata
        :return: dict
        """
        result = self.transitive_query(relations=relations, group_by=group_by, **filters)
        return self.enrich(result)

    def enrich(self, refs: dict):
        result = {}
        for key, values in refs.items():
            enrich_values = [self.nodes[value]["label"] for value in values]
            result[self.nodes[key]["label"]] = enrich_values
        return result

    def filter(self, relation: str, **kwargs):
        """
        Return edges filtered for given relation,
        and satisfying kwargs condition on metadata fields if field exists
        Example query:
        ```
        filtered edges =  graph_helper('is_mentioned', date='2020-01-01', type='pubmed')
        ```
        :param relation:
        :param kwargs:
        :return:
        """
        def satisfy(s: dict, conditions: dict):
            for key, value in conditions.items():
                if key in s and s[key] != value:
                    return False
            return True
        edges = [e for e in self.edges if e["relation"] == relation and satisfy(e['metadata'], kwargs)]
        return edges

    @staticmethod
    def group_by_key(refs: list[dict], key: str, value: str):
        result = {}
        for d in refs:
            result.setdefault(d[key], set()).add(d[value])
        return result

    def filter_and_group(self, relation, group_by='source', **kwargs):
        if group_by == 'source':
            value = 'target'
        elif group_by == 'target':
            value = 'source'
        else:
            raise ValueError("'group_by' parameter should be either 'source' or 'target'")
        edges = self.filter(relation, **kwargs)
        result = self.group_by_key(edges, key=group_by, value=value)
        return result

    def transitive_query(self, relations: list, result: dict = None, group_by='source', **kwargs):
        if len(relations) == 0:
            return result
        relation = relations.pop()
        intermediate = self.filter_and_group(relation, group_by, **kwargs)
        if result is None:
            result = intermediate
        else:
            for key, values in intermediate.items():
                transitive_values = [result[value] for value in values if value in result]
                if not transitive_values:
                    logger.warning(f"No transitive value found for set {values} and relation '{relation}'")
                    intermediate[key] = {}
                else:
                    intermediate[key] = set.union(*transitive_values)
            result = intermediate
        return self.transitive_query(relations, result, group_by, **kwargs)



