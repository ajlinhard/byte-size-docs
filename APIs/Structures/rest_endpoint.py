"""REST endpoint example — the client asks, the server answers, done.

    pip install flask requests
    python rest_endpoint.py        # starts the server on port 5000

An endpoint is just a URL the server exposes. The client decides when to
call it; the server responds once; then the exchange is over.
"""
from flask import Flask, request, jsonify

app = Flask(__name__)

users = {1: {"name": "Ada"}, 2: {"name": "Alan"}}   # in-memory "database"


@app.get("/users/<int:user_id>")     # an endpoint: read a user
def get_user(user_id):
    user = users.get(user_id)
    if user is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(user)              # server responds, then it's done


@app.post("/users")                   # another endpoint: create a user
def create_user():
    data = request.get_json()
    new_id = max(users) + 1
    users[new_id] = {"name": data["name"]}
    return jsonify({"id": new_id, **users[new_id]}), 201


if __name__ == "__main__":
    app.run(port=5000)


# ---- client side: you initiate every call ----
# import requests
# requests.get("http://localhost:5000/users/1").json()
#     -> {"name": "Ada"}
# requests.post("http://localhost:5000/users", json={"name": "Grace"}).json()
#     -> {"id": 3, "name": "Grace"}
