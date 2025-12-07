"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

GitHub provides the Gist service as a pastebin analog for sharing code and
other development artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given GitHub account.
"""

from flask import Flask, jsonify, request
import re
from .helpers import Database, GithubAPIRepository, DBRepository

app = Flask(__name__)
db = Database("dbname='gitgists' user='souvik' host='localhost' password=''") # will move this later
github_api_repo = GithubAPIRepository()
db_repo = DBRepository(db = db)

@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"

@app.route("/api/v1/search", methods=['POST'])
def search():
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    post_data = request.get_json()

    # Some basic data validation of the incoming request payload
    username = post_data.get("username").strip()
    pattern = post_data.get("pattern")

    if not username or not isinstance(username, str) :
        return jsonify({"error": "The 'username' is a required field and must be a string"}), 400

    if not pattern or not isinstance(pattern, str):
        return jsonify({"error": "The 'pattern' is a required field and must be a string"}), 400

    result = {}
    matches = []
    try:

        # try DB lookup first
        if db_repo.user_in_db(username):
            user_id = db_repo.userid_for_username_from_db(username)
            matches = db_repo.find_matching_gists_for_user_id_and_pattern(user_id, pattern)
        else :
            gists = github_api_repo.gists_for_user(username)
            for gist in gists:
                gist_id = gist.get("id")
                gist_info = github_api_repo.gist_for_gist_id(gist_id)
                for file_name, file_info in gist_info.get("files").items():
                    match = {}
                    if file_info.get("truncated"):
                        if github_api_repo.search_pattern_in_gist_file(content_url = file_info.get("raw_url"), pattern = pattern):
                            match['gist_id'] = gist_id
                            match['file_name'] = file_name
                            match['gist_content'] = 'Gist truncated - file too large'
                            matches.append(match)

                    else:
                        content = file_info.get("content")
                        if re.search(pattern, content):
                            match['gist_id'] = gist_id
                            match['file_name'] = file_name
                            match['gist_content'] = content
                            matches.append(match)

        result['status'] = 'success'
        result['username'] = username
        result['pattern'] = pattern
        # Paginate the matches
        per_page = 10
        result['total_pages'] = len(matches) // per_page + 1
        page = post_data.get('page')
        if page is not None:
            start = (page - 1) * per_page
            end = start + per_page
            result['matches'] = matches[start:end]
            result['page'] = page
        else:
            result['matches'] = matches[:per_page]
            result['page'] = 1

    except Exception as e:
        return jsonify({"error": str(e)}), 502
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9876)
