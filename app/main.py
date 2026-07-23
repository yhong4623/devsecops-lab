from flask import Flask, request, jsonify
from app.database import get_user, init_db
import ast
import sqlite3

app = Flask(__name__)


def safe_eval(expr: str):
    """Evaluate only safe Python literals and basic arithmetic expressions."""
    node = ast.parse(expr, mode="eval")

    allowed_nodes = {
        ast.Expression,
        ast.Constant,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Load,
        ast.Tuple,
        ast.List,
    }

    for child in ast.walk(node):
        if type(child) not in allowed_nodes:
            raise ValueError("expression contains unsafe operations")

    return eval(compile(node, filename="<ast>", mode="eval"), {"__builtins__": {}}, {})


@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "devsecops-lab running"})


@app.route("/user/<int:user_id>")
def user(user_id):
    result = get_user(user_id)
    if result:
        return jsonify({"user": result})
    return jsonify({"error": "not found"}), 404


@app.route("/eval")
def run_eval():
    expr = request.args.get("expr", "")
    try:
        result = safe_eval(expr)
    except Exception:
        return jsonify({"error": "invalid expression"}), 400
    return jsonify({"result": str(result)})


@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)  # nosemgrep: python.flask.security.audit.app-run-param-config.avoid_app_run_with_bad_host -- Codespaces需要綁定0.0.0.0才能對外access，非production環境
