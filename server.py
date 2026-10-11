from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import os

from app import (
    generate_sql,
    execute_sql,
    generate_answer,
    fix_sql
)

from sql_validator import validate_sql
from schema import JOIN_RELATIONSHIPS

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "development-key-change-before-deployment"
)

CORS(app)


# ---------------- LOGIN PAGE ----------------

@app.route("/")
def home():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    return render_template("login.html")


# ---------------- LOGIN API ----------------

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    # Demo credentials
    if username == "admin" and password == "admin123":

        session["logged_in"] = True
        session["username"] = username

        return jsonify({
            "success": True,
            "redirect": url_for("dashboard")
        })

    return jsonify({
        "success": False,
        "error": "Invalid username or password."
    }), 401


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if not session.get("logged_in"):
        return redirect(url_for("home"))

    return render_template(
        "dashboard.html",
        username=session.get("username", "User")
    )


# ---------------- LOGOUT ----------------

@app.route("/api/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "redirect": url_for("home")
    })


# ---------------- DATABASE STATUS ----------------

@app.route("/api/status")
def database_status():

    if not session.get("logged_in"):
        return jsonify({
            "success": False,
            "error": "Please log in."
        }), 401

    return jsonify({
        "success": True,
        "message": "AI API is running"
    })


# ---------------- DATABASE QUERY API ----------------

@app.route("/api/query", methods=["POST"])
def query_database():

    if not session.get("logged_in"):
        return jsonify({
            "success": False,
            "error": "Please log in first."
        }), 401

    try:

        data = request.get_json(silent=True) or {}
        question = data.get("question", "").strip()

        if not question:
            return jsonify({
                "success": False,
                "error": "Please enter a question."
            }), 400

        # Generate SQL
        sql, relevant_schema = generate_sql(question)

        # Validate SQL
        is_valid, validation_message = validate_sql(sql)

        if not is_valid:
            return jsonify({
                "success": False,
                "sql": sql,
                "validation": validation_message,
                "error": "SQL validation failed."
            }), 400

        # Execute SQL
        results, error = execute_sql(sql)

        # Attempt correction if execution fails
        if error:

            fixed_sql = fix_sql(
                sql,
                error,
                question,
                relevant_schema,
                JOIN_RELATIONSHIPS
            )

            fixed_valid, fixed_message = validate_sql(fixed_sql)

            if not fixed_valid:
                return jsonify({
                    "success": False,
                    "sql": fixed_sql,
                    "validation": fixed_message,
                    "error": "Corrected SQL failed validation."
                }), 400

            results, error = execute_sql(fixed_sql)

            if error:
                return jsonify({
                    "success": False,
                    "sql": fixed_sql,
                    "error": error
                }), 500

            sql = fixed_sql

        # Generate natural-language answer
        answer = generate_answer(question, results)

        # Return results
        formatted_results = [
            list(row) for row in results
        ]

        return jsonify({
            "success": True,
            "question": question,
            "sql": sql,
            "validation": "SQL validated successfully.",
            "answer": answer,
            "results": formatted_results,
            "row_count": len(formatted_results)
        })

    except Exception as e:

        app.logger.exception("Database query failed")

        return jsonify({
            "success": False,
            "error": "An unexpected error occurred. Check the server terminal."
        }), 500


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )