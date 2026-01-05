import requests
import re
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

class Database:
    def __init__(self, dsn: str):
        """Initializes the database connection
            Args:
                dsn (string): the database connection string
        """
        self.engine = create_engine(dsn)

    def fetch_all(self, sql: str, params=None):
        """ Runs a query and fetches query results from the database
        Args:
            sql (string): the SQL query,
            params (dict / None): the SQL query parameters
        Returns:
            the row(s) from the database query
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), params)
                rows = result.all()

        except SQLAlchemyError as error:
            print("Database error:", error)

        return rows

class GithubAPIRepository:
    def __init__(self) :
        """Initializes the GithubAPIRepository class"""

    def gists_for_user(self, username: str) -> dict:
        """Provides the list of gist metadata for a given user.

        This abstracts the /users/:username/gist endpoint from the GitHub API.
        See https://developer.github.com/v3/gists/#list-a-users-gists for
        more information.

        Args:
            username (string): the user to query gists for

        Returns:
            The dict parsed from the json response from the GitHub API.  See
            the above URL for details of the expected structure.
        """
        gists_url = 'https://api.github.com/users/{username}/gists'.format(username=username)
        try:
            response = requests.get(gists_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"API call failed to {gists_url} with error : {str(e)}")

    def gist_for_gist_id(self, gist_id: str) -> dict:
        """Provides the gist object for a given gist id.

        This abstracts the /gists/:gist_id endpoint from the GitHub API.
        See https://docs.github.com/en/rest/gists/gists?apiVersion=2022-11-28#get-a-gist for
        more information

        Args:
            gist_id (string): the gist ID to query the specific gist for

        Returns:
            The dict parsed from the json response from the GitHub API.  See
            the above URL for details of the expected structure.
        """
        gists_url = 'https://api.github.com/gists/{gist_id}'.format(gist_id=gist_id)
        try:
            response = requests.get(gists_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"API call failed to {gists_url} with error : {str(e)}")

    def search_pattern_in_gist_file(self, content_url : str, pattern : str) -> bool:
        """Searches for the pattern in the gist content from the url

        This streams an HTTP GET response to the given URL of a Gist file
        and checks if the pattern is present
        Args:
            content_url (string) : the url of the gist file content
            pattern (string) : the pattern to search for in the gist file content
        Returns:
            True if pattern is present in gist file, False otherwise
        """
        try:
            with requests.get(content_url, stream=True) as response:
                response.raise_for_status()
                pattern_bytes = pattern.encode("utf-8")
                pattern_regex = re.compile(pattern_bytes) # pattern bytes -> regex object
                buffer = b""
                pattern_len = len(pattern_bytes)
                for chunk in response.iter_content(chunk_size=1024):
                    chunk_with_buffer = buffer + chunk
                    if re.search(pattern_regex, chunk_with_buffer):
                        return True
                    buffer = chunk_with_buffer[-pattern_len:]
            return False
        except Exception as e:
            raise Exception(f"API call failed to {content_url} with error : {str(e)}")

class DBRepository:
    def __init__(self, db: Database) :
        """Initializes the DBRepository class"""
        self.db = db

    def user_in_db(self, username : str) -> bool:
        """Searches for the username in the users table in the database

        This queries the db table users and checks if the username is present
        Args:
            db (Database) : the database object to query the username for,
            username (string) : the username to search for
        Returns:
            True if username is present in database, False otherwise
        """
        (user_exists,) = self.db.fetch_all("SELECT EXISTS(SELECT 1 FROM users WHERE user_name= :username)", {"username": username })[0]
        return user_exists

    def userid_for_username_from_db(self, username : str) :
        """Searches for the user_name, the user id from the users table in the database

        This queries the db table users and returns the user_id for the given username
        Args:
            db (Database) : the database object to query the username for,
            username (string) : the username to search for
        Returns:
            The user_id for the given username
        """
        user_ids = self.db.fetch_all("SELECT id FROM users WHERE user_name= :username", {"username": username })
        if len(user_ids) > 0:
            return user_ids[0][0]
        else:
            return None

    def find_matching_gists_for_user_id_and_pattern(self, user_id: int, pattern: str) -> list:
        """Searches for the pattern among the gists contents for the given user_id

        This queries the db table gists and returns the list of matched gists for the given pattern
        Args:
            db (Database) : the database object to query the username for,
            user_id (int) : the user id to search for gists
            pattern (string) : the pattern to search for in the gists content
        Returns:
            List of matched gists for the given pattern and user id
        """
        contents = [gist_content for (gist_content,) in self.db.fetch_all("SELECT content FROM gists WHERE user_id = :user_id AND content ~ :content", {"user_id":user_id, "content":pattern})]
        return contents