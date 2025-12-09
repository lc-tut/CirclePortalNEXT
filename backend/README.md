# CirclePortal Backend

FastAPI backend for CirclePortal.

## Setup

```bash
# Install dependencies
uv sync

# Copy environment file
cp .env.example .env

# Start database (Docker required)
docker compose up -d

# Run development server
uv run uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Configuration
│   ├── db/             # Database session
│   ├── models/         # SQLModel classes
│   ├── services/       # Business logic
│   └── main.py         # Application entry point
├── static/             # Static files (images)
├── tests/              # Test files
└── pyproject.toml      # Python dependencies
```

## Development

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

## Keycloak 統合テスト (任意)

ローカルで起動した Keycloak を使った統合テストは、環境変数 `KEYCLOAK_INTEGRATION_TEST=1` をセットしたときのみ実行されます。未設定の場合は自動でスキップします。

```bash
# Keycloak / DB を起動 (compose.yml の keycloak サービスを含む)
mise run infra

# Keycloak 側で system_admin ロールを持つテストユーザーを作成し、資格情報を設定
export KEYCLOAK_INTEGRATION_TEST=1
export KEYCLOAK_TEST_USERNAME="your-admin-user"
export KEYCLOAK_TEST_PASSWORD="your-admin-password"

# 必要に応じて上書き
export KEYCLOAK_URL="http://localhost:8080"
export KEYCLOAK_REALM="CirclePortal-dev"
export KEYCLOAK_CLIENT_ID="circle-portal-backend"
# 公開クライアントでない場合のみ設定
export KEYCLOAK_CLIENT_SECRET="your-client-secret"

# 統合テスト実行
mise run test-back
```
