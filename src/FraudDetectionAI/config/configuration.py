import os
from pathlib import Path
from FraudDetectionAI.constants import *
from FraudDetectionAI.utils.common import read_yaml, create_directories
from FraudDetectionAI.entity.config_entity import (
    DataIngestionConfig,
    DataPreprocessingConfig
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
            preprocessed_test_path=Path(config.preprocessed_test_path),
        )

        return data_preprocessing_config
