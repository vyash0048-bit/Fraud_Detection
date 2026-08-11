from FraudDetectionAI.logger import logging
from FraudDetectionAI.pipeline.stage_01_data_ingestion import DataIngestionTrainingPipeline
from FraudDetectionAI.pipeline.stage_02_data_preprocessing import DataPreprocessingTrainingPipeline
from FraudDetectionAI.pipeline.stage_03_model_trainer import ModelTrainingPipeline
from FraudDetectionAI.pipeline.stage_04_model_evaluation import ModelEvaluationPipeline

STAGE_NAME = "Data Ingestion stage"

def main():
    try:
        logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        data_ingestion = DataIngestionTrainingPipeline()
        data_ingestion.main()
        logging.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise e

    STAGE_NAME = "Data Preprocessing stage"
    try:
        logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        data_preprocessing = DataPreprocessingTrainingPipeline()
        data_preprocessing.main()
        logging.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise e

    STAGE_NAME = "Model Training stage"
    try:
        logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        model_trainer = ModelTrainingPipeline()
        model_trainer.main()
        logging.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise e

    STAGE_NAME = "Model Evaluation stage"
    try:
        logging.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
        model_evaluation = ModelEvaluationPipeline()
        model_evaluation.main()
        logging.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
    except Exception as e:
        logging.exception(e)
        raise e

if __name__ == "__main__":
    main()
