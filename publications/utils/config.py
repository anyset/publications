publications: list = [
    {
        "type": "pubmed",
        "format": "csv",
        "file": "data/pubmed.csv"
    },
    {
        "type": "pubmed",
        "format": "json",
        "file": "data/pubmed.json"
    },
    {
        "type": "clinical_trials",
        "file": "data/clinical_trials.csv",
        "format": "csv",
        "columns_mapping": {
            "id": "id",
            "scientific_title": "title",
            "date": "date",
            "journal": "journal"
        }
    }
]

drugs: dict = {
    "file": "./data/drugs.csv",
    "format": "csv"
}

graph: dict = {
    "file": "target/publications_graph.json"
}

journal_referential: list[dict] = [
    {
        'name': 'American journal of veterinary research',
        'date_format': {
            'day_first': False
        }
    },
    {
        'name': 'The journal of allergy and clinical immunology. In practice',
        'date_format': {
            'day_first': True
        }
    },
    {
        'name': 'Hôpitaux Universitaires de Genève',
        'date_format': {
            'day_first': True
        }
    },
    {
        'name': 'The Journal of pediatrics',
        'date_format': {
            'day_first': False
        }
    },
    {
        'name': 'Journal of emergency nursing',
        'date_format': {
            'day_first': True
        }
    },
    {
        'name': 'Journal of food protection',
        'date_format': {
            'day_first': True
        }
    },
    {
        'name': 'Psychopharmacology',
        'date_format': {
            'day_first': True
        }
    },
    {
        'name': 'Journal of photochemistry and photobiology. B, Biology',
        'date_format': {
            'day_first': True
        }
    },
    {
        'name': 'The journal of maternal-fetal & neonatal medicine',
        'date_format': {
            'day_first': True
        }
    },
    {
        'name': 'Journal of back and musculoskeletal rehabilitation',
        'date_format': {
            'day_first': True
        }
    }
]
