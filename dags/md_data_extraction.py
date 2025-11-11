#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script creates a dag that runs 
fetchdata.py to extract Maryland environmental 
enforcement data.
"""

import os
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta

# Define the path to fetchdata.py
PARENT_DIR_PATH = os.path.dirname(os.getcwd())
FETCH_DATA_PATH = (os
                   .path
                   .join(PARENT_DIR_PATH,
                         "fetchdata.py")
                         )

# default arguments for the DAG
DAG_DEFAULT_ARGS = {
	"owner": "airflow",
	"depends_on_past": False,
	"email_on_failure": False,
	"email_on_retry": False,
	"retries": 1,
	"retry_delay": timedelta(minutes=2),
}

# arguments that define the DAG
DESCRIPTION = ("Extract Maryland environmental " + 
               "enforcement data via fetchdata.py")
DAG_DEFINE_ARGS = {
    "dag_id": "md_data_extraction",
    "description": DESCRIPTION,
    "default_args": DAG_DEFAULT_ARGS,
    "start_date": datetime(2024, 1, 1),
    "schedule": "0 6 * * *",
    "catchup": False,
}

with DAG(**DAG_DEFINE_ARGS) as dag:

    run_fetchdata = PythonOperator(
        task_id="run_fetchdata",
        python_callable=os.system,
        op_args=[f"python3 {FETCH_DATA_PATH}"],
    )

    # fetching data task
    run_fetchdata