# Documentation

## Requirements

- `Python 3.12` (tested) [python installation guide](https://docs.python.org/3/using/unix.html)
- `Docker 24.0.2` (tested) [docker installation guide](https://docs.docker.com/engine/install/)


## Usage

1. Clone the git repo :

```bash
git clone https://github.com/svkmdl/backend-coding-challenge.git
cd backend-coding-challenge
```

2. Run directly as flask app or in the docker container

Run as a flask app:
```bash
pip3 install -e .
python3 -m gistapi.gistapi
```

Build and run the docker container:
```bash
docker build -t gistapi:0.1 .
docker run --rm -p 9876:9876 gistapi:0.1
```

3. Requesting endpoints

Ping check
```bash
curl --location 'http://127.0.0.1:9876/ping'
```

Search for pattern in gist
```bash
curl --location 'http://127.0.0.1:9876/api/v1/search' \
--header 'Content-Type: application/json' \
--data '{
    "username" : "maneetgoyal",
    "pattern" : "KOLKATA"
}'
```

## Development

Install dependencies
```bash
pip3 install -e .
```

Code analysis using Qodana

1. Install Qodana CLI (make sure user has permissions to move into `/usr/local/bin`)
```bash
curl -fsSL https://jb.gg/qodana-cli/install | sudo bash
```
2. Scan the code using Qodana
```bash
qodana scan --config qodana.yaml --image jetbrains/qodana-python-community:2025.2
```

Run tests
```bash
python3 tests/test_gistapi.py
```

Setup Postgres (tested on version`14.20`) [postgres installation guide](https://wiki.postgresql.org/wiki/Homebrew)

1. Log into the Postgres CLI
```bash
psql postgres
```

2. (Using Postgres CLI) Create Database
```bash
CREATE DATABASE gitgists;
```

3. (Back to terminal again) Create Tables and Populate them
```bash
python3 gistapi/setup_postgres.py
python3 gistapi/populate_tables.py
```