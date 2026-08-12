import os
import pandas as pd
import numpy as np
import joblib
from lightgbm import LGBMClassifier
from sklearn.model_selection import RandomizedSearchCV
from FraudDetectionAI.logger import logging
from FraudDetectionAI.entity.config_entity import ModelTrainerConfig

class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig):
        self.config = config

    def initiate_model_training(self):
        logging.info("Loading preprocessed training data")
        train = pd.read_csv(self.config.train_data_path)
        val = pd.read_csv(self.config.val_data_path)
        
        target = 'isFraud'
        
        # Drop ID and target from features
        X_train = train.drop([target, 'TransactionID'], axis=1, errors='ignore')
        y_train = train[target]
        X_val = val.drop([target, 'TransactionID'], axis=1, errors='ignore')
        y_val = val[target]
        
        # Calculate scale_pos_weight
        num_neg = (y_train == 0).sum()
        num_pos = (y_train == 1).sum()
        scale_pos_weight = num_neg / num_pos
        logging.info(f"Calculated scale_pos_weight: {scale_pos_weight:.2f}")

        # Feature Selection Phase
        if getattr(self.config, 'feature_selection_enabled', False):
            top_n = getattr(self.config, 'top_n_features', 50)
            logging.info(f"Feature Selection Enabled: Training baseline to extract top {top_n} features.")
            import json
            baseline = LGBMClassifier(n_estimators=100, scale_pos_weight=scale_pos_weight, random_state=42, n_jobs=-1, verbosity=-1)
            baseline.fit(X_train, y_train)
            
            feat_imp = pd.DataFrame({'feature': baseline.feature_name_, 'importance': baseline.feature_importances_})
            feat_imp = feat_imp.sort_values(by='importance', ascending=False)
            top_features = feat_imp.head(top_n)['feature'].tolist()
            
            X_train = X_train[top_features]
            X_val = X_val[top_features]
            logging.info(f"Selected {len(top_features)} features.")
            
            with open(os.path.join(self.config.root_dir, "selected_features.json"), "w") as f:
                json.dump(top_features, f, indent=4)

        # LightGBM parameter grid
        param_grid = {
            'n_estimators': self.config.n_estimators,
            'learning_rate': self.config.learning_rate,
            'num_leaves': self.config.num_leaves,
            'max_depth': self.config.max_depth,
            'min_child_samples': self.config.min_child_samples,
            'subsample': self.config.subsample,
            'colsample_bytree': self.config.colsample_bytree
        }
        
        # Initialize base model
        lgbm = LGBMClassifier(
            scale_pos_weight=scale_pos_weight,
            objective='binary',
            metric='auc',
            n_jobs=-1,
            random_state=42,
            verbosity=-1
        )
        
        logging.info("Starting RandomizedSearchCV for LightGBM")
        random_search = RandomizedSearchCV(
            estimator=lgbm,
            param_distributions=param_grid,
            n_iter=self.config.n_iter_search,
            scoring='average_precision',
            cv=3,
            verbose=2,
            random_state=42,
            n_jobs=1  # LightGBM already uses multithreading
        )
        
        # For hyperparameter tuning, we will use early stopping in the fit
        # We need a small sample if the dataset is too big, but we'll run on full data since n_iter is small
        # To pass early_stopping to fit, we define fit_params (using LightGBM early stopping callback in modern versions)
        from lightgbm import early_stopping
        fit_params = {
            "eval_X": (X_val,),
            "eval_y": (y_val,),
            "eval_metric": "auc",
            "callbacks": [early_stopping(stopping_rounds=50, verbose=False)]
        }
        
        random_search.fit(X_train, y_train, **fit_params)
        
        logging.info(f"Best parameters found: {random_search.best_params_}")
        logging.info(f"Best cross-validation ROC-AUC: {random_search.best_score_:.4f}")
        
        # The best estimator is already refitted on the entire training set
        best_model = random_search.best_estimator_
        
        # Save model
        model_path = os.path.join(self.config.root_dir, self.config.model_name)
        joblib.dump(best_model, model_path)
        logging.info(f"LightGBM Model saved to {model_path}")
        
        logging.info("Calibrating model probabilities using Isotonic Regression...")
        from sklearn.calibration import CalibratedClassifierCV
        from sklearn.frozen import FrozenEstimator
        calibrated_model = CalibratedClassifierCV(estimator=FrozenEstimator(best_model), method='isotonic')
        calibrated_model.fit(X_val, y_val)
        
        calibrated_model_path = os.path.join(self.config.root_dir, self.config.calibrated_model_name)
        joblib.dump(calibrated_model, calibrated_model_path)
        logging.info(f"Calibrated LightGBM Model saved to {calibrated_model_path}")
