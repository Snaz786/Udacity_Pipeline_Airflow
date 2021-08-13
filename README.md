# INTRODUCTION

## ETL Data Pipelines with Airflow

### Project Summary

A music streaming company, Sparkify, has decided that it is time to introduce more automation and monitoring to their data warehouse ETL pipelines. They have come to the conclusion that the best tool to achieve this is Apache Airflow.

The source data resides in Amazon S3 buckets and needs to be processed in Sparkify's data warehouse in Amazon Redshift. The source datasets may consist of CSV or JSON logs that record user activity in the application and store metadata about the songs that have been played.

For this project, I have created a data pipeline using the Airflow python API. The pipeline is dynamic, built from reusable tasks, can be monitored, allows easy backfills, and conducts automated data quality checks.This project consists of one Directed Acyclic Graph that implements the data pipeline responsible for reading all Sparkify's event logs, process and create some fact/dimensions tables described in our data schema down below.

For illustration purposes you can check out the graph that represents this pipeline's flow:

![alt text](https://github.com/Snaz786/Udacity_Pipeline_Airflow/blob/master/Images/ETL_DAG.JPG)


### ETL pipeline Steps:-

1) Stages the raw data
2) Transform the raw data to the songplays fact table
3) Transform the raw data into the dimensions tables.
4) Finally, check if the fact/dimensions table has at least one row.

### Sources of Data:-We will read basically two main data sources on Amazon S3:

1) s3://udacity-dend/song_data/ - JSON files containing meta information about song/artists data
2) s3://udacity-dend/log_data/ - JSON files containing log events from the Sparkify app

The project template package contains three major components for the project:

1) The dag template has all the imports and task templates in place, but the task dependencies have been set.
2) The operators folder with operator templates
3) A helper class for the SQL transformations

### Files in Repository

/airflow/dags/udac_example_dag.py DAG definition file. Calls Operators to stage data to redshift, populate the data warehouse and run data quality checks.

/airflow/create_tables.sql Optional script to create staging and data warehouse tables in Redshift.I had directly ran these create tables on AWS reshift, hence didnt create a new Operator.

/airflow/plugins/operators/stage_redshift.py Defines the custom operator StageToRedshiftOperator. This operator loads data from S3 to staging tables in redshift. User may specify csv or JSON file format. Csv file options include delimiter and whether to ignore headers. JSON options include automatic parsing or use of JSONpaths file in the COPY command.

/airflow/plugins/operators/load_fact.py Defines the custom operator LoadFactOperator. This operator appends data from staging tables into the main fact table(SongPlays Table)

/airflow/plugins/operators/load_dimension.py Defines the custom operator LoadDimensionOperator. This operator loads data into dimension tables(artists,song,user,time) from staging tables. Update mode can set to 'insert' or 'overwrite'.

/airflow/plugins/operators/data_quality.py Defines the custom operator DataQualityOperator. This operator performs any number of data quality checks at the end of the pipeline run. The project provides two pre-defined checks in the helper files:

## How to Run

### Prerequisites: Access to AWS credentials and an Amazon Redshift cluster.

1) Put project files in their respective folders in an Airflow installation.
2) Adjust parameters in the DAG script, udac_example_dag.py, as desired.
3) Create aws_credentials and redshift connections in Airflow.
4) Launch udac_example_dag from the Airflow UI.Run /opt/airflow/start.sh to start DAG and watch for any errors if DAG is not launched in the logs.


### Quality Check:-

Count check: Raises task error when a tables are below zero records is detected in the fact table and dimension tables.
Users can specify their own data quality checks by entering the SQL query, table name and expected results as parameters.

![alt text](https://github.com/Snaz786/Udacity_Pipeline_Airflow/blob/master/Images/Quality_check.JPG)

