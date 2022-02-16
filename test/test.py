import sqlite3
import pandas as pd
from db.db_code import create_connection
from db.db_code import close_connection

conn = create_connection("db_file")

print(pd.read_sql('select * from flats_rent', conn))