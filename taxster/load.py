import pandas as pd

from itertools import chain


def load_taxonomy(taxonomy):
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


def load_seqs(seqs, table):
    """Load sequences into a table

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
