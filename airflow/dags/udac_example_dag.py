from datetime import datetime, timedelta
import datetime
import os
from airflow import conf
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator, LoadDimensionOperator,DataQualityOperator)
from helpers import SqlQueries

# AWS credentials from environment variables.
#AWS_KEY = os.environ.get('AWS_KEY')
#AWS_SECRET = os.environ.get('AWS_SECRET')

""" 

This Apache Airflow DAG provides a pipeline to
* COPY data from AWS S3 to AWS Redshift staging Tables
    (Tasks: Stage_events, Stage_songs)
* Load data from staging tables to star schema fact and dimensions Tables
    (Tasks: Load_songplays_fact_table, Load_user_dim_table, Load_song_dim_table,
    Load_artist_dim_table, Load_time_dim_table)
* Verify the data loaded to fast and dimension tables
    (Tasks: Run_data_quality_checks)
* As a default, DAG has been set to run daily, starting from 2018-11-01
* In case of failure, DAG retries 3 times, after 5 min delay
"""

# Default args 
default_args = {
    'owner': 'snaz3',
    'depends_on_past': False,
    'start_date': datetime.datetime.now(),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 5,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('udac_example_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='@hourly',
          max_active_runs=1
        )

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,    
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",    
    table = "staging_events",
    s3_bucket="udacity-dend",
    s3_key="log_data",
    region="us-west-2",
    s3_path = "s3://udacity-dend/log_data",
    json_path="s3://udacity-dend/log_json_path.json"
)


stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,  
    redshift_conn_id="redshift",
    aws_credentials_id="aws_credentials",    
    table = "staging_songs",
    s3_bucket = "udacity-dend",
    s3_key = "song_data",
    region = "us-west-2",
    s3_path = "s3://udacity-dend/song_data",
    json_path = "auto"
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,    
    redshift_conn_id="redshift",
    table="songplays",
    sql=SqlQueries.songplay_table_insert,
    append_only=False
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    redshift_conn_id="redshift",
    destination_table="songs",
    sql_statement=SqlQueries.song_table_insert,
    update_mode="insert",
    dag=dag
)


load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    redshift_conn_id="redshift",
    destination_table="users",
    sql_statement=SqlQueries.user_table_insert,
    update_mode="insert",
    dag=dag
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    redshift_conn_id="redshift",
    destination_table="artists",
    sql_statement=SqlQueries.artist_table_insert,
    update_mode="insert",
    dag=dag
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    redshift_conn_id="redshift",
    destination_table="time",
    sql_statement=SqlQueries.time_table_insert,
    update_mode="insert",
    dag=dag
)


run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id="redshift",
    tables=[ "songplays", "songs", "artists",  "time", "users"]
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)

start_operator >> stage_events_to_redshift
start_operator >> stage_songs_to_redshift


stage_events_to_redshift >> load_songplays_table
stage_songs_to_redshift >> load_songplays_table

load_songplays_table >> load_user_dimension_table
load_songplays_table >> load_song_dimension_table
load_songplays_table >> load_artist_dimension_table
load_songplays_table >> load_time_dimension_table

load_user_dimension_table >> run_quality_checks
load_song_dimension_table >> run_quality_checks
load_artist_dimension_table >> run_quality_checks
load_time_dimension_table >> run_quality_checks

run_quality_checks >> end_operator