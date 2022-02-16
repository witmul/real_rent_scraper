import pandas as pd
from db.db_code import create_connection
from db.db_code import close_connection
from db.db_dir import _starting_dir

# Connect to the database
conn = create_connection(_starting_dir() + "\db_flats.db")

# Run SQL
sql_query = pd.read_sql('SELECT * FROM flats_rent', conn)
print(sql_query)

close_connection(_starting_dir() + "\db_flats.db")