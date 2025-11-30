import requests
import psycopg2

# to not get rate-limited please generate a PAT with public_repo scope from https://github.com/settings/tokens and paste it here
headers = {'Authorization' : 'Bearer your_token_here'}
users = requests.get('https://api.github.com/users', headers=headers).json()

try:
    conn = psycopg2.connect("dbname='gitgists' user='souvik' host='localhost' password=''")
except:
    print("I am unable to connect to the database")


with conn.cursor() as curs:
    try:
        curs.execute("SELECT version()")
        print("You are connected to - ", curs.fetchone()[0])

        user_tuples = []
        gists_tuples = []
        for user in users[:15]:

            user_id = user.get('id')
            user_name = user.get('login')
            user_tuple = (user_id, user_name)
            user_tuples.append(user_tuple)

            gists = requests.get('https://api.github.com/users/{username}/gists'.format(username=user_name), headers=headers).json()

            for gist in gists:

                gist_id = gist.get('id')
                gist_url = gist.get('url')
                gist_info = requests.get(gist_url, headers=headers).json()

                for filename, file_info in gist_info.get('files').items():

                    if not file_info.get('truncated'):
                        content = file_info.get('content')
                    else:
                        content = requests.get(file_info.get('raw_url'), headers=headers).text

                gists_tuple = (gist_id, user_id, gist_url, content.replace('\x00', ''))
                gists_tuples.append(gists_tuple)

        curs.executemany("INSERT INTO users (id, user_name) VALUES (%s, %s)", user_tuples)
        curs.executemany("INSERT INTO gists(id, user_id, gist_url, content) VALUES(%s,%s,%s,%s)", gists_tuples)

        conn.commit()
        print("Records created successfully")

    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        print(error)

    finally:
        curs.close()
        conn.close()