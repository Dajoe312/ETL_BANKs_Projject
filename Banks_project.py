from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

def log_progress(message):
    timestamp_format = '%Y-%h-%d-%H:%M:%S'  # Year-Monthname-Day-Hour-Minute-Second
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open("./code_log.txt", "a") as f:
        f.write(timestamp + ' : ' + message + '\n')

def extract(url, table_attribs):
    page = requests.get(url).text
    data = BeautifulSoup(page, 'html.parser')
    df = pd.DataFrame(columns=table_attribs)
    tables = data.find_all('tbody')
    rows = tables[0].find_all('tr')
    for row in rows:
        col = row.find_all('td')
        if len(col) != 0:
            data_dict = {"Name": col[1].get_text(strip=True),
                         "MC_USD_Billion": float(col[2].contents[0][:-1])}  # strip trailing '\n', cast to float
            df1 = pd.DataFrame(data_dict, index=[0])
            df = pd.concat([df, df1], ignore_index=True)
    return df

def transform(df, exchange_rate_csv):
    # Load exchange rates into a dict: {'EUR': 0.93, 'GBP': 0.8, 'INR': 82.95}
    exchange_rate = pd.read_csv(exchange_rate_csv).set_index('Currency').to_dict()['Rate']

    gbp_rate = float(exchange_rate['GBP'])
    eur_rate = float(exchange_rate['EUR'])
    inr_rate = float(exchange_rate['INR'])

    df['MC_GBP_Billion'] = [np.round(x * gbp_rate, 2) for x in df['MC_USD_Billion']]
    df['MC_EUR_Billion'] = [np.round(x * eur_rate, 2) for x in df['MC_USD_Billion']]
    df['MC_INR_Billion'] = [np.round(x * inr_rate, 2) for x in df['MC_USD_Billion']]

    return df

def load_to_csv(df, csv_path):
    df.to_csv(csv_path)

def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists='replace', index=False)

def run_query(query_statement, sql_connection):
    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)

# ---- Declaring known values ----
url = 'https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks'
table_attribs = ["Name", "MC_USD_Billion"]
exchange_rate_csv = 'exchange_rate.csv'
db_name = 'Banks.db'
table_name = 'Largest_banks'
csv_path = './Largest_banks_data.csv'

log_progress('Preliminaries complete. Initiating ETL process')

# ---- Task 2: Extraction ----
df = extract(url, table_attribs)
# print(df)  # Task 2's print — commented out per Task 3's instruction
log_progress('Data extraction complete. Initiating Transformation process')

# ---- Task 3: Transformation ----
df = transform(df, exchange_rate_csv)
print(df)
log_progress('Data transformation complete. Initiating Loading process')

# ---- Task 4: Load to CSV ----
load_to_csv(df, csv_path)
log_progress('Data saved to CSV file')

# ---- Task 5: Load to Database ----
sql_connection = sqlite3.connect(db_name)
log_progress('SQL Connection initiated')

load_to_db(df, sql_connection, table_name)
log_progress('Data loaded to Database as a table, Executing queries')

# ---- Task 6: Run queries ----
query_statement = f"SELECT * FROM {table_name}"
run_query(query_statement, sql_connection)

query_statement = f"SELECT AVG(MC_GBP_Billion) FROM {table_name}"
run_query(query_statement, sql_connection)

query_statement = f"SELECT Name from {table_name} LIMIT 5"
run_query(query_statement, sql_connection)

log_progress('Process Complete')

# ---- Close connection ----
sql_connection.close()
log_progress('Server Connection closed')