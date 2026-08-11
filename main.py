from FraudDetectionAI.logger import logging
from FraudDetectionAI.pipeline.stage_01_data_ingestion import DataIngestionTrainingPipeline
from FraudDetectionAI.pipeline.stage_02_data_preprocessing import DataPreprocessingTrainingPipeline

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

if __name__ == "__main__":
    main()
