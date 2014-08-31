from itertools import chain

import pandas as pd
from sklearn.preprocessing import LabelEncoder

from taxster import logging


def load_training_set(taxonomy, training_seqs, rank):
    """Load a taxonomy and training sequences

    Parameters
    ----------
    taxonomy : TreeNode
        The taxonomy
    seqs : skbio.parse.sequences.SequenceIterator
        The sequences to load.
    rank : int
        The level in the taxonomy to encode

    Returns
    -------
    DataFrame
        The taxonomy represented as a DataFrame where the IDs are the index,
        and containing the sequence data.
    """
    logging.info('Loading taxonomy')
    tax_table = _load_taxonomy(taxonomy)
    logging.info('Loaded %d taxonomic descriptions' % len(tax_table))

    logging.info('Loading training sequences')
    tax_table = _load_seqs(training_seqs, tax_table)

    label_encoder = LabelEncoder()
    logging.info('Transforming labels using %s' % label_encoder)
    tax_table.label = label_encoder.fit_transform(tax_table[rank])

    n_labels = len(set(tax_table[rank]))
    logging.info('Training set has %s different labels' % n_labels)

    return tax_table


def _load_taxonomy(taxonomy):
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
    """Load sequences into a table

    Parameters
    ----------
    seqs : skbio.parse.sequences.SequenceIterator
        The sequences to load.
    table : DataFrame
        The labels table.

    Returns
    -------
    DataFrame
        The modified table
    """
    ids_to_keep = {str(i) for i in table.index}
    seq_dict = {rec['SequenceID']: rec['Sequence'] for rec in seqs
                if rec['SequenceID'] in ids_to_keep}
    table = table.ix[seq_dict]
    table.sequence = [seq_dict[i] for i in table.index]

    return table
