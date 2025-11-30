import psycopg2

try:
    conn = psycopg2.connect("dbname='gitgists' user='souvik' host='localhost' password=''")
except:
    print("I am unable to connect to the database")


with conn.cursor() as curs:
    try:
        curs.execute("SELECT version()")
        print("You are connected to - ", curs.fetchone()[0])

        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_name TEXT NOT NULL
        );
        """
        curs.execute(create_users_table)
        print("Created users table")

        create_gists_table = """
        CREATE TABLE IF NOT EXISTS gists (
        id UUID PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
        gist_url TEXT NOT NULL,
        content TEXT
        );
        """
        curs.execute(create_gists_table)
        print("Created gists table")

        conn.commit()
        print("Tables created successfully")

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        print(error)

    finally:
        curs.close()
        conn.close()