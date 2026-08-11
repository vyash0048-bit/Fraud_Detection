import os
from pathlib import Path
from FraudDetectionAI.constants import *
from FraudDetectionAI.utils.common import read_yaml, create_directories
from FraudDetectionAI.entity.config_entity import (
    DataIngestionConfig,
    DataPreprocessingConfig,
    ModelTrainerConfig,
    ModelEvaluationConfig
)

class ConfigurationManager:
    def __init__(
        self,
        config_filepath = CONFIG_FILE_PATH,
        params_filepath = PARAMS_FILE_PATH):

        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)

        create_directories([self.config.artifacts_root])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        create_directories([config.root_dir])

        data_ingestion_config = DataIngestionConfig(
            root_dir=Path(config.root_dir),
            local_data_dir=Path(config.local_data_dir),
        )

        return data_ingestion_config

    def get_data_preprocessing_config(self) -> DataPreprocessingConfig:
        config = self.config.data_preprocessing

        create_directories([config.root_dir])

        data_preprocessing_config = DataPreprocessingConfig(
            root_dir=Path(config.root_dir),
            train_data_path=Path(config.train_data_path),
            train_identity_path=Path(config.train_identity_path),
            test_data_path=Path(config.test_data_path),
            test_identity_path=Path(config.test_identity_path),
            preprocessed_train_path=Path(config.preprocessed_train_path),
            preprocessed_val_path=Path(config.preprocessed_val_path),
            preprocessed_test_path=Path(config.preprocessed_test_path),
        )

        return data_preprocessing_config

    def get_model_trainer_config(self) -> ModelTrainerConfig:
        config = self.config.model_trainer
        params = self.params.LogisticRegression

        create_directories([config.root_dir])

        model_trainer_config = ModelTrainerConfig(
            root_dir=Path(config.root_dir),
            train_data_path=Path(config.train_data_path),
            val_data_path=Path(config.val_data_path),
            model_name=config.model_name,
            penalty=params.penalty,
            C=params.C,
            class_weight=params.class_weight,
            max_iter=params.max_iter,
            solver=params.solver
        )

        return model_trainer_config

    def get_model_evaluation_config(self) -> ModelEvaluationConfig:
        config = self.config.model_evaluation

        create_directories([config.root_dir])

        model_evaluation_config = ModelEvaluationConfig(
            root_dir=Path(config.root_dir),
            test_data_path=Path(config.test_data_path),
            model_path=Path(config.model_path),
            metric_file_name=Path(config.metric_file_name)
        )

        return model_evaluation_config
