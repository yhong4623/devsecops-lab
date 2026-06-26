import sqlite3

# ── 閱讀教材：SQL Injection 好寫法 vs 壞寫法對照 ──────────────────────────
# 這個檔案不是 semgrep 的掃描目標，而是讓學員閱讀理解的對照範例。
# 問題：為什麼 semgrep 掃 main.py 的 eval()，而不掃這裡的 SQL injection？
# 答案：Semgrep 免費規則對 sqlite3 的跨行 taint tracking 支援有限。
#       這正是「工具有其侷限，不能完全依賴單一工具」的教學點。
# ─────────────────────────────────────────────────────────────────────────────


def get_user(username):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # 壞寫法：字串拼接直接帶入 SQL，有 SQL Injection 風險
    # 攻擊者輸入 ' OR '1'='1 可以繞過認證、撈出所有資料
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)

    return cursor.fetchone()


def get_user_safe(username):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    # 好寫法：參數化查詢，資料庫會自動跳脫特殊字元
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))

    return cursor.fetchone()
