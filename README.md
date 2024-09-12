# Ping Pong Checker

This script is used to check if the pong bot has emmited a pong event for all the pings. This is part of the exercices that a candidate has to solve during the Kleros interviews.

# How to use it
## Preparation
- Define the RPC environmental variable in the .env file.
- Create a virtual env with `python3 -m venv .venv`
- Activate the venv: `source .venv/bin/activate`
- install dependencies: `pip3 install -r requirements.txt`

## Run
Set up the bot address of the `candidate_bot` and the `candidate_starting_block` in the `main.py` file.
Run the main.py with `python3 main.py`

All the logs are stored in the logs folder with the name of the candidate_bot address. Also are streamed to the console.
