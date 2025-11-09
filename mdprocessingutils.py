#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains utility functions for processing
Maryland environmental data.
"""

import pandas as pd
import os

CURRENT_DIR = os.getcwd()
raw_data_path = os.path.join(CURRENT_DIR,'raw_data')

def get_all_file_paths(directory):
    """
    Retrieves a list of all absolute file paths within 
    a given directory.
    """
    file_paths = []
    for root, _, files in os.walk(directory):
        for file_name in files:
            full_path = os.path.join(root, file_name)
            file_paths.append(full_path)
    return file_paths

def null_value_report(df):
    """
    Generates a report of null values in each column of 
    the DataFrame.
    """
    null_report = df.isnull().sum()
    return null_report

def string_split_column(df,column_name,delimiter):
    """
    Splits the specified string column into multiple columns
    based on the given delimiter.
    """
    split_cols = df[column_name].str.split(delimiter, expand=True)
    for i in range(split_cols.shape[1]):
        df[f"{column_name}_{i+1}"] = split_cols[i]
    df.drop(columns=[column_name], inplace=True)

    return df

def rename_split_columns(df,base_col_name='city_state_zip'):
    """
    Renames columns generated from 
    splitting a string column. Assumes generation from
    string_split_column function.
    """
    col_names = base_col_name.split('_')
    rename_dict = {}
    for i, name in enumerate(col_names):
        old_col_name = f"{base_col_name}_{i+1}"
        rename_dict[old_col_name] = name

    df.rename(columns=rename_dict, inplace=True)

    return df

def combine_2_cols(df,col1,col2,new_col_name,separator=' '):
    """
    Combines two specified columns into a new column
    with a given separator.
    """
    df[new_col_name] = (df[col1]
                        .astype(str) 
                        + separator 
                        + df[col2]
                        .astype(str)
                        )
    
    # dropping the original columns (optional)
    df.drop(columns=[col1, col2],inplace=True)

    return df