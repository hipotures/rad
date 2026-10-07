"""Regression cases for the reviewed admission-index chronology error."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))
from live_trajectory import relationship, E, L
import numpy as np


class ChronologyRegression(unittest.TestCase):
    def make(self, publications):
        events = []
        layers = []
        for times in publications:
            rows = np.zeros(len(times), E)
            for i, at in enumerate(times):
                rows[i]['trigger'] = 0
                rows[i]['target'] = 40 + i
                rows[i]['incoming'] = i
                rows[i]['layer'] = i
                rows[i]['bytes'] = 3072000
                rows[i]['published_at'] = at
                rows[i]['publish_ns'] = at * 100 + 20
            events.append(rows)
            service = np.zeros(30, L)
            service['plan_end'] = np.arange(30) * 100 + 90
            layers.append(service)
        return events, layers

    def test_earlier_array_record_can_publish_after_selection(self):
        events, layers = self.make([[14], [12]])
        result = relationship(events, layers, 10, 1)
        self.assertEqual(result['classification'], 'CONFIRMED_PUBLICATION_DOES_NOT_PRECEDE_DIVERGENCE')

    def test_inspect_all_matching_generations(self):
        events, layers = self.make([[14, 10], [12, 12]])
        result = relationship(events, layers, 10, 2)
        self.assertEqual(result['classification'], 'CONFIRMED_PUBLICATION_PRECEDES_DIVERGENCE')
        self.assertEqual([x['generation'] for x in result['prior_differences']], [1])

    def test_contradictory_same_event_time_is_unknown(self):
        events, layers = self.make([[10], [12]])
        events[0][0]['publish_ns'] = 1100
        result = relationship(events, layers, 10, 1)
        self.assertEqual(result['classification'], 'UNRESOLVED_WITH_RETAINED_EVIDENCE')

    def test_absent_divergence_is_unknown(self):
        events, layers = self.make([[10], [12]])
        self.assertEqual(relationship(events, layers, None, 1)['classification'],
                         'UNRESOLVED_WITH_RETAINED_EVIDENCE')


if __name__ == '__main__':
    unittest.main()
