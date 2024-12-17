import sqlite3 as sql
from docx import Document

doc = Document(docx="shelf.docx")

with sql.connect(database=r"\\CEH19TT\_shared access\Databases\DocExp\list.db") as conn:
    cursor = conn.cursor()

    for table in doc.tables:
        for row in table.rows:

            shelf_row = []
            for cell in row.cells:
                shelf_row.append(cell.text)

            shelf_row[-1] = shelf_row[-1].replace(" ", "").replace("/", "-")

            cursor.execute(f"""CREATE TABLE IF NOT EXISTS "{shelf_row[-1]}" (
                        Обозначение TEXT, 
                        Наименование TEXT)""")
            
            cursor.execute(f'INSERT OR IGNORE INTO "{shelf_row[-1]}" VALUES (?, ?)', [shelf_row[0], shelf_row[2]])