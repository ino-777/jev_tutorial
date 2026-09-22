# jev TODO tutorial

Jev (`typesafe-sdk`) を使った、TODOアプリのチュートリアルです。
新しいタスクを追加すると、Jevのモデルが「カテゴリ」「緊急かどうか」「優先度」を型付きの構造化データとして返してくれます。

## 構成

```
jev_tutorial/
├── app/
│   ├── main.py     # FastAPI: /api/todos の CRUD
│   ├── ai.py        # TypeSafeClient.system_one() の呼び出し (jevへの質問)
│   ├── db.py         # SQLite (標準ライブラリ) への保存
│   └── schemas.py    # APIのリクエスト/レスポンス用 Pydantic モデル
├── static/            # フロントエンド (素のHTML/JS)
├── pyproject.toml
└── .env.example
```

`app/ai.py` で Jevのモデルに3つの質問を投げています:

```python
result = client.system_one(
    state=text,  # ユーザーが入力したTODOの本文
    questions={
        "category": Choice(instructions="...", criteria=CATEGORIES),
        "urgent": Noul(instructions="..."),
        "priority": Score(instructions="...", criteria=PRIORITY_LEVELS),
    },
)
result.choices["category"].choice   # 例: "work"
result.nouls["urgent"].noul         # 例: 0.92 (0〜1のYes確率)
result.scores["priority"].score     # 例: 1.7 (期待値スコア)
```

## セットアップ

### 1. uvのインストール確認

[uv](https://docs.astral.sh/uv/) を使います (Python 3.10以上が必要ですが、uvが自動で用意してくれます)。

```sh
brew install uv
uv --version
```

### 2. 依存関係のインストール

```sh
uv sync
```

`pyproject.toml` の内容に基づいて `.venv` が作成され、依存関係がインストールされます
(仮想環境を手動で有効化する必要はありません。以降のコマンドは `uv run` 経由で実行します)。

### 3. APIキーの設定

[Typesafe aiのコンソール画面](https://console.typesafe.ai/keys) でAPIキーを取得し、`.env` に設定します。

```sh
cp .env.example .env
# .env を開いて TYPESAFE_API_KEY=... を実際のキーに書き換える
```

### 4. 起動

```sh
uv run uvicorn app.main:app --reload
```

ブラウザで http://127.0.0.1:8000 を開くと、TODOを追加できます。追加するとjevモデルへのリクエストが飛び、カテゴリ・緊急度・優先度のバッジが付いた状態で一覧に表示されます。

## 動作確認 (curl)

```sh
curl -X POST http://127.0.0.1:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"text": "明日までに請求書を送る"}'
```
