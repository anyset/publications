from publications.utils.graph_helper import GraphHelper
from publications.utils import config
import json


def pprint(d: dict):
    print(json.dumps(d, sort_keys=True, indent=4))


def run():
    with open(config.graph["file"], encoding='utf-8') as file:
        graph = json.load(file)
    gh = GraphHelper(graph['graph']['nodes'], graph['graph']['edges'])

    print("Publications by drugs for the specific date of 2019-01-01")
    pprint(gh.query(relations=['is_referenced'], group_by='source', date='2019-01-01'))
    print("\n")

    print("Journals by publications for the specific date of 2019-01-01")
    pprint(gh.query(relations=['is_mentioned'], group_by='source', date='2019-01-01'))
    print("\n")

    print("Publications by journals for the specific date of 2019-01-01")
    pprint(gh.query(relations=['is_mentioned'], group_by='target', date='2019-01-01'))
    print("\n")

    print("All journal references by drugs (transitive query")
    pprint(gh.query(relations=['is_referenced', 'is_mentioned'], group_by='source'))

    print("\n")
    print("All drugs by journal reference (transitive query)")
    drugs_by_journal = gh.query(relations=['is_mentioned', 'is_referenced'], group_by='target')
    pprint(drugs_by_journal)

    print("\n")
    print("Drugs by journal filtered by pubmed")
    drugs_by_journal_filtered_by_pubmed = gh.query(relations=['is_mentioned', 'is_referenced'], group_by='target', type="pubmed")
    pprint(drugs_by_journal_filtered_by_pubmed)

    print("\n")
    print("Journal with most mentions")
    pprint(sorted(drugs_by_journal.items(), key=lambda x: len(x[1])).pop())

    def drugs_referenced_by_same_journals_from_pubmed(drug: str):
        result = set()
        for journal, drugs in drugs_by_journal_filtered_by_pubmed.items():
            if drug in drugs:
                result.update(drugs)
        result.remove(drug)
        return result

    print("\n")
    print("Drugs referenced by same journals from pubmed - example for TETRACYCLINE")
    print(drugs_referenced_by_same_journals_from_pubmed('TETRACYCLINE'))

    print("\n")
    print("Drugs referenced by same journals from pubmed - example for ETHANOL")
    print(drugs_referenced_by_same_journals_from_pubmed('ETHANOL'))


