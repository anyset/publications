# Publications
<!-- TOC -->
* [Publications](#publications)
  * [Notes](#notes)
    * [Graph modelisation](#graph-modelisation)
    * [Processing pipeline](#processing-pipeline)
    * [Validate publications](#validate-publications)
      * [Validate date](#validate-date)
      * [Validate journal](#validate-journal)
      * [Deduplication](#deduplication)
    * [Build Graph](#build-graph)
      * [Nodes](#nodes)
      * [Edges](#edges)
    * [Graph Helpers](#graph-helpers)
      * [Examples](#examples-)
  * [Scalability](#scalability)
* [SQL](#sql)
  * [1. Sales by date](#1-sales-by-date)
  * [2. Sales by client and product type](#2-sales-by-client-and-product-type)
<!-- TOC -->
## Notes

### Graph modelisation

There may be multiple ways to modelize the pipeline output, the most scalable one would be as a graph, defining nodes and edges.
These [specifications](https://jsongraphformat.info/) don't seem much maintained but will be used in the context of this exercice.


### Processing pipeline
The processing pipeline may be deployed as a docker container [docker/Dockerfile](docker/Dockerfile), or executed by a scheduler
```
python -m publications.main
```

Several pipeline steps methods, as `validate`, `deduplicate`, `load`, `write` call more generic methods from the utils module, than can be exported as a library and reused, eventually as udf.  

### Validate publications

#### Validate date
All publication date follow different format standards, which can be parsed with the `dateutil.parser` module.  
A strong ambiguity remains regarding the `day_first` parameter, for values like '01/02/2020'. 
Britannic and US source would usually have month as first value, while '25/05/2020' for 'Journal of emergency nursing' is clearly day first.
A solution could be to infer the date format from the publication source location. In the hypothesis that we could maintain an up-to-date referential of medical journals, this could be set as a journal property.
In lack of better specification, this is shown as an example.

#### Validate journal
There seems to be some added junk characters on some fields, probably from an ocr read. 
A generic validation method could use a Levensthein distance against some referential... This was noy implemented here, keeping an ad-hoc method for one specific error. 

#### Deduplication
Some publication entries will be considered duplicates when IDs are identical, or when (title, date) are identical.
Moreover, some entries will be incomplete (missing id, or other attributes).
Rules for deduplication:
- group by given columns
- aggregate on a list of value for all other columns
- keep first non-blank value in list
- Never deduplicate on null key

### Build Graph

#### Nodes
Publications, journals and drugs populate a node dictionary with uid as key, label and metadata,  
Examples: 
```
      "S03AA": {
        "label": "TETRACYCLINE",
        "metadata": {
          "type": "drug"
        }
      },
      "clinical_trials_NCT04189588": {
        "label": "Phase 2 Study IV QUZYTTIR™ (Cetirizine Hydrochloride Injection) vs V Diphenhydramine",
        "metadata": {
          "id": "NCT04189588",
          "title": "Phase 2 Study IV QUZYTTIR™ (Cetirizine Hydrochloride Injection) vs V Diphenhydramine",
          "date": "2020-01-01",
          "journal": "Journal of emergency nursing",
          "type": "clinical_trials",
          "uid": "clinical_trials_NCT04189588"
        }
      },
```

Publications are normalized with an added field "type", one of "pubmed" or "clinical_trials".
To ensure unicity, an uid as been added as a composite key on (type, '_', id) 

#### Edges
Two different relations are defined: 
- 'is_referenced' links a drug to a publication
- 'is_mentioned' links a publication to a journal

Example:
```
  {
    "source": "A04AD",
    "target": "clinical_trials_NCT01967433",
    "relation": "is_referenced",
    "metadata": {
        "date": "2020-01-01",
        "type": "clinical_trials"
    }
  },
  {
    "source": "clinical_trials_NCT01967433",
    "target": "Journal of emergency nursing",
    "relation": "is_mentioned",
    "metadata": {
        "date": "2020-01-01",
        "type": "clinical_trials"
    }
  }
```

### Graph Helpers
Helper methods to query a graph document.
The transitive `query` method allows sequentially query several relations on graph edges, filtered by metadata, and aggregates the results either on source or target.
Example :
```
drugs_by_journal_filtered_by_pubmed = graph_helper.query(
    relations=['is_mentioned', 'is_referenced'],
    group_by='target',
    type="pubmed"
    )
```

#### Examples 

Query example on graph file:  
[publications/examples.py](publications/examples.py)

The result is as follows:
```
Publications by drugs for the specific date of 2019-01-01
{
    "DIPHENHYDRAMINE": [
        "An evaluation of benadryl, pyribenzamine, and other so-called diphenhydramine antihistaminic drugs in the treatment of allergy.",
        "A 44-year-old man with erythema of the face diphenhydramine, neck, and chest, weakness, and palpitations"
    ]
}


Journals by publications for the specific date of 2019-01-01
{
    "A 44-year-old man with erythema of the face diphenhydramine, neck, and chest, weakness, and palpitations": [
        "Journal of emergency nursing"
    ],
    "An evaluation of benadryl, pyribenzamine, and other so-called diphenhydramine antihistaminic drugs in the treatment of allergy.": [
        "Journal of emergency nursing"
    ]
}


Publications by journals for the specific date of 2019-01-01
{
    "Journal of emergency nursing": [
        "An evaluation of benadryl, pyribenzamine, and other so-called diphenhydramine antihistaminic drugs in the treatment of allergy.",
        "A 44-year-old man with erythema of the face diphenhydramine, neck, and chest, weakness, and palpitations"
    ]
}


All journal references by drugs (transitive query)
{
    "BETAMETHASONE": [
        "Hôpitaux Universitaires de Genève",
        "The journal of maternal-fetal & neonatal medicine",
        "Journal of back and musculoskeletal rehabilitation"
    ],
    "DIPHENHYDRAMINE": [
        "Journal of emergency nursing",
        "The Journal of pediatrics"
    ],
    "EPINEPHRINE": [
        "Journal of emergency nursing",
        "The journal of allergy and clinical immunology. In practice"
    ],
    "ETHANOL": [
        "Psychopharmacology"
    ],
    "ISOPRENALINE": [
        "Journal of photochemistry and photobiology. B, Biology"
    ],
    "TETRACYCLINE": [
        "Journal of food protection",
        "Psychopharmacology",
        "American journal of veterinary research"
    ]
}


All drugs by journal reference (transitive query)
{
    "American journal of veterinary research": [
        "TETRACYCLINE"
    ],
    "Hôpitaux Universitaires de Genève": [
        "BETAMETHASONE"
    ],
    "Journal of back and musculoskeletal rehabilitation": [
        "BETAMETHASONE"
    ],
    "Journal of emergency nursing": [
        "DIPHENHYDRAMINE",
        "EPINEPHRINE"
    ],
    "Journal of food protection": [
        "TETRACYCLINE"
    ],
    "Journal of photochemistry and photobiology. B, Biology": [
        "ISOPRENALINE"
    ],
    "Psychopharmacology": [
        "ETHANOL",
        "TETRACYCLINE"
    ],
    "The Journal of pediatrics": [
        "DIPHENHYDRAMINE"
    ],
    "The journal of allergy and clinical immunology. In practice": [
        "EPINEPHRINE"
    ],
    "The journal of maternal-fetal & neonatal medicine": [
        "BETAMETHASONE"
    ]
}


Drugs by journal filtered by pubmed
{
    "American journal of veterinary research": [
        "TETRACYCLINE"
    ],
    "Journal of back and musculoskeletal rehabilitation": [
        "BETAMETHASONE"
    ],
    "Journal of emergency nursing": [
        "DIPHENHYDRAMINE"
    ],
    "Journal of food protection": [
        "TETRACYCLINE"
    ],
    "Journal of photochemistry and photobiology. B, Biology": [
        "ISOPRENALINE"
    ],
    "Psychopharmacology": [
        "ETHANOL",
        "TETRACYCLINE"
    ],
    "The Journal of pediatrics": [
        "DIPHENHYDRAMINE"
    ],
    "The journal of allergy and clinical immunology. In practice": [
        "EPINEPHRINE"
    ],
    "The journal of maternal-fetal & neonatal medicine": [
        "BETAMETHASONE"
    ]
}


Journal with most mentions
[
    "Psychopharmacology",
    [
        "ETHANOL",
        "TETRACYCLINE"
    ]
]


Drugs referenced by same journals from pubmed - example for TETRACYCLINE
{'ETHANOL'}


Drugs referenced by same journals from pubmed - example for ETHANOL
{'TETRACYCLINE'}

```

## Scalability

The best way to store and process larger volumes of data would be through the use of a graph processing framework such as [Spark GraphX](https://spark.apache.org/graphx/) and the Python API for the Dataframe library [GraphFrames](https://graphframes.github.io/graphframes/docs/_site/index.html).

In that eventuality the main processing steps would remain, some validation functionality could be reused as udf.

All graph functions `build_nodes`, `build_edges`, `build_graph` should be reimplemented, leveraging Spark Dataframe SQL functionalities.



# SQL

## 1. Sales by date

The exercise may be tricky because the date format is atypical, so it seems to be a STRING field.
It that is the case, it won't work well on date comparison and sorting.
A solution may be to parse and convert the field, but parsing functions may differ from databases. 

This is an example for Postgresql: 

```sql
  SELECT date, sum(prod_price * prod_qty)
  FROM TRANSACTION
  WHERE TO_DATE(date, 'dd/MM/yy') >= "2019-01-01" AND TO_DATE(date, 'dd/MM/yy') < "2020-01-01"
  GROUP BY date
  ORDER BY TO_DATE(date, 'dd/MM/yy')
```

## 2. Sales by client and product type

```sql
WITH sales_by_product_type AS (
    SELECT
        client_id,
        IF(product_type = 'MEUBLE', prod_price * prod_qty, 0) AS ventes_meuble,
        IF(product_type = 'DECO',  prod_price * prod_qty, 0) AS ventes_deco
    FROM TRANSACTION t
    JOIN PRODUCT_NOMENCLATURE pn
        ON pn.product_id = t.product_id
    WHERE TO_DATE(date, 'dd/MM/yy') >= "2019-01-01" AND TO_DATE(date, 'dd/MM/yy') < "2020-01-01"
)

SELECT client_id, SUM(ventes_meuble) AS ventes_meuble, SUM(ventes_deco) AS ventes_deco
FROM sales_by_product_type
GROUP BY client_id
```
