# CirclePortal NEXT

東京工科大学のサークル情報を集約・可視化するWebサービス

## 概要

各サークルの担当者が自律的に情報を更新できることを強みとし、受験生・在学生に最新のサークル情報を提供するポータルサイトです。

## 技術スタック

- **Frontend**: Next.js 15 (App Router) + shadcn/ui + Tailwind CSS
- **Backend**: FastAPI + SQLModel + PostgreSQL
- **Infrastructure**: Docker Compose
- **Development Tools**: mise + uv + npm

## プロジェクト構成

```
CirclePortalNEXT/
├── backend/          # FastAPI バックエンド
├── frontend/         # Next.js フロントエンド
├── docs/             # ドキュメント
├── docker-compose.yml
├── .mise.toml        # 開発環境管理
└── README.md
```

## セットアップ

### 必須ツール

- [mise](https://mise.jdx.dev/) - バージョン管理・タスクランナー
- [uv](https://docs.astral.sh/uv/) - Python パッケージ管理
- [Docker](https://www.docker.com/) - コンテナ管理

### 初期セットアップ

1. リポジトリをクローン

```bash
git clone <repository-url>
cd CirclePortalNEXT
```

2. mise で環境をセットアップ

```bash
# Python 3.12 と Node 20 を自動インストール
mise install

# 依存関係をインストール
mise run setup
```

3. 環境変数を設定

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.local.example frontend/.env.local
```

4. データベースを起動

```bash
docker compose up -d
```

## 開発

### 開発サーバーの起動

```bash
# すべてのサービスを起動（DB + Backend + Frontend）
mise run dev
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 個別起動

```bash
# Backend のみ
cd backend
uv run uvicorn app.main:app --reload

# Frontend のみ
cd frontend
npm run dev
```

### テスト実行

```bash
# すべてのテストを実行
mise run test

# Backend のみ
cd backend && uv run pytest

# Frontend のみ
cd frontend && npm run test
```

### その他のコマンド

```bash
# すべてのサービスを停止
mise run down

# データベースをリセット（警告: すべてのデータが削除されます）
mise run db-reset
```

## ドキュメント

詳細な要件定義やDB設計については以下を参照してください:

- [要件定義書](./docs/要件定義書.md)

## 開発ルール

### Git フロー

- GitHub Flow を採用
- `main` ブランチは常にデプロイ可能な状態を保つ
- フィーチャーブランチから PR を作成してマージ

### コミットメッセージ

Conventional Commits に準拠:

- `feat:` 新機能
- `fix:` バグ修正
- `docs:` ドキュメント
- `style:` フォーマット
- `refactor:` リファクタリング
- `test:` テスト
- `chore:` その他

## ライセンス

このプロジェクトは東京工科大学 Linux Club により開発されています。
東京工科大学の最新サークル情報一覧を行えるサービス
