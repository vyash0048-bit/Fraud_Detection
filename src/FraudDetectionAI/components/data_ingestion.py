import os
import gdown
from dotenv import load_dotenv
from FraudDetectionAI.logger import logging
from FraudDetectionAI.entity.config_entity import DataIngestionConfig

# Load environment variables
load_dotenv()

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config
        self.gdrive_link = os.getenv("GDRIVE_LINK")

    def download_data(self):
        """
        Download dataset from Google Drive
        """
        try:
            if not self.gdrive_link:
                raise ValueError("GDRIVE_LINK environment variable is not set")
                
            logging.info(f"Downloading dataset from Google Drive...")
            
            # Create local_data_dir if it doesn't exist
            os.makedirs(self.config.local_data_dir, exist_ok=True)
            
            # gdown.download_folder takes URL or folder ID
            gdown.download_folder(url=self.gdrive_link, output=str(self.config.local_data_dir), quiet=False)
            
            logging.info(f"Dataset downloaded successfully at {self.config.local_data_dir}")
            
        except Exception as e:
            logging.error(f"Error while downloading dataset: {e}")
            raise e
