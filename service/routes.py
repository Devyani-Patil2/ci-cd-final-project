
"""
Controller for routes
"""
from flask import jsonify, url_for, abort, request
from service import app
from service.common import status

COUNTER = {}
ACCOUNTS = {}


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


############################################################
# Index page
############################################################
@app.route("/")
def index():
    """Returns information about the service"""
    app.logger.info("Request for Base URL")
    return jsonify(
        status=status.HTTP_200_OK,
        message="Accounts Service",
        version="1.0.0",
        url=url_for("list_accounts", _external=True),
    )


############################################################
# Account CREATE endpoint
############################################################
@app.route("/accounts", methods=["POST"])
def create_account():
    """Creates a new account"""
    account_data = request.get_json()

    if not account_data:
        return abort(status.HTTP_400_BAD_REQUEST, "Missing account data")

    if "name" not in account_data:
        return abort(status.HTTP_400_BAD_REQUEST, "Missing account name")

    account_id = str(account_data.get("id", len(ACCOUNTS) + 1))

    if account_id in ACCOUNTS:
        return abort(status.HTTP_409_CONFLICT, "Account already exists")

    account = {
        "id": account_id,
        "name": account_data["name"],
        "email": account_data.get("email", ""),
    }

    ACCOUNTS[account_id] = account

    location_url = url_for(
        "read_account", account_id=account_id, _external=True
    )

    return (
        jsonify(account),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


############################################################
# Account LIST endpoint
############################################################
@app.route("/accounts", methods=["GET"])
def list_accounts():
    """Lists all accounts"""
    accounts = list(ACCOUNTS.values())
    return jsonify(accounts), status.HTTP_200_OK


############################################################
# Account READ endpoint
############################################################
@app.route("/accounts/<account_id>", methods=["GET"])
def read_account(account_id):
    """Reads a single account"""
    if account_id not in ACCOUNTS:
        return abort(
            status.HTTP_404_NOT_FOUND,
            "Account does not exist",
        )

    return jsonify(ACCOUNTS[account_id]), status.HTTP_200_OK


############################################################
# Account UPDATE endpoint
############################################################
@app.route("/accounts/<account_id>", methods=["PUT"])
def update_account(account_id):
    """Updates an existing account"""
    if account_id not in ACCOUNTS:
        return abort(
            status.HTTP_404_NOT_FOUND,
            "Account does not exist",
        )

    account_data = request.get_json()

    if not account_data:
        return abort(
            status.HTTP_400_BAD_REQUEST,
            "Missing account data",
        )

    if "name" in account_data:
        ACCOUNTS[account_id]["name"] = account_data["name"]

    if "email" in account_data:
        ACCOUNTS[account_id]["email"] = account_data["email"]

    return jsonify(ACCOUNTS[account_id]), status.HTTP_200_OK


############################################################
# Existing Counter endpoints
############################################################
@app.route("/counters", methods=["GET"])
def list_counters():
    """Lists all counters"""
    counters = [
        dict(name=count[0], counter=count[1])
        for count in COUNTER.items()
    ]
    return jsonify(counters)


@app.route("/counters/<name>", methods=["POST"])
def create_counters(name):
    """Creates a new counter"""
    if name in COUNTER:
        return abort(
            status.HTTP_409_CONFLICT,
            f"Counter {name} already exists",
        )

    COUNTER[name] = 0

    location_url = url_for(
        "read_counters", name=name, _external=True
    )

    return (
        jsonify(name=name, counter=0),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


@app.route("/counters/<name>", methods=["GET"])
def read_counters(name):
    """Reads a single counter"""
    if name not in COUNTER:
        return abort(
            status.HTTP_404_NOT_FOUND,
            f"Counter {name} does not exist",
        )

    return jsonify(name=name, counter=COUNTER[name])


@app.route("/counters/<name>", methods=["PUT"])
def update_counters(name):
    """Updates a counter"""
    if name not in COUNTER:
        return abort(
            status.HTTP_404_NOT_FOUND,
            f"Counter {name} does not exist",
        )

    COUNTER[name] += 1
    return jsonify(name=name, counter=COUNTER[name])


@app.route("/counters/<name>", methods=["DELETE"])
def delete_counters(name):
    """Deletes a counter"""
    if name in COUNTER:
        COUNTER.pop(name)

    return "", status.HTTP_204_NO_CONTENT


############################################################
# Utility for testing
############################################################
def reset_counters():
    """Removes all counters while testing"""
    global COUNTER  # pylint: disable=global-statement

    if app.testing:
        COUNTER = {}
        ACCOUNTS.clear()
