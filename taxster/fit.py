from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.naive_bayes import MultinomialNB

from taxster import logging


def fit_classifier(table, ngram_range, classifier=MultinomialNB,
                   classifier_kwargs=None):
    """Construct and fit a classifier based on the table data

    Parameters
    ----------
    table : DataFrame
        The training table
    ngram_range : ???
    classifier : sklearn classifier, optional
        The scikit-learn classifier, defaults to MultinomialNB
    classifier_kwargs : dict, optional
        kwargs to pass to the classifier, defaults to None

    Returns
    -------
    sklearn.pipeline.Pipeline

    """
    if classifier_kwargs is None:
        classifier_kwargs = {}

    # define transformation and classification pipeline
    hasher = HashingVectorizer(analyzer='char',
                               ngram_range=ngram_range,
                               non_negative=True)

    pipeline = Pipeline([('transformer', hasher),
                         ('classifier', classifier(**classifier_kwargs))])

    # fit the classifier
    logging.info('Fitting classifier')
    pipeline.fit(table.sequence, table.label)

    return pipeline
