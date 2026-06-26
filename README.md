# DevSecOps Lab — AIS3 課程實作環境

> **教學聲明**：本 repo 的漏洞為課程教學目的**刻意預埋**，所有密鑰均為公開範例值，不是真實憑證。
> AWS Key `AKIAIOSFODNN7EXAMPLE` 來自 [AWS 官方文件](https://docs.aws.amazon.com/general/latest/gr/aws-access-keys-best-practices.html)。

---

## 開始之前

1. Fork 這個 repo 到你的 GitHub 帳號
2. 點選 **Code** → **Codespaces** → **Create codespace on main**
3. 等待環境啟動（約 1-2 分鐘，自動安裝所有工具）

---

## Lab 指令

### Phase 1：讀 Workflow，找出安全防線缺失

打開 `.github/workflows/security-incomplete.yml`，回答：
- 這個 CI pipeline 缺少哪些安全步驟？
- 如果這個 pipeline 跑在你的 production repo，有什麼風險？

---

### Phase 2 Step 1：手動跑三個掃描工具

在 Codespaces terminal 依序執行：

```bash
# 1. 密鑰掃描
gitleaks detect --source . -v

# 2. SCA 相依性掃描（找有 CVE 的套件）
pip-audit -r requirements.txt

# 3. SAST 靜態分析
semgrep --config=p/python .
```

---

### Phase 2 Step 2：體驗 pre-commit 本機自動化

```bash
pre-commit run --all-files
```

思考題：為什麼 pre-commit 的 gitleaks 結果和 Step 1 的 `gitleaks detect` 不同？

---

### Phase 2 Step 3：對照完整版 CI Workflow

打開 `.github/workflows/security-complete.yml`，找出：
- 每個手動指令對應到哪一個 CI step？
- CI 版和手動版的差異是什麼？

---

## 預埋漏洞清單（掃描前先不要看）

<details>
<summary>點開查看答案（Phase 2 結束後再看）</summary>

| 漏洞類型 | 位置 | 工具 | 說明 |
|---------|------|------|------|
| Hardcoded AWS Key | `app/config.py:4-5` | gitleaks | AWS Access Key ID 和 Secret |
| Code Injection | `app/main.py:17` | semgrep | eval() 直接執行使用者輸入 |
| SQL Injection | `app/database.py:17` | 閱讀教材 | 字串拼接帶入 SQL（對照好寫法） |
| 有 CVE 的套件 | `requirements.txt` | pip-audit | Pillow 9.0.0、requests 2.6.0 等 |
| Debug 模式開啟 | `app/config.py:11` | semgrep | `DEBUG = True` 不應上 production |

</details>

---

## 發現表格（請自行填寫）

| 漏洞類型 | 位置（檔案/行號） | 嚴重性 | 發現工具 |
|---------|----------------|--------|---------|
| | | | |
| | | | |
| | | | |

---

## Repo 結構

```
devsecops-lab/
├── .devcontainer/devcontainer.json   # Codespaces 環境設定
├── .github/workflows/
│   ├── security-incomplete.yml       # 不完整版（Phase 1 審計用）
│   └── security-complete.yml         # 完整版（Phase 2 Step 3 對照用）
├── app/
│   ├── main.py                       # Flask 主程式
│   ├── database.py                   # 資料庫操作（含預埋漏洞）
│   └── config.py                     # 設定檔（含預埋漏洞）
├── tests/test_basic.py
├── .pre-commit-config.yaml
├── .gitleaks.toml
└── requirements.txt                  # 含有 CVE 的舊版依賴
```
