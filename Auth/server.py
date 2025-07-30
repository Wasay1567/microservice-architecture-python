from flask import Flask, request
import os
import psycopg2
from hash import check_password
import jwt
from datetime import datetime, timedelta
import datetime
from hash import hash_password
from uuid import uuid4

app = Flask(__name__)

def get_db():
    POSTGRESS_URI = f"postgresql://:{os.environ.get('POSTGRES_USER')}@{os.environ.get('POSTGRES_PASS')}:5432/{os.environ.get('POSTGRES_DB')}"
    con = psycopg2.connect(POSTGRESS_URI)
    return con


@app.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401
    
    con = get_db()
    cur = con.cursor()
    res = cur.execute("SELECT * FROM Users where email=%s", (auth.username))
    if res > 0:
        user_row = cur.fetchone()
        if not user_row:
            return "invalid credentials", 401
        id = user_row[0]
        email = user_row[1]
        if auth.username != email or not check_password(auth.password, user_row[2]):
            return "invalid credentials", 401
        else:
            return jwt.encode(payload={
                "sub": id,
                "email": email,
                "is_admin": user_row[3],
                "exp": datetime.utcnow() + timedelta(days=1)
            }, key=os.environ.get("JWT_SECRET"), algorithm="HS256"), 200
    else:
        return "invalid credentials", 401
        

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return "missing credentials", 400

    email = data["email"]
    password = data["password"]

    hashed_password = hash_password(password)

    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO Users (id, email, password, is_admin) VALUES (%s, %s, %s, %s) RETURNING id", (uuid4(), email, hashed_password, False))
        user_id = cur.fetchone()[0]
        con.commit()
    except psycopg2.errors.UniqueViolation:
        con.rollback()
        return "user already exists", 409
    except Exception as e:
        con.rollback()
        return "registration failed", 500
    finally:
        cur.close()
        con.close()

    return {"id": user_id, "email": email, "is_admin": False}, 201


@app.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers.get("Authorization")
    if not encoded_jwt:
        return "missing jwt", 401
    try:
        decoded = jwt.decode(jwt=encoded_jwt.split(" ")[1], 
                    algorithms=["HS256"], 
                    key=os.environ.get("JWT_SECRET"))
        return decoded, 200

    except:
        return "not authorized", 403
    

@app.route("/health", methods=["GET"])
def health():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
