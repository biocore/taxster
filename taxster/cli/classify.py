import click
from skbio.parse.sequences import load
from skbio.tree import TreeNode

from taxster import logging
from .main import main


@main.command()
@click.option('--training-seqs', type=click.Path(exists=True),
              help='training sequences. hint: use greengenes.')
@click.option('--query-seqs', type=click.Path(exists=True),
              help='query sequences in fasta format')
@click.option('--taxonomy', type=click.File('r'),
              help='training taxonomies. hint: use greengenes.')
@click.option('--output', type=click.Path(exists=False),
              help='where to save trained model.')
@click.option('--rank', help='taxonomic rank to train at', type=int, default=6)
@click.option('--ngram-range', nargs=2, type=int, default=(4, 4))
@click.pass_context
def classify(ctx, training_seqs, query_seqs, taxonomy, output, rank,
             ngram_range):
    """Assign taxonomy to sequences

    Examples
    --------
    Classify sequences at the species level using Greengenes:

    $ taxster classify --training-seqs=$PWD/70_otus.fasta \
            --taxonomy=$PWD/70_otus_taxonomy.txt --query-seqs=$PWD/query.fna \
            --rank=6 --output=$PWD/result.txt

    """
    from ..api.classify import classify as classify_

    def _parse_taxonomy(lines):
        for line in lines:
            id_, lin = line.split('\t', 1)
            yield (id_, [l.strip() for l in lin.split(';')])

    training_seqs = load(training_seqs)
    query_seqs = load(query_seqs)
    taxonomy = TreeNode.from_taxonomy(_parse_taxonomy(taxonomy))

    result = classify_(training_seqs, query_seqs, taxonomy, rank, ngram_range)

    logging.info('Writing to %s...' % output)
    result.to_csv(output)
    logging.info('Done!')
