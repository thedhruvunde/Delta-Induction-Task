import yaml
import psycopg2

# DB config
DB_PARAMS = {
    'dbname': 'blogdb',
    'user': 'postgres',
    'password': 'yourpassword',
    'host': 'localhost',
    'port': 5432
}

# YAML path
YAML_PATH = "/mnt/data/users.yaml"  # Adjust if needed

def connect_db():
    return psycopg2.connect(**DB_PARAMS)

def create_users_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

def insert_user(cursor, username):
    cursor.execute("""
        INSERT INTO users (username)
        VALUES (%s)
        ON CONFLICT (username) DO NOTHING;
    """, (username,))

def extract_usernames(yaml_data):
    usernames = []

    for section in ["users", "authors", "admins"]:
        if section in yaml_data:
            usernames.extend([entry["username"] for entry in yaml_data[section]])

    return usernames

def main():
    with open(YAML_PATH, "r") as f:
        data = yaml.safe_load(f)

    usernames = extract_usernames(data)

    conn = connect_db()
    cur = conn.cursor()

    create_users_table(cur)

    for username in usernames:
        insert_user(cur, username)
        print(f"✅ Inserted: {username}")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
