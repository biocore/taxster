# ----------------------------------------------------------------------------
# Copyright (c) 2016--, taxster development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import io
from unittest import TestCase, main

from taxster._uc import (_compute_consensus_annotation,
                         _compute_consensus_annotations,
                         _uc_to_taxonomy)
from taxster import uc_consensus_assignments


class ConsensusAnnotationTests(TestCase):

    # This code has been ported to taxster from QIIME 1.9.1 with
    # permission from @gregcaporaso.

    def test_varied_min_fraction(self):
        in_ = [['Ab', 'Bc', 'De'],
               ['Ab', 'Bc', 'Fg', 'Hi'],
               ['Ab', 'Bc', 'Fg', 'Jk']]

        actual = _compute_consensus_annotation(in_, 0.51, "Unassigned")
        expected = (['Ab', 'Bc', 'Fg'], 2. / 3.)
        self.assertEqual(actual, expected)

        # increased min_consensus_fraction yields decreased specificity
        in_ = [['Ab', 'Bc', 'De'],
               ['Ab', 'Bc', 'Fg', 'Hi'],
               ['Ab', 'Bc', 'Fg', 'Jk']]

        actual = _compute_consensus_annotation(in_, 0.99, "Unassigned")
        expected = (['Ab', 'Bc'], 1.0)
        self.assertEqual(actual, expected)

    def test_single_annotation(self):
        in_ = [['Ab', 'Bc', 'De']]

        actual = _compute_consensus_annotation(in_, 1.0, "Unassigned")
        expected = (['Ab', 'Bc', 'De'], 1.0)
        self.assertEqual(actual, expected)

        actual = _compute_consensus_annotation(in_, 0.501, "Unassigned")
        expected = (['Ab', 'Bc', 'De'], 1.0)
        self.assertEqual(actual, expected)

    def test_no_consensus(self):
        in_ = [['Ab', 'Bc', 'De'],
               ['Cd', 'Bc', 'Fg', 'Hi'],
               ['Ef', 'Bc', 'Fg', 'Jk']]

        actual = _compute_consensus_annotation(in_, 0.51, "Unassigned")
        expected = (['Unassigned'], 1.)
        self.assertEqual(actual, expected)

        actual = _compute_consensus_annotation(
                    in_, 0.51, unassignable_label="Hello world!")
        expected = (['Hello world!'], 1.)
        self.assertEqual(actual, expected)

    def test_invalid_min_consensus_fraction(self):
        in_ = [['Ab', 'Bc', 'De'],
               ['Ab', 'Bc', 'Fg', 'Hi'],
               ['Ab', 'Bc', 'Fg', 'Jk']]
        self.assertRaises(ValueError, _compute_consensus_annotation, in_,
                          0.50, "Unassigned")
        self.assertRaises(ValueError, _compute_consensus_annotation, in_,
                          0.00, "Unassigned")
        self.assertRaises(ValueError, _compute_consensus_annotation, in_,
                          -0.1, "Unassigned")

    def test_overlapping_names(self):
        # here the 3rd level is different, but the 4th level is the same
        # across the three assignments. this can happen in practice if
        # three different genera are assigned, and under each there is
        # an unnamed species
        # (e.g., f__x;g__A;s__, f__x;g__B;s__, f__x;g__B;s__)
        # in this case, the assignment should be f__x.
        in_ = [['Ab', 'Bc', 'De', 'Jk'],
               ['Ab', 'Bc', 'Fg', 'Jk'],
               ['Ab', 'Bc', 'Hi', 'Jk']]
        actual = _compute_consensus_annotation(in_, 0.51, "Unassigned")
        expected = (['Ab', 'Bc'], 1.)
        self.assertEqual(actual, expected)

        # here the third level is the same in 4/5 of the
        # assignments, but one of them (z, y, c) refers to a
        # different taxa since the higher levels are different.
        # the consensus value should be 3/5, not 4/5, to
        # reflect that.
        in_ = [['a', 'b', 'c'],
               ['a', 'd', 'e'],
               ['a', 'b', 'c'],
               ['a', 'b', 'c'],
               ['z', 'y', 'c']]
        actual = _compute_consensus_annotation(in_, 0.51, "Unassigned")
        expected = (['a', 'b', 'c'], 0.6)
        self.assertEqual(actual, expected)

    def test_adjusts_resolution(self):
        # max result depth is that of shallowest assignment
        in_ = [['Ab', 'Bc', 'Fg'],
               ['Ab', 'Bc', 'Fg', 'Hi'],
               ['Ab', 'Bc', 'Fg', 'Hi'],
               ['Ab', 'Bc', 'Fg', 'Hi'],
               ['Ab', 'Bc', 'Fg', 'Hi', 'Jk']]

        actual = _compute_consensus_annotation(in_, 0.51, "Unassigned")
        expected = (['Ab', 'Bc', 'Fg'], 1.0)
        self.assertEqual(actual, expected)

        in_ = [['Ab', 'Bc', 'Fg'],
               ['Ab', 'Bc', 'Fg', 'Hi', 'Jk'],
               ['Ab', 'Bc', 'Fg', 'Hi', 'Jk'],
               ['Ab', 'Bc', 'Fg', 'Hi', 'Jk'],
               ['Ab', 'Bc', 'Fg', 'Hi', 'Jk']]

        actual = _compute_consensus_annotation(in_, 0.51, "Unassigned")
        expected = (['Ab', 'Bc', 'Fg'], 1.0)
        self.assertEqual(actual, expected)


