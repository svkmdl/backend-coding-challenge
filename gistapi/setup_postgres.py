import psycopg2

try:
    conn = psycopg2.connect("dbname='gitgists' user='souvik' host='localhost' password=''")
except:
    print("I am unable to connect to the database")


with conn.cursor() as curs:
    try:
        curs.execute("SELECT version()")
        print("You are connected to - ", curs.fetchone()[0])
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)