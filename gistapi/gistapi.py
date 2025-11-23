"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

GitHub provides the Gist service as a pastebin analog for sharing code and
other development artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given GitHub account.
"""

import requests
from flask import Flask, jsonify, request
import re

app = Flask(__name__)


@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


def gists_for_user(username: str):
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

def gist_for_gist_id(gist_id: str):
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

def search_pattern_in_gist_file(content_url : str, pattern : str):
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
    username = post_data.get("username")
    pattern = post_data.get("pattern")

    if not username or not isinstance(username, str) :
        return jsonify({"error": "The 'username' is a required field and must be a string"}), 400

    if not pattern or not isinstance(pattern, str):
        return jsonify({"error": "The 'pattern' is a required field and must be a string"}), 400

    result = {}
    matches = []
    try:
        gists = gists_for_user(username)
        for gist in gists:
            gist_id = gist.get("id")
            gist_info = gist_for_gist_id(gist_id)
            for file_name, file_info in gist_info.get("files").items():
                match = {}
                if file_info.get("truncated"):
                    if search_pattern_in_gist_file(content_url = file_info.get("raw_url"), pattern = pattern):
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