class ConsensusAnnotationsTests(TestCase):

    # This code has been ported to taxster from QIIME 1.9.1 with
    # permission from @gregcaporaso.

    def test_varied_fraction(self):

        in_ = {'q1': [['A', 'B', 'C', 'D'],
                      ['A', 'B', 'C', 'E']],
               'q2': [['A', 'H', 'I', 'J'],
                      ['A', 'H', 'K', 'L', 'M'],
                      ['A', 'H', 'I', 'J']],
               'q3': [[]],
               'q4': [[]],
               'q5': [[]]}
        expected = {'q1': (['A', 'B', 'C'], 1.0, 2),
                    'q2': (['A', 'H', 'I', 'J'], 2. / 3., 3),
                    'q3': (['Unassigned'], 1.0, 1),
                    'q4': (['Unassigned'], 1.0, 1),
                    'q5': (['Unassigned'], 1.0, 1)}
        actual = _compute_consensus_annotations(in_, 0.51, "Unassigned")
        self.assertEqual(actual, expected)

        expected = {'q1': (['A', 'B', 'C'], 1.0, 2),
                    'q2': (['A', 'H'], 1.0, 3),
                    'q3': (['Unassigned'], 1.0, 1),
                    'q4': (['Unassigned'], 1.0, 1),
                    'q5': (['Unassigned'], 1.0, 1)}
        actual = _compute_consensus_annotations(in_, 0.99, "Unassigned")
        self.assertEqual(actual, expected)

    def test_varied_label(self):
        in_ = {'q1': [['A', 'B', 'C', 'D'],
                      ['A', 'B', 'C', 'E']],
               'q2': [['A', 'H', 'I', 'J'],
                      ['A', 'H', 'K', 'L', 'M'],
                      ['A', 'H', 'I', 'J']],
               'q3': [[]],
               'q4': [[]],
               'q5': [[]]}
        expected = {'q1': (['A', 'B', 'C'], 1.0, 2),
                    'q2': (['A', 'H', 'I', 'J'], 2. / 3., 3),
                    'q3': (['x'], 1.0, 1),
                    'q4': (['x'], 1.0, 1),
                    'q5': (['x'], 1.0, 1)}
        actual = _compute_consensus_annotations(in_, 0.51, "x")
        self.assertEqual(actual, expected)


