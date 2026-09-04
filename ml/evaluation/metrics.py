import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    log_loss,
    confusion_matrix,
    accuracy_score
)


class ModelEvaluator:
    """
    Standardized ML Model Evaluator for RecoverAI.
    Calculates Precision, Recall, F1, ROC-AUC, PR-AUC, Brier score loss, Log loss,
    and Majority-Class Baseline accuracy.
    """

    @staticmethod
    def evaluate(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> Dict[str, Any]:
        """
        Evaluate predicted probabilities against ground truth labels.
        """
        y_pred = (y_prob >= threshold).astype(int)

        precision = float(precision_score(y_true, y_pred, zero_division=0))
        recall = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        roc_auc = float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else 0.5
        pr_auc = float(average_precision_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else 0.5
        brier = float(brier_score_loss(y_true, y_prob))
        logloss = float(log_loss(y_true, y_prob))
        accuracy = float(accuracy_score(y_true, y_pred))

        # Majority-class baseline accuracy
        majority_class = int(np.round(np.mean(y_true)))
        majority_pred = np.full_like(y_true, majority_class)
        majority_baseline_accuracy = float(accuracy_score(y_true, majority_pred))

        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

        return {
            "accuracy": accuracy,
            "majority_baseline_accuracy": majority_baseline_accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "roc_auc": roc_auc,
            "pr_auc": pr_auc,
            "brier_score": brier,
            "log_loss": logloss,
            "confusion_matrix": {
                "tn": int(tn),
                "fp": int(fp),
                "fn": int(fn),
                "tp": int(tp),
            },
            "positive_count": int(np.sum(y_true)),
            "total_count": int(len(y_true)),
        }
