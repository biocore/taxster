def predict_labels(query_seqs, pipeline):
    """Predict class labels for each query sequence

    Parameters
    ----------
    query_seqs : skbio.parse.sequences.SequenceIterator
        The query sequences.
    pipeline : sklearn.pipeline.Pipeline
        The classifier.

    Returns
    -------
    generator
        Yields sequence ID and probabilities for each taxon
    """
    for rec in query_seqs:
        seq_id = rec['SequenceID']
        seq = rec['Sequence']

        probs = pipeline.predict_proba([seq])

        yield (seq_id, probs[0])