class UcToAssignments(TestCase):

    # This code has been ported to taxster from QIIME 1.9.1 with
    # permission from @gregcaporaso.

    def test_uc_to_taxonomy(self):
        expected = {'q1': [['A', 'B', 'C', 'D'],
                           ['A', 'B', 'C', 'E']],
                    'q2': [['A', 'H', 'I', 'J'],
                           ['A', 'H', 'K', 'L', 'M'],
                           ['A', 'H', 'I', 'J']],
                    'q3': [[]],
                    'q4': [[]],
                    'q5': [[]]}
        id_to_taxonomy = {'r1': ['A', 'F', 'G'],
                          'r2': ['A', 'B', 'C', 'D'],
                          'r3': ['A', 'H', 'I', 'J'],
                          'r4': ['A', 'B', 'C', 'E'],
                          'r5': ['A', 'H', 'K', 'L', 'M'],
                          'r6': ['A', 'H', 'I', 'J']}
        in_ = io.StringIO(uc1)
        actual = _uc_to_taxonomy(in_, id_to_taxonomy)
        self.assertEqual(actual, expected)


class UcConsensusAssignments(TestCase):

    # This code has been ported to taxster from QIIME 1.9.1 with
    # permission from @gregcaporaso.

    def test_uc_consensus_assignments(self):
        expected = {'q1': (['A', 'B', 'C'], 1.0, 2),
                    'q2': (['A', 'H', 'I', 'J'], 2. / 3., 3),
                    'q3': (['Unassigned'], 1.0, 1),
                    'q4': (['Unassigned'], 1.0, 1),
                    'q5': (['Unassigned'], 1.0, 1)}
        id_to_taxonomy = {'r1': ['A', 'F', 'G'],
                          'r2': ['A', 'B', 'C', 'D'],
                          'r3': ['A', 'H', 'I', 'J'],
                          'r4': ['A', 'B', 'C', 'E'],
                          'r5': ['A', 'H', 'K', 'L', 'M'],
                          'r6': ['A', 'H', 'I', 'J']}
        in_ = io.StringIO(uc1)
        actual = uc_consensus_assignments(in_, id_to_taxonomy)
        self.assertEqual(actual, expected)

    def test_varied_parameters(self):
        expected = {'q1': (['A', 'B', 'C'], 1.0, 2),
                    'q2': (['A', 'H'], 1.0, 3),
                    'q3': (['x'], 1.0, 1),
                    'q4': (['x'], 1.0, 1),
                    'q5': (['x'], 1.0, 1)}
        id_to_taxonomy = {'r1': ['A', 'F', 'G'],
                          'r2': ['A', 'B', 'C', 'D'],
                          'r3': ['A', 'H', 'I', 'J'],
                          'r4': ['A', 'B', 'C', 'E'],
                          'r5': ['A', 'H', 'K', 'L', 'M'],
                          'r6': ['A', 'H', 'I', 'J']}
        in_ = io.StringIO(uc1)
        actual = uc_consensus_assignments(in_, id_to_taxonomy, 1.0, 'x')
        self.assertEqual(actual, expected)


uc1 = u"""# uclust --input /Users/caporaso/Dropbox/code/short-read...
# version=1.2.22
# Tab-separated fields:
# 1=Type, 2=ClusterNr, 3=SeqLength or ClusterSize, 4=PctId, ...
# Record types (field 1): L=LibSeed, S=NewSeed, H=Hit, ...
# For C and D types, PctId is average id with seed.
# QueryStart and SeedStart are zero-based relative to start of sequence.
# If minus strand, SeedStart is relative to reverse-complemented seed.
N	*	195	*	*	*	*	*	q3	*
N	*	191	*	*	*	*	*	q4	*
N	*	192	*	*	*	*	*	q5	*
L	748	1374	*	*	*	*	*	1081058	*
H	r3	193	100.0	+	0	0	534I193M787I	q2	r3
H	r5	193	97.0	+	0	0	534I193M787I	q2	r5
H	r6	193	97.0	+	0	0	534I193M787I	q2	r6
L	92734	1541	*	*	*	*	*	4440404	*
H	r2	189	99.0	+	0	0	531I189M821I	q1	r2
H	r4	189	100.0	+	0	0	531I189M821I	q1	r4
"""


if __name__ == "__main__":
    main()
