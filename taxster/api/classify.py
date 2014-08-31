from ..load import load_training_set
from ..fit import fit_classifier
from ..predict import predict_labels


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
    taxon labels
        The taxon labels that can be predicted
    generator
        A generator that yields sequence IDs and probabilities of
        classification for each label. The probabilities are in index order
        with the taxon labels.

    Examples
    --------

    """
    tax_table = load_training_set(taxonomy, training_seqs, rank)
    pipeline = fit_classifier(tax_table, ngram_range)
    return (tax_table[rank], predict_labels(query_seqs, pipeline))
