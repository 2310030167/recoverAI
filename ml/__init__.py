"""
RecoverAI Machine Learning Package.
Provides dataset preparation, temporal splitting, feature engineering,
recovery prediction models, natural recovery estimation, and evaluation metrics.
"""

from ml.data.dataset import InvoiceDatasetManager
from ml.features.pipeline import MLFeaturePipeline
from ml.models.baseline import LogisticRegressionBaseline
from ml.models.tabular import StrongTabularModel
from ml.models.natural_recovery import NaturalRecoveryEstimator
from ml.models.assisted_recovery import AssistedRecoveryEstimator
from ml.evaluation.metrics import ModelEvaluator
from ml.training.trainer import ModelTrainer

__all__ = [
    "InvoiceDatasetManager",
    "MLFeaturePipeline",
    "LogisticRegressionBaseline",
    "StrongTabularModel",
    "NaturalRecoveryEstimator",
    "AssistedRecoveryEstimator",
    "ModelEvaluator",
    "ModelTrainer",
]
