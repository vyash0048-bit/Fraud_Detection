import os
import pandas as pd
import numpy as np
import joblib
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (roc_auc_score, average_precision_score, 
                             precision_score, recall_score, f1_score, 
                             confusion_matrix, roc_curve, precision_recall_curve)
from FraudDetectionAI.logger import logging
from FraudDetectionAI.entity.config_entity import ModelEvaluationConfig

class ModelEvaluation:
    def __init__(self, config: ModelEvaluationConfig):
        self.config = config
        self.plots_dir = os.path.join(self.config.root_dir, "plots")
        os.makedirs(self.plots_dir, exist_ok=True)

    def calculate_at_k(self, y_true, y_prob, k_percent=0.05):
        # Calculate precision and recall at top K% of transactions
        k = int(len(y_true) * k_percent)
        idx = np.argsort(y_prob)[::-1]
        y_true_sorted = y_true.iloc[idx].values
        
        tp = np.sum(y_true_sorted[:k])
        precision_at_k = tp / k
        recall_at_k = tp / np.sum(y_true)
        return precision_at_k, recall_at_k
        
    def plot_roc_pr(self, y_true, y_prob):
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))
        
        # ROC Curve
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        auc = roc_auc_score(y_true, y_prob)
        ax[0].plot(fpr, tpr, label=f'AUC = {auc:.4f}')
        ax[0].plot([0, 1], [0, 1], 'k--')
        ax[0].set_title('ROC Curve')
        ax[0].set_xlabel('False Positive Rate')
        ax[0].set_ylabel('True Positive Rate')
        ax[0].legend()
        
        # PR Curve
        precisions, recalls, _ = precision_recall_curve(y_true, y_prob)
        pr_auc = average_precision_score(y_true, y_prob)
        ax[1].plot(recalls, precisions, label=f'PR-AUC = {pr_auc:.4f}')
        ax[1].set_title('Precision-Recall Curve')
        ax[1].set_xlabel('Recall')
        ax[1].set_ylabel('Precision')
        ax[1].legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "roc_pr_curves.png"))
        plt.close()

    def plot_threshold_dynamics(self, df_thresh):
        fig, ax = plt.subplots(1, 2, figsize=(14, 5))
        
        # Threshold vs Precision/Recall/F1
        ax[0].plot(df_thresh['threshold'], df_thresh['precision'], label='Precision')
        ax[0].plot(df_thresh['threshold'], df_thresh['recall'], label='Recall')
        ax[0].plot(df_thresh['threshold'], df_thresh['f1'], label='F1 Score')
        ax[0].set_title('Threshold vs Metrics')
        ax[0].set_xlabel('Probability Threshold')
        ax[0].set_ylabel('Score')
        ax[0].legend()
        
        # Investigation Volume vs Fraud Capture
        ax[1].plot(df_thresh['investigation_volume'], df_thresh['fraud_capture_rate'])
        ax[1].set_title('Investigation Volume vs Fraud Capture')
        ax[1].set_xlabel('Total Transactions Flagged (Volume)')
        ax[1].set_ylabel('Fraud Captured (Recall)')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "threshold_dynamics.png"))
        plt.close()

    def plot_confusion_matrix(self, cm, threshold):
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
        plt.title(f'Confusion Matrix (Threshold = {threshold:.2f})')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, "confusion_matrix.png"))
        plt.close()

    def initiate_model_evaluation(self):
        logging.info("Loading preprocessed test/val data and model")
        test = pd.read_csv(self.config.test_data_path)
        model = joblib.load(self.config.model_path)
        
        target = 'isFraud'
        
        X_test = test.drop([target, 'TransactionID'], axis=1, errors='ignore')
        y_test = test[target]
        
        logging.info("Predicting probabilities...")
        y_prob = model.predict_proba(X_test)[:, 1]
        
        # 1. Base Metrics
        roc_auc = roc_auc_score(y_test, y_prob)
        gini = 2 * roc_auc - 1
        pr_auc = average_precision_score(y_test, y_prob)
        
        # 2. Precision/Recall @ 5%
        p_at_5, r_at_5 = self.calculate_at_k(y_test, y_prob, 0.05)
        
        # 3. Threshold Optimization Framework
        logging.info("Building Threshold Optimization Framework...")
        thresholds = np.linspace(0.01, 0.99, 99)
        thresh_data = []
        
        total_fraud = np.sum(y_test)
        
        for t in thresholds:
            y_pred = (y_prob >= t).astype(int)
            tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0,1]).ravel()
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            investigation_volume = tp + fp
            fraud_capture_rate = tp / total_fraud if total_fraud > 0 else 0
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
            
            thresh_data.append({
                'threshold': t,
                'tp': int(tp), 'fp': int(fp), 'tn': int(tn), 'fn': int(fn),
                'precision': float(precision), 'recall': float(recall), 'f1': float(f1),
                'fraud_capture_rate': float(fraud_capture_rate),
                'fpr': float(fpr),
                'investigation_volume': int(investigation_volume)
            })
            
        df_thresh = pd.DataFrame(thresh_data)
        
        # Best F1 Threshold
        best_f1_row = df_thresh.loc[df_thresh['f1'].idxmax()]
        best_thresh = best_f1_row['threshold']
        
        logging.info("Generating evaluation plots...")
        self.plot_roc_pr(y_test, y_prob)
        self.plot_threshold_dynamics(df_thresh)
        
        best_cm = [[int(best_f1_row['tn']), int(best_f1_row['fp'])], 
                   [int(best_f1_row['fn']), int(best_f1_row['tp'])]]
        self.plot_confusion_matrix(best_cm, best_thresh)
        
        metrics = {
            'roc_auc': float(roc_auc),
            'gini': float(gini),
            'pr_auc': float(pr_auc),
            'precision_at_5pct': float(p_at_5),
            'recall_at_5pct': float(r_at_5),
            'best_f1_threshold': float(best_thresh),
            'best_f1_score': float(best_f1_row['f1']),
            'precision_at_best': float(best_f1_row['precision']),
            'recall_at_best': float(best_f1_row['recall']),
            'confusion_matrix': best_cm
        }
        
        # Save metrics
        with open(self.config.metric_file_name, "w") as f:
            json.dump(metrics, f, indent=4)
        logging.info(f"Detailed metrics saved to {self.config.metric_file_name}")
        
        # Save threshold data for analysts
        df_thresh.to_csv(os.path.join(self.config.root_dir, "threshold_optimization.csv"), index=False)
        logging.info("Threshold optimization framework data saved to CSV")
        
        return metrics
