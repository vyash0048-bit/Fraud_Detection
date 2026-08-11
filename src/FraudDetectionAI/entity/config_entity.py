from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DataIngestionConfig:
    root_dir: Path
    local_data_dir: Path

@dataclass(frozen=True)
class DataPreprocessingConfig:
    root_dir: Path
    train_data_path: Path
    train_identity_path: Path
    test_data_path: Path
    test_identity_path: Path
    preprocessed_train_path: Path
    preprocessed_test_path: Path
