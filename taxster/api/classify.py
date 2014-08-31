from collections import defaultdict

import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder

from taxster import logging
from ..load import load_taxonomy, load_seqs


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
    tax_table = load_taxonomy(taxonomy)
    logging.info('Loaded %d taxonomic descriptions' % len(tax_table))

    logging.info('Loading training sequences')
    load_seqs(training_seqs, tax_table)

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
