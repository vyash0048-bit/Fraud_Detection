import os
import pandas as pd
import numpy as np
import joblib
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score, recall_score, f1_score, confusion_matrix
from FraudDetectionAI.logger import logging
from FraudDetectionAI.entity.config_entity import ModelEvaluationConfig

class ModelEvaluation:
    def __init__(self, config: ModelEvaluationConfig):
        self.config = config

    def evaluate_model(self, y_true, y_prob):
        # ROC-AUC, GINI, PR-AUC
        roc_auc = roc_auc_score(y_true, y_prob)
        gini = 2 * roc_auc - 1
        pr_auc = average_precision_score(y_true, y_prob)
        
        # Threshold selection (maximize F1)
        thresholds = np.linspace(0.01, 0.99, 50)
        best_f1 = 0
        best_thresh = 0.5
        for t in thresholds:
            y_pred = (y_prob >= t).astype(int)
            f1 = f1_score(y_true, y_pred, zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_thresh = t
                
        y_pred_best = (y_prob >= best_thresh).astype(int)
        precision = precision_score(y_true, y_pred_best, zero_division=0)
        recall = recall_score(y_true, y_pred_best, zero_division=0)
        cm = confusion_matrix(y_true, y_pred_best).tolist()
        
        return {
            'roc_auc': roc_auc,
            'gini': gini,
            'pr_auc': pr_auc,
            'best_threshold': best_thresh,
            'precision': precision,
            'recall': recall,
            'f1_score': best_f1,
            'confusion_matrix': cm
        }

    def initiate_model_evaluation(self):
        logging.info("Loading preprocessed validation data and model")
        test = pd.read_csv(self.config.test_data_path)
        model = joblib.load(self.config.model_path)
        
        target = 'isFraud'
        
        # Drop ID and target from features
        X_test = test.drop([target, 'TransactionID'], axis=1, errors='ignore')
        y_test = test[target]
        
        # Fill any remaining NaNs safely
        X_test = X_test.fillna(0)
        
        logging.info("Predicting on validation/test split...")
        y_prob = model.predict_proba(X_test)[:, 1]
        
        metrics = self.evaluate_model(y_test, y_prob)
        
        logging.info(f"Temporal Validation Results:")
        logging.info(f"ROC-AUC: {metrics['roc_auc']:.4f}")
        logging.info(f"GINI: {metrics['gini']:.4f}")
        logging.info(f"PR-AUC: {metrics['pr_auc']:.4f}")
        logging.info(f"Optimal Threshold for F1: {metrics['best_threshold']:.4f}")
        logging.info(f"Precision: {metrics['precision']:.4f}, Recall: {metrics['recall']:.4f}, F1: {metrics['f1_score']:.4f}")
        logging.info(f"Confusion Matrix: {metrics['confusion_matrix']}")
        
        # Save metrics
        with open(self.config.metric_file_name, "w") as f:
            json.dump(metrics, f, indent=4)
        logging.info(f"Metrics saved to {self.config.metric_file_name}")
        
        return metrics
