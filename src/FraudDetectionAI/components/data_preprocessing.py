import os
import pandas as pd
from FraudDetectionAI.logger import logging
from FraudDetectionAI.entity.config_entity import DataPreprocessingConfig

class DataPreprocessing:
    def __init__(self, config: DataPreprocessingConfig):
        self.config = config

    def reduce_mem_usage(self, df):
        """ iterate through all the columns of a dataframe and modify the data type
            to reduce memory usage.        
        """
        start_mem = df.memory_usage().sum() / 1024**2
        logging.info(f'Memory usage of dataframe is {start_mem:.2f} MB')
        
        for col in df.columns:
            col_type = df[col].dtype
            
            if col_type != object:
                c_min = df[col].min()
                c_max = df[col].max()
                if str(col_type)[:3] == 'int':
                    if c_min > pd.np.iinfo(pd.np.int8).min and c_max < pd.np.iinfo(pd.np.int8).max:
                        df[col] = df[col].astype(pd.np.int8)
                    elif c_min > pd.np.iinfo(pd.np.int16).min and c_max < pd.np.iinfo(pd.np.int16).max:
                        df[col] = df[col].astype(pd.np.int16)
                    elif c_min > pd.np.iinfo(pd.np.int32).min and c_max < pd.np.iinfo(pd.np.int32).max:
                        df[col] = df[col].astype(pd.np.int32)
                    elif c_min > pd.np.iinfo(pd.np.int64).min and c_max < pd.np.iinfo(pd.np.int64).max:
                        df[col] = df[col].astype(pd.np.int64)  
                else:
                    if c_min > pd.np.finfo(pd.np.float16).min and c_max < pd.np.finfo(pd.np.float16).max:
                        df[col] = df[col].astype(pd.np.float16)
                    elif c_min > pd.np.finfo(pd.np.float32).min and c_max < pd.np.finfo(pd.np.float32).max:
                        df[col] = df[col].astype(pd.np.float32)
                    else:
                        df[col] = df[col].astype(pd.np.float64)
        
        end_mem = df.memory_usage().sum() / 1024**2
        logging.info(f'Memory usage after optimization is: {end_mem:.2f} MB')
        logging.info(f'Decreased by {100 * (start_mem - end_mem) / start_mem:.1f}%')
        
        return df

    def initiate_data_preprocessing(self):
        logging.info("Starting data preprocessing")
        
        try:
            # Load and merge train data
            logging.info("Reading train data...")
            train_transaction = pd.read_csv(self.config.train_data_path)
            train_identity = pd.read_csv(self.config.train_identity_path)
            
            logging.info("Merging train data...")
            train = pd.merge(train_transaction, train_identity, on='TransactionID', how='left')
            del train_transaction, train_identity
            
            # Load and merge test data
            logging.info("Reading test data...")
            test_transaction = pd.read_csv(self.config.test_data_path)
            test_identity = pd.read_csv(self.config.test_identity_path)
            
            logging.info("Merging test data...")
            test = pd.merge(test_transaction, test_identity, on='TransactionID', how='left')
            del test_transaction, test_identity
            
            # Reduce memory usage (optional but recommended for this dataset)
            # We'll skip it in this basic script to avoid np dependency issues unless needed,
            # but let's implement a simpler null filling strategy.
            
            logging.info("Handling missing values...")
            # For simplicity, filling numeric with median and categorical with 'missing'
            # (In a real scenario, this would be more sophisticated)
            
            for col in train.columns:
                if pd.api.types.is_numeric_dtype(train[col]):
                    median_val = train[col].median()
                    train[col] = train[col].fillna(median_val)
                    if col in test.columns:
                        test[col] = test[col].fillna(median_val)
                else:
                    train[col] = train[col].fillna('missing')
                    if col in test.columns:
                        test[col] = test[col].fillna('missing')
            
            logging.info("Saving preprocessed data...")
            train.to_csv(self.config.preprocessed_train_path, index=False)
            test.to_csv(self.config.preprocessed_test_path, index=False)
            
            logging.info("Data preprocessing completed successfully")
            
        except Exception as e:
            logging.error(f"Error in data preprocessing: {e}")
            raise e
