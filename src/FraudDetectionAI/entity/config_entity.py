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
    preprocessed_val_path: Path
    preprocessed_test_path: Path

@dataclass(frozen=True)
class ModelTrainerConfig:
    root_dir: Path
    train_data_path: Path
    val_data_path: Path
    model_name: str
    penalty: str
    C: float
    class_weight: str
    max_iter: int
    solver: str

@dataclass(frozen=True)
class ModelEvaluationConfig:
    root_dir: Path
    test_data_path: Path
    model_path: Path
    metric_file_name: Path
