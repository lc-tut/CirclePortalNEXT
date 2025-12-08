# セットアップガイド

## 前提条件

以下のツールがインストールされている必要があります:

- **mise**: https://mise.jdx.dev/getting-started.html
- **Docker**: https://docs.docker.com/get-docker/

## ステップバイステップ

### 1. mise のインストール

```bash
# Linux / macOS
curl https://mise.run | sh

# または Homebrew (macOS)
brew install mise

# シェル設定に追加
echo 'eval "$(mise activate bash)"' >> ~/.bashrc
source ~/.bashrc
```

### 2. プロジェクトのセットアップ

```bash
# リポジトリに移動
cd CirclePortalNEXT

# Python と Node.js を自動インストール
mise install

# 依存関係をすべてインストール
mise run setup
```

### 3. 環境変数の設定

```bash
# Backend
cp backend/.env.example backend/.env
# 必要に応じて backend/.env を編集

# Frontend  
cp frontend/.env.local.example frontend/.env.local
# 必要に応じて frontend/.env.local を編集
```

### 4. データベースの起動

```bash
docker compose up -d
```

### 5. 開発サーバーの起動

```bash
mise run dev
```

以下のURLでアクセス可能になります:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## トラブルシューティング

### mise がコマンドを認識しない

シェルの設定ファイルに mise の初期化コードを追加してください:

```bash
echo 'eval "$(mise activate bash)"' >> ~/.bashrc
source ~/.bashrc
```

### ポートが既に使用されている

別のサービスがポートを使用している場合、以下で確認・停止してください:

```bash
# ポート使用状況の確認
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# プロセスの停止
kill -9 <PID>
```

### Docker の権限エラー

```bash
# Docker グループにユーザーを追加
sudo usermod -aG docker $USER
# ログアウト・ログインして反映
```

### GitHub API レート制限エラー

`mise install` 実行時に以下のエラーが発生する場合:

```
mise ERROR Failed to install aqua:astral-sh/uv@latest: 
   HTTP status client error (403 rate limit exceeded)
```

**原因:** GitHubの未認証APIリクエスト制限(60回/時)に到達しています。

**解決方法:**

1. **GitHub認証を使用する (推奨)**
```bash
# GitHub CLIを使用している場合
export GITHUB_TOKEN=$(gh auth token)
mise install

# または、Personal Access Tokenを直接設定
export GITHUB_TOKEN="your_github_token"
mise install
```

2. **時間を待つ**
```bash
# エラーメッセージに表示された時刻までしばらく待ってから再実行
mise install
```

3. **uvを直接インストールする場合**
```bash
# miseを経由せずに公式インストーラーを使用
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### uv のインストールエラー

```bash
# 手動でインストール
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 次のステップ

セットアップが完了したら、以下のドキュメントを参照してください:

- [要件定義書](./要件定義書.md) - 機能仕様・DB設計
- [Backend README](../backend/README.md) - API開発
- [Frontend README](../frontend/README.md) - UI開発
