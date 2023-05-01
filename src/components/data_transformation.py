import os
import sys
import numpy as np
import pandas as pd

from src.utils import save_object
from src.logger import logging
from src.exception import CustomException

from dataclasses import dataclass
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder


@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path = os.path.join('artifacts', 'preprocessor.pkl')


class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()
        
    def get_data_transformer_object(self):
        try:
            numerical_features = ['reading_score', 'writing_score']
            categorical_features = [
                'gender', 
                'race_ethnicity', 
                'parental_level_of_education', 
                'lunch',
                'test_preparation_course'
            ]
        
            numerical_pipeline = Pipeline(
                steps=[
                    ('imputer', SimpleImputer(strategy='median')),
                    ('scaler', StandardScaler(with_mean=False))
                ]
            )
            logging.info('Numerical columns standard scalling completed.')

            categorical_pipeline = Pipeline(
                steps=[
                    ('imputer', SimpleImputer(strategy='most_frequent')),
                    ('encoder', OneHotEncoder()),
                    ('scaler', StandardScaler(with_mean=False))
                ]
            )
            logging.info('Categorical columns encoding completed.')

            preprocessor = ColumnTransformer(
                [
                    ('numerical_pipeline', numerical_pipeline, numerical_features),
                    ('categorical_pipeline', categorical_pipeline, categorical_features)
                ]
            )
            return preprocessor
        except Exception as e:
            raise CustomException(e, sys)


    def initiate_data_transformation(self, train_path, test_path):
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            logging.info('Read train and test data completed.')
            logging.info('Obtaining preprocessor object')

            preprocessing_obj = self.get_data_transformer_object()

            target_column = 'math_score'
            numerical_columns = ['reading_score', 'writing_score']

            train_input_features = train_df.drop(columns=[target_column], axis=1)
            train_target_feature = train_df[target_column]

            test_input_features = test_df.drop(columns=[target_column], axis=1)
            test_target_feature = test_df[target_column]

            logging.info(
                f'Applying preprocessing object on training dataframe and testing dataframe.'
            )

            train_input_features_arr = preprocessing_obj.fit_transform(train_input_features)
            test_inpute_features_arr = preprocessing_obj.fit_transform(test_input_features)

            train_arr = np.c_[train_input_features_arr, np.array(train_target_feature)]
            test_arr = np.c_[test_inpute_features_arr, np.array(test_target_feature)]

            logging.info('Saved preprocessing object.')
            save_object(
                file_path = self.data_transformation_config.preprocessor_obj_file_path,
                obj = preprocessing_obj
            )
            return (
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_obj_file_path
            )
        except Exception as e:
            raise CustomException(e, sys)
