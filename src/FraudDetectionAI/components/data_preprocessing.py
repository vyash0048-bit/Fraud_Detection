import os
import pandas as pd
import numpy as np
import gc
from sklearn.preprocessing import RobustScaler
from FraudDetectionAI.logger import logging
from FraudDetectionAI.entity.config_entity import DataPreprocessingConfig

class DataPreprocessing:
    def __init__(self, config: DataPreprocessingConfig):
        self.config = config
        self.constant_cols = []
        self.numerical_cols = []
        self.categorical_cols = []
        self.freq_encoding_maps = {}
        self.scaler = RobustScaler()
        self.medians = {}

    def reduce_mem_usage(self, df):
        """ iterate through all the columns of a dataframe and modify the data type
            to reduce memory usage.        
        """
        start_mem = df.memory_usage().sum() / 1024**2
        logging.info(f'Memory usage of dataframe is {start_mem:.2f} MB')
        
        for col in df.columns:
            col_type = df[col].dtype
            
            if col_type != object and col_type.name != 'category':
                c_min = df[col].min()
                c_max = df[col].max()
                if str(col_type)[:3] == 'int':
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        df[col] = df[col].astype(np.int64)  
                else:
                    if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        df[col] = df[col].astype(np.float16)
                    elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        df[col] = df[col].astype(np.float32)
                    else:
                        df[col] = df[col].astype(np.float64)
        
        end_mem = df.memory_usage().sum() / 1024**2
        logging.info(f'Memory usage after optimization is: {end_mem:.2f} MB')
        logging.info(f'Decreased by {100 * (start_mem - end_mem) / start_mem:.1f}%')
        
        return df.copy()

    def feature_engineering(self, df):
        logging.info("Performing advanced feature engineering...")
        df = df.copy()
        
        # 1. Missing Value Counts
        df['Nan_Count'] = df.isnull().sum(axis=1)
        
        # 2. Transaction Amount Features
        if 'TransactionAmt' in df.columns:
            df['TransactionAmt_Log'] = np.log1p(df['TransactionAmt'])
            df['TransactionAmt_Decimal'] = df['TransactionAmt'] - np.floor(df['TransactionAmt'])
            
            # Entity: Card (using card1 as proxy)
            if 'card1' in df.columns:
                # To prevent leakage, ensure it's sorted by time
                if 'TransactionDT' in df.columns:
                    df = df.sort_values('TransactionDT')
                
                # Cumulative count of transactions for this card
                df['Card_Txn_Count_Hist'] = df.groupby('card1').cumcount()
                
                # Time since last transaction
                if 'TransactionDT' in df.columns:
                    df['Time_Since_Last_Txn'] = df.groupby('card1')['TransactionDT'].diff().fillna(-1)
                
                # Historical rolling mean amount per card (shifted to avoid leakage)
                df['Card_Amt_Mean_Hist'] = df.groupby('card1')['TransactionAmt'] \
                                             .transform(lambda x: x.shift(1).expanding().mean()).fillna(df['TransactionAmt'].mean())
                
                # Historical rolling std amount per card
                df['Card_Amt_Std_Hist'] = df.groupby('card1')['TransactionAmt'] \
                                            .transform(lambda x: x.shift(1).expanding().std()).fillna(0)
                                            
                df['Amt_vs_Hist_Mean'] = df['TransactionAmt'] / (df['Card_Amt_Mean_Hist'] + 1e-5)
                df['Amt_vs_Hist_Std'] = (df['TransactionAmt'] - df['Card_Amt_Mean_Hist']) / (df['Card_Amt_Std_Hist'] + 1e-5)
                
        # 3. Email features
        if 'P_emaildomain' in df.columns:
            free_email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'anonymous.com']
            df['Is_Free_Email'] = df['P_emaildomain'].isin(free_email_domains).astype(np.int8)
            
        if 'P_emaildomain' in df.columns and 'R_emaildomain' in df.columns:
            df['Email_Domain_Match'] = (df['P_emaildomain'] == df['R_emaildomain']).astype(np.int8)
            
        # 4. Time features (Is_Weekend relies on DayOfWeek which is calculated later, so we will calculate DayOfWeek here instead)
        if 'TransactionDT' in df.columns:
            day = df['TransactionDT'] // (24 * 60 * 60)
            day_of_week = day % 7
            df['Is_Weekend'] = (day_of_week >= 5).astype(np.int8)

        # 5. Magic Feature: UID (Client identifier) from Kaggle 1st place solution
        if 'card1' in df.columns and 'addr1' in df.columns and 'D1' in df.columns:
            if 'Day' not in df.columns and 'TransactionDT' in df.columns:
                day = df['TransactionDT'] // (24 * 60 * 60)
            else:
                day = df.get('Day', 0)
                
            # Create UID
            df['uid'] = df['card1'].astype(str) + '_' + df['addr1'].astype(str) + '_' + np.floor(day - df['D1']).astype(str)
            
            # Global aggregations within the dataset (similar to the Kaggle notebook)
            agg_cols_mean_std = ['TransactionAmt','D4','D9','D10','D15']
            for col in agg_cols_mean_std:
                if col in df.columns:
                    df[f'UID_{col}_mean'] = df.groupby('uid')[col].transform('mean')
                    df[f'UID_{col}_std'] = df.groupby('uid')[col].transform('std')
            
            agg_cols_mean = [f'C{x}' for x in range(1,15) if x!=3] + [f'M{x}' for x in range(1,10)]
            for col in agg_cols_mean:
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    df[f'UID_{col}_mean'] = df.groupby('uid')[col].transform('mean')
                    
            agg_cols_nunique = ['P_emaildomain','dist1','id_02','TransactionAmt_Decimal', 'C13','V314', 'V127','V136','V309','V307','V320']
            for col in agg_cols_nunique:
                if col in df.columns:
                    df[f'UID_{col}_nunique'] = df.groupby('uid')[col].transform('nunique')
                    
            if 'C14' in df.columns:
                df['UID_C14_std'] = df.groupby('uid')['C14'].transform('std')
            
        return df.copy()

    def initiate_data_preprocessing(self):
        logging.info("Starting data preprocessing")
        
        try:
            # Load and merge train data
            logging.info("Reading train data...")
            train_transaction = pd.read_csv(self.config.train_data_path)
            train_identity = pd.read_csv(self.config.train_identity_path)
            train = pd.merge(train_transaction, train_identity, on='TransactionID', how='left')
            del train_transaction, train_identity
            gc.collect()
            train = self.reduce_mem_usage(train)
            
            # Load and merge test data
            logging.info("Reading test data...")
            test_transaction = pd.read_csv(self.config.test_data_path)
            test_identity = pd.read_csv(self.config.test_identity_path)
            test = pd.merge(test_transaction, test_identity, on='TransactionID', how='left')
            del test_transaction, test_identity
            
            # Fix famous IEEE-CIS dataset quirk: test identity columns use '-' instead of '_'
            test.columns = test.columns.str.replace('-', '_', regex=False)
            gc.collect()
            test = self.reduce_mem_usage(test)

            # 1. Datetime/time variables
            logging.info("Engineering Datetime variables...")
            for df in [train, test]:
                if 'TransactionDT' in df.columns:
                    # Assuming TransactionDT is in seconds
                    df['Day'] = df['TransactionDT'] // (24 * 60 * 60)
                    df['Hour'] = (df['TransactionDT'] // (60 * 60)) % 24
                    df['DayOfWeek'] = df['Day'] % 7
            
            train = train.copy()
            test = test.copy()
            
            # 2. Duplicate records
            logging.info("Removing duplicate records...")
            initial_len = len(train)
            train = train.drop_duplicates()
            logging.info(f"Dropped {initial_len - len(train)} duplicate records from train data.")
            
            # Feature Engineering on Combined Data (Kaggle Magic)
            logging.info("Combining train and test for global UID aggregations...")
            train['is_test_data_flag'] = False
            test['is_test_data_flag'] = True
            
            combined = pd.concat([train, test], ignore_index=True)
            combined = self.feature_engineering(combined)
            
            train = combined[combined['is_test_data_flag'] == False].copy()
            test = combined[combined['is_test_data_flag'] == True].copy()
            
            train.drop(columns=['is_test_data_flag'], inplace=True)
            test.drop(columns=['is_test_data_flag'], inplace=True)
            del combined
            gc.collect()
            
            # 3. Train/validation splitting (Time-based to prevent leakage)
            logging.info("Performing Time-based Train/Validation split...")
            if 'TransactionDT' in train.columns:
                train = train.sort_values('TransactionDT').reset_index(drop=True)
            
            # 80/20 Time-based split
            split_idx = int(len(train) * 0.8)
            val = train.iloc[split_idx:].copy()
            train = train.iloc[:split_idx].copy()
            
            # Determine Categorical vs Numerical safely
            from pandas.api.types import is_numeric_dtype
            self.numerical_cols = [c for c in train.columns if is_numeric_dtype(train[c]) and c not in ['TransactionID', 'isFraud', 'TransactionDT']]
            self.categorical_cols = [c for c in train.columns if c not in self.numerical_cols and c not in ['TransactionID', 'isFraud', 'TransactionDT']]

            # 4. Constant/near-constant variables
            logging.info("Identifying constant and near-constant variables on Train set...")
            threshold = 0.99
            for col in train.columns:
                if col in ['TransactionID', 'isFraud']:
                    continue
                # Check frequency of most common value
                if train[col].value_counts(dropna=False, normalize=True).iloc[0] > threshold:
                    self.constant_cols.append(col)
            
            logging.info(f"Dropping {len(self.constant_cols)} constant/near-constant columns.")
            train = train.drop(columns=self.constant_cols, errors='ignore')
            val = val.drop(columns=self.constant_cols, errors='ignore')
            test = test.drop(columns=self.constant_cols, errors='ignore')
            
            # Update columns list
            self.categorical_cols = [c for c in self.categorical_cols if c not in self.constant_cols]
            self.numerical_cols = [c for c in self.numerical_cols if c not in self.constant_cols]
            
            # 5. Missing values (Leakage prevention: learn parameters ONLY from Train)
            logging.info("Handling missing values...")
            for col in self.numerical_cols:
                self.medians[col] = train[col].median()
                train[col] = train[col].fillna(self.medians[col])
                val[col] = val[col].fillna(self.medians[col])
                if col in test.columns:
                    test[col] = test[col].fillna(self.medians[col])
                    
            for col in self.categorical_cols:
                train[col] = train[col].fillna('missing')
                val[col] = val[col].fillna('missing')
                if col in test.columns:
                    test[col] = test[col].fillna('missing')

            # 6. Categorical variables & High-cardinality categorical variables
            logging.info("Encoding categorical variables (Frequency Encoding)...")
            for col in self.categorical_cols:
                freq = train[col].value_counts()
                self.freq_encoding_maps[col] = freq
                
                # Apply mapping and fill unseen categories in val/test with 0
                train[col] = train[col].map(freq).fillna(0)
                val[col] = val[col].map(freq).fillna(0)
                if col in test.columns:
                    test[col] = test[col].map(freq).fillna(0)
            
            # 7. Outliers (using RobustScaler)
            logging.info("Scaling numerical features with RobustScaler to handle outliers...")
            train[self.numerical_cols] = self.scaler.fit_transform(train[self.numerical_cols])
            val[self.numerical_cols] = self.scaler.transform(val[self.numerical_cols])
            
            # Ensure we only pass columns that exist, but ordered properly
            test_num_cols = [c for c in self.numerical_cols if c in test.columns]
            if len(test_num_cols) == len(self.numerical_cols):
                test[self.numerical_cols] = self.scaler.transform(test[self.numerical_cols])
            else:
                logging.warning(f"Test numerical columns do not match Train perfectly. Using only available columns for scaling.")
                # This handles edge cases where some columns are genuinely missing
                self.scaler.feature_names_in_ = np.array(test_num_cols) # hack to bypass sklearn if absolutely needed, though renaming fixed it
                test[test_num_cols] = self.scaler.transform(test[test_num_cols])

            # Optional: reduce memory usage before saving
            logging.info("Reducing memory usage...")
            train = self.reduce_mem_usage(train)
            val = self.reduce_mem_usage(val)
            test = self.reduce_mem_usage(test)

            logging.info("Saving preprocessed data...")
            train.to_csv(self.config.preprocessed_train_path, index=False)
            val.to_csv(self.config.preprocessed_val_path, index=False)
            test.to_csv(self.config.preprocessed_test_path, index=False)
            
            logging.info("Data preprocessing completed successfully")
            
        except Exception as e:
            logging.error(f"Error in data preprocessing: {e}")
            raise e
