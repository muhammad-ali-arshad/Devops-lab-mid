import hashlib
import json
import os
import unittest
from pathlib import Path

import pandas as pd

from app import PredictionRequest, health, metrics as api_metrics, predict


class MidtermTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(Path('config.json').read_text())
        cls.raw = Path('dataset/train.csv').read_bytes()
        cls.dataset = pd.read_csv('dataset/train.csv')
        cls.metrics = json.loads(Path('artifacts/metrics.json').read_text())

    def test_training_dataset(self):
        self.assertGreaterEqual(len(self.dataset), 100)
        self.assertTrue(set(self.config['features'] + ['label']).issubset(self.dataset.columns))
        self.assertEqual(set(self.dataset['label'].dropna().unique()), {0, 1})

    def test_metrics_retrain_for_exact_dataset(self):
        digest = hashlib.sha256(self.raw).hexdigest()
        self.assertEqual(self.metrics['student_id'], self.config['student_id'])
        self.assertEqual(self.metrics['training_rows'], len(self.dataset))
        self.assertEqual(self.metrics['dataset_sha256'], digest)
        self.assertEqual(self.metrics['model_version'], digest[:12])
        self.assertGreaterEqual(self.metrics['accuracy'], 0)
        self.assertLessEqual(self.metrics['accuracy'], 1)
        self.assertEqual(self.metrics['git_sha'], os.getenv('BUILD_COMMIT', 'local'))

    def test_health_and_metrics_api(self):
        self.assertEqual(health()['status'], 'ok')
        data = api_metrics()
        self.assertEqual(data['model_version'], self.metrics['model_version'])
        self.assertIn('git_sha', data)

    def test_prediction_api(self):
        features = self.config['features']
        # Use an existing row, preserving any missing values as null.
        record = self.dataset[features].iloc[0].where(pd.notna(self.dataset[features].iloc[0]), None).to_dict()
        response = predict(PredictionRequest(records=[record]))
        self.assertEqual(len(response['predictions']), 1)
        self.assertIn(response['predictions'][0], (0, 1))
        self.assertGreaterEqual(response['probabilities'][0], 0)
        self.assertLessEqual(response['probabilities'][0], 1)


if __name__ == '__main__':
    unittest.main()
