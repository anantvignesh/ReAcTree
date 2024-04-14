# db_helpers.py
import asyncio
import pandas as pd
import psycopg2
import asyncpg
from google.cloud import bigquery
import time

class PostgresDBHelper:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        self.connection_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }

    async def async_connect(self):
        self.conn = await asyncpg.connect(**self.connection_params)
    
    def sync_connect(self):
        self.conn = psycopg2.connect(**self.connection_params)
    
    async def close_async(self):
        await self.conn.close()
    
    def close_sync(self):
        self.conn.close()
    
    async def read_query_df_async(self, query):
        await self.async_connect()
        records = await self.conn.fetch(query)
        await self.close_async()
        return pd.DataFrame(records)
    
    def read_query_df_sync(self, query):
        self.sync_connect()
        df = pd.read_sql_query(query, self.conn)
        self.close_sync()
        return df

class BigQueryDBHelper:
    def __init__(self, project_id):
        self.client = bigquery.Client(project=project_id)

    async def read_query_async(self, query):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.client.query, query)
        df = await loop.run_in_executor(None, result.result().to_dataframe)
        return df

    def read_query_sync(self, query):
        start_time = time.time()
        result = self.client.query(query)
        df = result.result().to_dataframe()
        end_time = time.time()
        execution_time = end_time - start_time
        print("Execution time:", execution_time)
        return df