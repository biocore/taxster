import click
import numpy as np

from taxster import logging
from .main import main


@main.command()
@click.option('--training-seqs', type=click.Path(exists=True),
              help='training sequences. hint: use greengenes.')
@click.option('--query-seqs', type=click.Path(exists=True),
              help='query sequences in fasta format')
@click.option('--taxonomy', type=click.File('r'),
              help='training taxonomies. hint: use greengenes.')
@click.option('--output', type=click.File('w'),
              help='where to save trained model.')
@click.option('--rank', help='taxonomic rank to train at', type=int, default=6)
@click.option('--ngram-range', nargs=2, type=int, default=(4, 4))
@click.pass_context
def classify(ctx, **kwargs):
    """Assign taxonomy to sequences

    Examples
    --------
    Classify sequences at the species level using Greengenes:

    $ taxster classify --training-seqs=$PWD/70_otus.fasta \
            --taxonomy=$PWD/70_otus_taxonomy.txt --query-seqs=$PWD/query.fna \
            --rank=6 --output=$PWD/result.txt

    """
    from skbio.parse.sequences import load
    from skbio.tree import TreeNode

    from ..api.classify import classify as classify_

    def _parse_taxonomy(lines):
        for line in lines:
            id_, lin = line.split('\t', 1)
            yield (id_, [l.strip() for l in lin.split(';')])

    output = kwargs.pop('output')
    training_seqs = load(kwargs.pop('training_seqs'))
    query_seqs = load(kwargs.pop('query_seqs'))
    taxonomy = TreeNode.from_taxonomy(_parse_taxonomy(kwargs.pop('taxonomy')))

    labels, probs = classify_(training_seqs, query_seqs, taxonomy, **kwargs)

    logging.info('Writing to %s...' % output.name)
    output.write("#SequenceID\tlabel\tprobability\n")
    for seq_id, label_probs in probs:
        idx = np.argmax(label_probs)
        output.write("%s\t%s\t%s\n" % (seq_id, labels[idx],
                                       str(label_probs[idx])))
    logging.info('Done!')
