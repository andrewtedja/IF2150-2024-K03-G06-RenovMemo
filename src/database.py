import sqlite3
import os

conn = None

def initializeDatabase(db_name="database.db"):
    global conn
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS proyek (
        proyek_id INTEGER PRIMARY KEY,
        proyek_nama TEXT NOT NULL,
        proyek_status TEXT NOT NULL,
        proyek_deskripsi TEXT,
        proyek_mulai TEXT,
        proyek_selesai TEXT,
        proyek_budget INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tugas (
        tugas_id INTEGER PRIMARY KEY,
        tugas_nama TEXT NOT NULL,
        tugas_deskripsi TEXT,
        tugas_status TEXT NOT NULL,
        proyek_id INTEGER NOT NULL,
        FOREIGN KEY (proyek_id) REFERENCES proyek (proyek_id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inspirasi (
        inspirasi_id INTEGER PRIMARY KEY,
        inspirasi_nama TEXT NOT NULL,
        inspirasi_deskripsi TEXT,
        inspirasi_gambar BLOB,
        inspirasi_referensi TEXT
    )
    ''')

    conn.commit()
    print("Database initialized successfully.")

def closeDatabase():
    global conn
    if conn:
        conn.close()
        conn = None
        print("Database connection closed.")
    else:
        print("Database not initialized.")

# Proyek Functions

def addProyek(proyek_nama: str, proyek_status: str, proyek_deskripsi:str=None, proyek_mulai:str=None, proyek_selesai:str=None, proyek_budget:int=None):
    global conn
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
    INSERT INTO proyek (proyek_nama, proyek_status, proyek_deskripsi, proyek_mulai, proyek_selesai, proyek_budget)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (proyek_nama, proyek_status, proyek_deskripsi, proyek_mulai, proyek_selesai, proyek_budget))
        conn.commit()
        print(f"Proyek '{proyek_nama}' added successfully.")
    else:
        print("Database not initialized.")

def editProyek(proyek_id:int, proyek_nama:str=None, proyek_status:str=None, proyek_deskripsi:str=None, proyek_mulai:str=None, proyek_selesai:str=None, proyek_budget:int=None):
    global conn
    if conn:
        cursor = conn.cursor()
        boolean = checkProyekId(proyek_id)
        if not boolean:
            print(f"Proyek with ID {proyek_id} not found.")
            return
        query = "UPDATE proyek SET"
        updates = []
        params = []

        if proyek_nama is not None:
            updates.append(" proyek_nama = ?")
            params.append(proyek_nama)
        if proyek_status is not None:
            updates.append(" proyek_status = ?")
            params.append(proyek_status)
        if proyek_deskripsi is not None:
            updates.append(" proyek_deskripsi = ?")
            params.append(proyek_deskripsi)
        if proyek_mulai is not None:
            updates.append(" proyek_mulai = ?")
            params.append(proyek_mulai)
        if proyek_selesai is not None:
            updates.append(" proyek_selesai = ?")
            params.append(proyek_selesai)
        if proyek_budget is not None:
            updates.append(" proyek_budget = ?")
            params.append(proyek_budget)
        
        if updates:
            query += ",".join(updates)
            query += " WHERE proyek_id = ?"
            params.append(proyek_id)
            
            cursor.execute(query, params)
            conn.commit()
            print(f"Proyek with ID {proyek_id} updated successfully.")
        else:
            print("No fields provided to update.")
    else:
        print("Database not initialized.")

def deleteProyek(proyek_id:int):
    global conn
    if conn:
        cursor = conn.cursor()
        boolean = checkProyekId(proyek_id)
        if not boolean:
            print(f"Proyek with ID {proyek_id} not found.")
            return
        cursor.execute("DELETE FROM proyek WHERE proyek_id = ?", (proyek_id,))
        conn.commit()
        print(f"Proyek with ID {proyek_id} deleted successfully.")
    else:
        print("Database not initialized.")

def getAllProyek():
    global conn
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM proyek")
        rows = cursor.fetchall()
        print("All proyek successfully fetched")
        return rows
    else:
        print("Database not initialized.")
        return []

def getProyek(proyek_id:int):
    global conn
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT proyek_nama, proyek_status, proyek_deskripsi, proyek_mulai, proyek_selesai, proyek_budget 
            FROM proyek 
            WHERE proyek_id = ?
        """, (proyek_id,))
        row = cursor.fetchone()
        if row:
            print(f"Proyek with ID {proyek_id} successfully fetched")
            return row
        else:
            print(f"Proyek with ID {proyek_id} not found")
            return False
    else:
        print("Database not initialized.")
        return False

def getProyekWithStatus(proyek_status: str):
    global conn
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM proyek WHERE proyek_status = ?", (proyek_status,))
        rows = cursor.fetchall()
        print(f"All Proyek with status '{proyek_status}' successfully fetched")
        return rows
    else:
        print("Database not initialized.")
        return []

def checkProyekId(proyek_id:int) -> bool:
    row = getProyek(proyek_id)
    return bool(row)

# Tugas Functions

def addTugas(tugas_nama:str, tugas_status:str, proyek_id:int, tugas_deskripsi:str=None):
    global conn
    if conn:
        cursor = conn.cursor()
        
        boolean = checkProyekId(proyek_id)
        if not boolean:
            print(f"Invalid foreign key proyek_id, Tugas '{tugas_nama}' not added.")
            return
        cursor.execute('''
    INSERT INTO tugas (tugas_nama, tugas_deskripsi, tugas_status, proyek_id)
    VALUES (?, ?, ?, ?)
    ''', (tugas_nama, tugas_deskripsi, tugas_status, proyek_id))
        conn.commit()
        print(f"Tugas '{tugas_nama}' added successfully.")
    else:
        print("Database not initialized.")

def editTugas(tugas_id:int, tugas_nama:str=None, tugas_status:str=None, tugas_deskripsi:str=None, proyek_id:int=None):
    global conn
    if conn:
        cursor = conn.cursor()
        boolean = checkTugasId(tugas_id)
        if not boolean:
            print(f"Tugas with ID {tugas_id} not found.")
            return
        query = "UPDATE tugas SET"
        updates = []
        params = []

        if tugas_nama is not None:
            updates.append(" tugas_nama = ?")
            params.append(tugas_nama)
        if tugas_status is not None:
            updates.append(" tugas_status = ?")
            params.append(tugas_status)
        if tugas_deskripsi is not None:
            updates.append(" tugas_deskripsi = ?")
            params.append(tugas_deskripsi)
        if proyek_id is not None:
            boolean = checkProyekId(proyek_id)
            if boolean:
                updates.append(" proyek_id = ?")
                params.append(proyek_id)
            else:
                print(f"Invalid foreign key proyek_id, Tugas with ID '{tugas_id}' not updated.")
                return
        if updates:
            query += ",".join(updates)
            query += " WHERE tugas_id = ?"
            params.append(tugas_id)
            
            cursor.execute(query, params)
            conn.commit()
            print(f"Tugas with ID {tugas_id} updated successfully.")
        else:
            print("No fields provided to update.")
    else:
        print("Database not initialized.")

def deleteTugas(tugas_id:int):
    global conn
    if conn:
        cursor = conn.cursor()
        boolean = checkTugasId(tugas_id)
        if not boolean:
            print(f"Tugas with ID {tugas_id} not found.")
            return
        cursor.execute("DELETE FROM tugas WHERE tugas_id = ?", (tugas_id,))
        conn.commit()
        print(f"Tugas with ID {tugas_id} deleted successfully.")
    else:
        print("Database not initialized.")

def getAllTugas():
    global conn
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tugas")
        rows = cursor.fetchall()
        print("All tugas successfully fetched")
        return rows
    else:
        print("Database not initialized.")
        return []

def getTugasWithProyek(proyek_id:int):
    global conn
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tugas WHERE proyek_id = ?", (proyek_id,))
        rows = cursor.fetchall()
        print(f"All Tugas with proyek ID '{proyek_id}' successfully fetched")
        return rows
    else:
        print("Database not initialized.")
        return []

def getTugas(tugas_id:int):
    global conn
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM tugas WHERE tugas_id = ?", (tugas_id,))
        row = cursor.fetchone()
        if row:
            print(f"Tugas with ID {tugas_id} successfully fetched")
            return row
        else:
            print(f"Tugas with ID {tugas_id} not found")
            return False
    else:
        print("Database not initialized.")
        return False

def checkTugasId(tugas_id:int) -> bool:
    row = getTugas(tugas_id)
    return bool(row)

# Inspirasi Functions

def addInspirasi(nama: str, deskripsi: str, gambar_path: str = None, referensi: str = None):
    global conn
    if conn:
        cursor = conn.cursor()
        if gambar_path and os.path.exists(gambar_path):
            try:
                with open(gambar_path, 'rb') as f:
                    inspirasi_gambar_blob = f.read()
            except Exception as e:
                print(f"Failed to read image: {e}")
                inspirasi_gambar_blob = None
        else:
            inspirasi_gambar_blob = None
        cursor.execute('''
            INSERT INTO inspirasi (inspirasi_nama, inspirasi_deskripsi, inspirasi_gambar, inspirasi_referensi)
            VALUES (?, ?, ?, ?)
        ''', (nama, deskripsi, inspirasi_gambar_blob, referensi))
        conn.commit()
        print(f"Inspirasi '{nama}' added successfully.")
    else:
        print("Database not initialized.")

def getInspirasiById(inspirasi_id:int):
    global conn
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT inspirasi_id, inspirasi_nama, inspirasi_deskripsi, inspirasi_gambar, inspirasi_referensi 
            FROM inspirasi 
            WHERE inspirasi_id = ?
        """, (inspirasi_id,))
        row = cursor.fetchone()
        if row:
            print(f"Inspirasi with ID {inspirasi_id} successfully fetched")
            return row
        else:
            print(f"Inspirasi with ID {inspirasi_id} not found")
            return False
    else:
        print("Database not initialized.")
        return False

def editInspirasi(inspirasi_id:int, inspirasi_nama: str=None, inspirasi_gambar_blob: bytes=None, inspirasi_referensi:str=None, inspirasi_deskripsi:str=None):
    global conn
    if conn:
        cursor = conn.cursor()
        inspirasi = getInspirasiById(inspirasi_id)
        if not inspirasi:
            print(f"Inspirasi with ID {inspirasi_id} not found.")
            return
        updates = []
        params = []

        if inspirasi_nama is not None:
            updates.append("inspirasi_nama = ?")
            params.append(inspirasi_nama)
        if inspirasi_deskripsi is not None:
            updates.append("inspirasi_deskripsi = ?")
            params.append(inspirasi_deskripsi)
        if inspirasi_gambar_blob is not None:
            updates.append("inspirasi_gambar = ?")
            params.append(inspirasi_gambar_blob)
        if inspirasi_referensi is not None:
            updates.append("inspirasi_referensi = ?")
            params.append(inspirasi_referensi)

        if updates:
            query = "UPDATE inspirasi SET " + ", ".join(updates) + " WHERE inspirasi_id = ?"
            params.append(inspirasi_id)
            try:
                cursor.execute(query, params)
                conn.commit()
                print(f"Inspirasi with ID {inspirasi_id} updated successfully.")
            except Exception as e:
                print(f"Failed to update Inspirasi: {e}")
        else:
            print("No fields provided to update.")
    else:
        print("Database not initialized.")

def deleteInspirasi(inspirasi_id:int):
    global conn
    if conn:
        cursor = conn.cursor()
        boolean = checkInspirasiId(inspirasi_id)
        if not boolean:
            print(f"Inspirasi with ID {inspirasi_id} not found.")
            return
        cursor.execute("DELETE FROM inspirasi WHERE inspirasi_id = ?", (inspirasi_id,))
        conn.commit()
        print(f"Inspirasi with ID {inspirasi_id} deleted successfully.")
    else:
        print("Database not initialized.")

def getAllInspirasi():
    global conn
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inspirasi")
        rows = cursor.fetchall()
        print("All inspirasi successfully fetched")
        return rows
    else:
        print("Database not initialized.")
        return []

def checkInspirasiId(inspirasi_id:int) -> bool:
    row = getInspirasiById(inspirasi_id)
    return bool(row)

def migrateInspirasiTableToBlob():
    global conn
    if not conn:
        print("Database not initialized.")
        return
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(inspirasi)")
    columns = cursor.fetchall()
    column_types = {col[1]: col[2].upper() for col in columns}
    if column_types.get('INSPIRASI_GAMBAR') == 'BLOB':
        print("'inspirasi_gambar' is already BLOB. Migration not required.")
        return
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspirasi_new (
            inspirasi_id INTEGER PRIMARY KEY,
            inspirasi_nama TEXT NOT NULL,
            inspirasi_deskripsi TEXT,
            inspirasi_gambar BLOB,
            inspirasi_referensi TEXT
        )
    ''')

    cursor.execute('SELECT inspirasi_id, inspirasi_nama, inspirasi_deskripsi, inspirasi_gambar, inspirasi_referensi FROM inspirasi')
    all_inspirasi = cursor.fetchall()
    
    for inspirasi in all_inspirasi:
        inspirasi_id, inspirasi_nama, inspirasi_deskripsi, inspirasi_gambar_path, inspirasi_referensi = inspirasi
        if inspirasi_gambar_path and os.path.exists(inspirasi_gambar_path):
            try:
                with open(inspirasi_gambar_path, 'rb') as f:
                    inspirasi_gambar_blob = f.read()
            except Exception as e:
                inspirasi_gambar_blob = None
                print(f"Failed to read image for inspirasi_id {inspirasi_id}: {e}")
        else:
            inspirasi_gambar_blob = None
        cursor.execute('''
            INSERT INTO inspirasi_new (inspirasi_id, inspirasi_nama, inspirasi_deskripsi, inspirasi_gambar, inspirasi_referensi)
            VALUES (?, ?, ?, ?, ?)
        ''', (inspirasi_id, inspirasi_nama, inspirasi_deskripsi, inspirasi_gambar_blob, inspirasi_referensi))
    
    cursor.execute('DROP TABLE inspirasi')
    cursor.execute('ALTER TABLE inspirasi_new RENAME TO inspirasi')
    conn.commit()
    print("Migrated 'inspirasi' table to store images as BLOBs.")

def deleteAllData():
    global conn
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inspirasi")
        cursor.execute("DELETE FROM tugas")
        cursor.execute("DELETE FROM proyek")
        conn.commit()
        print("All data from inspirasi, tugas, and proyek tables have been deleted.")
    else:
        print("Database not initialized.")

if __name__ == "__main__":
    initializeDatabase()
    migrateInspirasiTableToBlob()
    closeDatabase()
