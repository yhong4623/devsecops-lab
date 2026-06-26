from flask import Flask, request, jsonify
from app.database import get_user
from app.config import DEBUG

app = Flask(__name__)


@app.route("/user")
def user():
    username = request.args.get("username")
    result = get_user(username)
    return jsonify({"user": result})


@app.route("/calc")
def calc():
    expr = request.args.get("expr")
    # 預埋漏洞：eval() 直接執行使用者輸入，Semgrep 應該抓到這行
    result = eval(expr)
    return jsonify({"result": result})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=DEBUG)
