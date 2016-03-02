# ----------------------------------------------------------------------------
# Copyright (c) 2016--, taxster development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from unittest import TestCase, main
from taxster._uc import _compute_consensus_annotation


class ConsensusAnnotationTests(TestCase):

    def test_compute_consensus_annotation(self):
        """_get_consensus_assignment fuctions as expected """
        in1 = [['Ab', 'Bc', 'De'],
               ['Ab', 'Bc', 'Fg', 'Hi'],
               ['Ab', 'Bc', 'Fg', 'Jk']]

        actual = _compute_consensus_annotation(in1, 0.51)
        expected = (['Ab', 'Bc', 'Fg'], 2. / 3.)
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    main()
