from pathlib import Path

import pandas as pd
from backend.database.connection import get_connection

CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "exoplanets_raw.csv"
COLUMNS = [
    "pl_name", "hostname", "discoverymethod", "disc_year", "pl_orbper",
    "pl_orbsmax", "pl_rade", "pl_bmasse", "pl_bmassprov", "pl_orbeccen",
    "pl_insol", "pl_eqt", "st_teff", "st_rad", "st_mass", "st_met",
    "st_spectype", "sy_dist",
]

df = pd.read_csv(CSV_PATH, usecols=COLUMNS)[COLUMNS]       # keep our column order
df = df.astype(object).where(df.notna(), None)             # NaN -> None
rows = [tuple(r) for r in df.itertuples(index=False, name=None)]

print(f"Prepared {len(rows)} rows")

connection = None
cursor = None
try:
    connection = get_connection()                         
    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE staging_exoplanets")
    sql = f"INSERT INTO staging_exoplanets ({", ".join(COLUMNS)}) VALUES ({", ".join(["%s"] * len(COLUMNS))})"
    cursor.executemany(sql, rows)
    connection.commit()
    print(f"Inserted {len(rows)} rows")
finally:
    if cursor is not None:
        cursor.close()
    if connection is not None:
        connection.close()