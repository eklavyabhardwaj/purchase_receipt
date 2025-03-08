import psycopg2

db_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'admin@123'
}

def create_table():
    conn = None 
    cursor = None
    try:
        # Establish connection
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Check if the table exists
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'purchase_reciept_batch');"
        )
        table_exists = cursor.fetchone()[0]

        if table_exists:
            print("Table 'purchase_reciept_batch' already exists.")
        else:
            print("Table 'purchase_reciept_batch' does not exist. Creating...")
            # Create table if not exists
            create_table_query = """
            CREATE TABLE IF NOT EXISTS purchase_reciept_batch (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                item_name VARCHAR(255),
                child_name VARCHAR(255),
                eipl_unique_batch_code VARCHAR(255) UNIQUE
            );
            """
            cursor.execute(create_table_query)
            conn.commit()
            print("Table 'purchase_reciept_batch' created successfully.")

    except psycopg2.Error as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()  # Rollback the transaction if an error occurred
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_table()
