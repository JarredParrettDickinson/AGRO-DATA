import pyodbc
from sqlalchemy import create_engine
import urllib
import pandas as pd
from pandas import DataFrame
# Update connection string information
server = "agrodatadb.database.windows.net"
database = "agrodatadb"
username = "JarredParrett"
password = "8!DEzXjlfPKXYTff"

params = urllib.parse.quote_plus \
(r' Driver={ODBC Driver 17 for SQL Server};Server=tcp:agrodatadb.database.windows.net,1433;Database=agrodata;Uid=JarredParrett;Pwd=8!DEzXjlfPKXYTff;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
engine_azure = create_engine(conn_str,echo=True)



def execute_sql(statment):
    rs = engine_azure.execute(statment)
    return rs

def execute_sql_to_df(statment):
    rs = execute_sql(statment)
    df = DataFrame(rs.fetchall())
    df.columns = rs.keys()
    return df
