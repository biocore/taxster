from collections import defaultdict
from itertools import chain

import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder

from taxster import logging


def _taxonomy_to_dataframe(taxonomy):
    """Convert a taxonomy to a DataFrame

    Parameters
    ----------
    taxonomy : TreeNode
        The taxonomy

    Returns
    -------
    DataFrame
        The taxonomy represented as a DataFrame where the IDs are the index.

    Notes
    -----
    The columns are inferred from the first taxon pulled from the tree.
    """
    iter_ = ((node.name, lineage) for node, lineage in taxonomy.to_taxonomy())

    first_id, first_lineage = iter_.next()
    columns = range(len(first_lineage))
    iter_ = chain([(first_id, first_lineage)], iter_)

    tax_table = pd.DataFrame.from_items(iter_, columns=columns, orient='index')
    tax_table = tax_table.dropna()

    return tax_table


def _load_seqs(seqs, table):
    """Load sequences

    Parameters
    ----------
    seqs : skbio.parse.sequences.SequenceIterator
        The sequences to load.
    table : DataFrame
        The labels table.

    Notes
    -----
    This is inplace on table
    """
    ids_to_keep = {str(i) for i in table.index}
    seq_dict = {rec['SequenceID']: rec['Sequence'] for rec in seqs
                if rec['SequenceID'] in ids_to_keep}
    table = table.ix[seq_dict]
    table.sequence = [seq_dict[i] for i in table.index]


def classify(training_seqs, query_seqs, taxonomy, rank, ngram_range):
    """Classify a set of query sequences against a training set

    Parameters
    ----------
    training_seqs : skbio.parse.sequences.SequenceIterator
        The training sequence dataset.
    query_seqs : skbio.parse.sequences.SequenceIterator
        The sequences to classify.
    taxonomy : skbio.tree.TreeNode
        The class labels for the training dataset represented as a taxonomy.
    rank : unsigned int
        The depth from the root of the taxonomy to classify at where 0 is
        domain, and 6 is species.
    ngram_range : ???

    Returns
    -------
    pandas.DataFrame
        The corresponding classifications

    Examples
    --------

    """
    logging.info('Loading taxonomy')
    tax_table = _taxonomy_to_dataframe(taxonomy)
    logging.info('Loaded %d taxonomic descriptions' % len(tax_table))

    logging.info('Loading training sequences')
    _load_seqs(training_seqs, tax_table)
    logging.info('Kept %s training sequences' % len(train_seqs))

    n_labels = len(set(tax_table[rank]))
    logging.info('Training set has %s different labels' % n_labels)

    logging.info('Classifying at %s rank' % rank)

    # transform labels
    label_encoder = LabelEncoder()
    logging.info('Transforming labels using %s' % label_encoder)
    tax_table.label = label_encoder.fit_transform(tax_table[rank])

    # define transformation and classification pipeline
    hasher = HashingVectorizer(analyzer='char',
                               ngram_range=ngram_range,
                               non_negative=True)

    classifier = MultinomialNB()

    pipeline = Pipeline([('transformer', hasher),
                         ('classifier', classifier)])

    # fit the classifier
    logging.info('Fitting classifier')
    pipeline.fit(tax_table.sequence, tax_table.label)

    # iterate over query sequences, predicting probabilites for each
    # store probabilities in a matrix (DataFrame) with database ID
    # as the column and sequence ID as the row

    target_record_proba = defaultdict(dict)

    # this will be prohibitive for large datasets, so it would be useful to
    # filter. Could do this as a generator too
    for rec in query_seqs:
        probs = pipeline.predict_proba([rec['Sequence']])
        for t, p in zip(tax_table[rank], probs[0]):
            target_record_proba[t][rec['SequenceID']] = p

    return pd.DataFrame.from_dict(target_record_proba)
