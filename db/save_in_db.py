from rrs.scraper import load_flats_table
from rrs.user_input import select_city
from db.db_code import create_connection
from db.db_code import close_connection
from db.db_dir import _starting_dir


conn = create_connection(_starting_dir() + "\db_flats.db")

city_list = select_city()

if len(city_list) > 1:
    for city in city_list:
        print("Working on flats from" + city)
        df = load_flats_table(city)
        df.to_sql('flats_rent', conn, if_exists='append', index=False)
else:
    df = load_flats_table(city_list[0])
    df.to_sql('flats_rent', conn, if_exists='append', index=False)


close_connection(_starting_dir() + "\db_flats.db")