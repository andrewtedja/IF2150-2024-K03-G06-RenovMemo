import sqlite3
import os
import threading

db_lock = threading.Lock()
conn = None

def initializeDatabase(db_name="database.db"):
    global conn
    conn = sqlite3.connect(db_name, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS proyek (
        proyek_id INTEGER PRIMARY KEY,
        proyek_nama TEXT NOT NULL,
        proyek_status TEXT NOT NULL,
        proyek_deskripsi TEXT,
        proyek_mulai TEXT,
        proyek_selesai TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tugas (
        tugas_id INTEGER PRIMARY KEY,
        tugas_nama TEXT NOT NULL,
        tugas_deskripsi TEXT,
        tugas_status TEXT NOT NULL,
        proyek_id INTEGER NOT NULL,
        budget INTEGER DEFAULT 0,
        estimated INTEGER DEFAULT 0,
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

def addProyek(proyek_nama: str, proyek_status: str, proyek_deskripsi: str = None, proyek_mulai: str = None, proyek_selesai: str = None):
    global conn
    if conn:
        try:
            cursor = conn.cursor()
            print(f"Starting INSERT for proyek: {proyek_nama}")
            cursor.execute('''
            INSERT INTO proyek (proyek_nama, proyek_status, proyek_deskripsi, proyek_mulai, proyek_selesai)
            VALUES (?, ?, ?, ?, ?)
            ''', (proyek_nama, proyek_status, proyek_deskripsi, proyek_mulai, proyek_selesai))
            conn.commit()
            print(f"Proyek '{proyek_nama}' added successfully.")
        except Exception as e:
            print(f"Error while adding proyek: {e}")
    else:
        print("Database not initialized.")


def editProyek(proyek_id:int, proyek_nama:str=None, proyek_status:str=None, proyek_deskripsi:str=None, proyek_mulai:str=None, proyek_selesai:str=None):
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
        
        if updates:
            query += ",".join(updates)
            query += " WHERE proyek_id = ?"
            params.append(proyek_id)
            
            try:
                cursor.execute(query, params)
                conn.commit()
                print(f"Proyek with ID {proyek_id} updated successfully.")
            except Exception as e:
                print(f"Error while updating proyek: {e}")
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
        try:
            cursor.execute("DELETE FROM proyek WHERE proyek_id = ?", (proyek_id,))
            conn.commit()
            print(f"Proyek with ID {proyek_id} deleted successfully.")
        except Exception as e:
            print(f"Error while deleting proyek: {e}")
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
            SELECT proyek_nama, proyek_status, proyek_deskripsi, proyek_mulai, proyek_selesai 
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


def migrateProyekTable():
    global conn
    if not conn:
        print("Database not initialized.")
        return
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(proyek)")
    columns = cursor.fetchall()
    existing_columns = [col[1].lower() for col in columns]

    if 'budget' not in existing_columns:
        print("'proyek' table does not have 'budget' column. No migration required.")
        return

    print("Migrating 'proyek' table: Removing 'budget' field.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proyek_new (
            proyek_id INTEGER PRIMARY KEY,
            proyek_nama TEXT NOT NULL,
            proyek_status TEXT NOT NULL,
            proyek_deskripsi TEXT,
            proyek_mulai TEXT,
            proyek_selesai TEXT
        )
    ''')

    cursor.execute('''
        INSERT INTO proyek_new (proyek_id, proyek_nama, proyek_status, proyek_deskripsi, proyek_mulai, proyek_selesai)
        SELECT proyek_id, proyek_nama, proyek_status, proyek_deskripsi, proyek_mulai, proyek_selesai
        FROM proyek
    ''')

    cursor.execute("DROP TABLE proyek")
    cursor.execute("ALTER TABLE proyek_new RENAME TO proyek")

    conn.commit()
    print("Migration of 'proyek' table completed successfully.")

# Tugas Functions

def addTugas(tugas_nama:str, tugas_status:str, proyek_id:int, tugas_deskripsi:str=None, budget: int = 0, estimated: int = 0):
    global conn
    if conn:
        cursor = conn.cursor()
        
        boolean = checkProyekId(proyek_id)
        if not boolean:
            print(f"Invalid foreign key proyek_id, Tugas '{tugas_nama}' not added.")
            return
        try:
            cursor.execute('''
                INSERT INTO tugas (tugas_nama, tugas_deskripsi, tugas_status, proyek_id, budget, estimated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tugas_nama, tugas_deskripsi, tugas_status, proyek_id, budget, estimated))
            conn.commit()
            print(f"Tugas '{tugas_nama}' added successfully.")
        except Exception as e:
            print(f"Error while adding tugas: {e}")
    else:
        print("Database not initialized.")

def editTugas(tugas_id:int, tugas_nama:str=None, tugas_status:str=None, tugas_deskripsi:str=None, proyek_id:int=None, budget: int = None, estimated: int = None):
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
        if budget is not None:
            updates.append(" budget = ?")
            params.append(budget)
        if estimated is not None:
            updates.append(" estimated = ?")
            params.append(estimated)
        
        if updates:
            query += ",".join(updates)
            query += " WHERE tugas_id = ?"
            params.append(tugas_id)
            
            try:
                cursor.execute(query, params)
                conn.commit()
                print(f"Tugas with ID {tugas_id} updated successfully.")
            except Exception as e:
                print(f"Error while updating tugas: {e}")
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
        try:
            cursor.execute("DELETE FROM tugas WHERE tugas_id = ?", (tugas_id,))
            conn.commit()
            print(f"Tugas with ID {tugas_id} deleted successfully.")
        except Exception as e:
            print(f"Error while deleting tugas: {e}")
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

def addInspirasi(nama: str, deskripsi: str, gambar_data: bytes = None, referensi: str = None):
    global conn
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO inspirasi (inspirasi_nama, inspirasi_deskripsi, inspirasi_gambar, inspirasi_referensi)
                VALUES (?, ?, ?, ?)
            ''', (nama, deskripsi, gambar_data, referensi))
            conn.commit()
            print(f"Inspirasi '{nama}' added successfully.")
        except Exception as e:
            print(f"Error while adding inspirasi: {e}")
    else:
        print("Database not initialized.")

def getInspirasiById(inspirasi_id: int):
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
        try:
            cursor.execute("DELETE FROM inspirasi WHERE inspirasi_id = ?", (inspirasi_id,))
            conn.commit()
            print(f"Inspirasi with ID {inspirasi_id} deleted successfully.")
        except Exception as e:
            print(f"Error while deleting inspirasi: {e}")
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
        try:
            cursor.execute("DELETE FROM inspirasi")
            cursor.execute("DELETE FROM tugas")
            cursor.execute("DELETE FROM proyek")
            conn.commit()
            print("All data from inspirasi, tugas, and proyek tables have been deleted.")
        except Exception as e:
            print(f"Error while deleting all data: {e}")
    else:
        print("Database not initialized.")

def migrateTugasTable():
    global conn
    if not conn:
        print("Database not initialized.")
        return
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(tugas)")
    columns = cursor.fetchall()
    existing_columns = [col[1].lower() for col in columns]

    if 'budget' not in existing_columns:
        print("Adding 'budget' column to 'tugas' table.")
        try:
            cursor.execute("ALTER TABLE tugas ADD COLUMN budget INTEGER DEFAULT 0")
        except Exception as e:
            print(f"Error while adding 'budget' column: {e}")
    else:
        print("'budget' column already exists in 'tugas' table.")

    if 'estimated' not in existing_columns:
        print("Adding 'estimated' column to 'tugas' table.")
        try:
            cursor.execute("ALTER TABLE tugas ADD COLUMN estimated INTEGER DEFAULT 0")
        except Exception as e:
            print(f"Error while adding 'estimated' column: {e}")
    else:
        print("'estimated' column already exists in 'tugas' table.")

    conn.commit()
    print("Migration of 'tugas' table completed successfully.")

if __name__ == "__main__":
    initializeDatabase()
    migrateProyekTable()
    migrateTugasTable()
    migrateInspirasiTableToBlob()
    closeDatabase()
