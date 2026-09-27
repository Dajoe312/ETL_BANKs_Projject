# ETL Banks Project

A Python ETL (Extract–Transform–Load) pipeline that scrapes the world's largest banks by market capitalization from an archived Wikipedia page, converts the figures into four currencies, and loads the results into both a CSV file and a SQLite database — with progress logged at every stage.

## What it does

`Banks_project.py` runs a full ETL pipeline built from five functions:

| Function | Purpose |
|---|---|
| `extract(url, table_attribs)` | Fetches the archived page with `requests`, parses the "By market capitalization" table with `BeautifulSoup`, and builds a DataFrame of `Name` / `MC_USD_Billion` |
| `transform(df, exchange_rate_csv)` | Reads exchange rates from a CSV and adds `MC_GBP_Billion`, `MC_EUR_Billion`, and `MC_INR_Billion` columns, each rounded to 2 decimal places |
| `load_to_csv(df, csv_path)` | Writes the transformed DataFrame to a CSV file |
| `load_to_db(df, sql_connection, table_name)` | Writes the transformed DataFrame to a table in a SQLite database (replacing it if it already exists) |
| `run_query(query_statement, sql_connection)` | Runs a SQL query against the database and prints both the query and its result |
| `log_progress(message)` | Appends a timestamped line to a log file after each pipeline stage |

The script runs end to end: extract → transform → save to CSV → save to database → run three sample queries → close the connection, logging progress at every step.

## Data source

Data is scraped from a Wayback Machine snapshot of the "List of largest banks" Wikipedia page, under the "By market capitalization" heading:

```
https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks
```

Using an archived snapshot (rather than the live page) keeps the table structure stable — the live page has since been restructured multiple times and no longer contains the same table in the same position.

## Project structure

```
ETL_BANKs_Projject/
├── Banks_project.py          # The ETL pipeline (extract, transform, load, query, log)
├── exchange_rate.csv         # Input: USD → EUR/GBP/INR exchange rates
├── Largest_banks_data.csv    # Output: transformed data as CSV
├── Banks.db                  # Output: transformed data loaded into SQLite (table: Largest_banks)
├── code_log.txt              # Output: timestamped log of each pipeline stage
└── README.md
```

## Requirements

- Python 3.8+
- [requests](https://pypi.org/project/requests/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- [pandas](https://pypi.org/project/pandas/)
- [numpy](https://pypi.org/project/numpy/)

`sqlite3` and `datetime` are part of the Python standard library.

```bash
pip install requests beautifulsoup4 pandas numpy
```

`exchange_rate.csv` must be present alongside the script, with two columns:

```
Currency,Rate
EUR,0.93
GBP,0.8
INR,82.95
```

## Usage

```bash
git clone https://github.com/Dajoe312/ETL_BANKs_Projject.git
cd ETL_BANKs_Projject
python Banks_project.py
```

Running the script will:
1. Scrape and parse the bank market-cap table from the archived page.
2. Convert each bank's market cap from USD into GBP, EUR, and INR.
3. Overwrite `Largest_banks_data.csv` with the latest data.
4. Overwrite the `Largest_banks` table in `Banks.db`.
5. Print the results of three queries: the full table, the average market cap in GBP, and the top 5 bank names.
6. Append a fresh set of timestamped entries to `code_log.txt`.

## Sample output

The top 10 banks by market cap (USD billions), as of the archived snapshot:

| Name | MC_USD_Billion | MC_GBP_Billion | MC_EUR_Billion | MC_INR_Billion |
|---|---|---|---|---|
| JPMorgan Chase | 432.92 | 346.34 | 402.62 | 35,910.71 |
| Bank of America | 231.52 | 185.22 | 215.31 | 19,204.58 |
| Industrial and Commercial Bank of China | 194.56 | 155.65 | 180.94 | 16,138.75 |
| Agricultural Bank of China | 160.68 | 128.54 | 149.43 | 13,328.41 |
| HDFC Bank | 157.91 | 126.33 | 146.86 | 13,098.63 |
| Wells Fargo | 155.87 | 124.70 | 144.96 | 12,929.42 |
| HSBC Holdings PLC | 148.90 | 119.12 | 138.48 | 12,351.26 |
| Morgan Stanley | 140.83 | 112.66 | 130.97 | 11,681.85 |
| China Construction Bank | 139.82 | 111.86 | 130.03 | 11,598.07 |
| Bank of China | 136.81 | 109.45 | 127.23 | 11,348.39 |

## Inspecting the results

```bash
sqlite3 Banks.db
sqlite> SELECT * FROM Largest_banks;
sqlite> SELECT AVG(MC_GBP_Billion) FROM Largest_banks;
```

Or with `pandas`:

```python
import pandas as pd
df = pd.read_csv("Largest_banks_data.csv")
print(df.head())
```

## Notes

- Exchange rates are a fixed snapshot in `exchange_rate.csv`, not live — update that file if more current rates are needed.
- The bank name is extracted with `.get_text(strip=True)` rather than indexing directly into the cell's child nodes, since some cells contain hidden/nested elements (e.g. sort-key spans) before the visible name.

## License

No license specified.
