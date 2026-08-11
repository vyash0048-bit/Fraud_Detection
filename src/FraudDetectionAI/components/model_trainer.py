import os
import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from FraudDetectionAI.logger import logging
from FraudDetectionAI.entity.config_entity import ModelTrainerConfig

class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def initiate_model_training(self):
        logging.info("Loading preprocessed training data")
        train = pd.read_csv(self.config.train_data_path)
        
        target = 'isFraud'
        
        # Drop ID and target from features
        X_train = train.drop([target, 'TransactionID'], axis=1, errors='ignore')
        y_train = train[target]
        
        # Fill any remaining NaNs safely
        X_train = X_train.fillna(0)
        
        logging.info("--- Strict Temporal Validation Training ---")
        lr = LogisticRegression(
            penalty=self.config.penalty, C=self.config.C, class_weight=self.config.class_weight,
            max_iter=self.config.max_iter, solver=self.config.solver, n_jobs=-1
        )
        
        logging.info(f"Training Logistic Regression baseline model on temporal train split...")
        lr.fit(X_train, y_train)
        
        # Save model
        model_path = os.path.join(self.config.root_dir, self.config.model_name)
        joblib.dump(lr, model_path)
        logging.info(f"Model saved to {model_path}")
