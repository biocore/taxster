taxster: assigning taxonomy to organisms you've never even heard of 
===================================================================

This library contains tools for working with taxonomic assignment data. This should be considered pre-alpha software. **Public APIs can and will change!**

Install
-------

pip install https://github.com/biocore/taxster/archive/master.zip

Consensus taxonomy assignments from .uc files
---------------------------------------------

This example illustrates how to apply the consensus taxonomy processing described in [Bokulich et al (in preparation)](https://peerj.com/preprints/934/). It assumes that you have the test data files included in this repository in ``./test-data``.

```python
import taxster

taxonomy_map = {}
for line in open('./test-data/uc/tax-map.tsv', 'U'):
    line = line.strip()
    if line.startswith('#') or not line:
        continue
    fields = line.split('\t')
    id_ = fields[0]
    tax = fields[1].split('; ')
    taxonomy_map[id_] = tax

uc = open('./test-data/uc/1.uc', 'U')
consensus_assignments = taxster.uc_consensus_assignments(uc, taxonomy_map)
```

If you'd then like to write these out to file, you can do the following. This will write the consensus taxonomy assignments to a file that can be used with ``biom add-metadata`` (compatible with biom-format >= 2.1.5, < 2.2.0).

```python
f = open('uc-consensus-tax.tsv', 'w')
for id_, (tax, fraction, hits) in consensus_assignments.items():
    tax = '; '.join(tax)
    f.write('\t'.join(map(str, [id_, tax, fraction, hits])))
    f.write('\n')
f.close()
```

To get help with ``taxster.uc_consensus_assignments``, call:

```python
help(taxster.uc_consensus_assignments)
```
