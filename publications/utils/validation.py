import dateutil.parser
from publications.utils.config import journal_referential


def validate_publication_date(date_string: str, journal: str | None):
    day_first = True
    date_format = get_date_format(journal)
    if date_format is not None:
        day_first = date_format["day_first"]
    d = dateutil.parser.parse(date_string, dayfirst=day_first)
    return d.strftime("%Y-%m-%d")


def get_date_format(journal: str | None):
    if journal:
        for journal_ref in journal_referential:
            if journal_ref['name'] == journal:
                return journal_ref["date_format"]


def validate_journal(journal: str | None):
    if journal and journal.startswith("Journal of emergency nursing"):
        return "Journal of emergency nursing"
    return journal





