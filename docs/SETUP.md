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
mise run infra
```

PostgreSQL と Keycloak (OAuth2/OIDC 認証基盤) が起動します。

### 5. Keycloak の初期設定

Keycloak をテストとして使用する場合、以下の手順で初期設定を行ってください。

#### 5.1 Keycloak Admin Console へのアクセス

```bash
# ブラウザで開く
http://localhost:8080
```

ログイン画面が表示されたら、以下の資格情報でログイン:
- **Username**: `admin`
- **Password**: `admin`

#### 5.2 Realm の作成

1. **Realm の一覧画面** → 左側メニューの「Master」の右隣にある **Create realm** をクリック
2. 以下の情報を入力:
   - **Name**: `CirclePortal-dev`
3. **Create** をクリック

#### 5.2.1 Realm の言語設定（国際化の有効化）

作成した Realm で、以下の手順で言語設定を行ってください:

1. 左側メニュー → **Realm settings** をクリック
2. **General** タブで以下を設定:
   - **Internationalization Enabled**: **ON** に変更（国際化を有効化）
3. **Localization** タブで以下を設定:
   - **Supported locales**: `ja` (Japanese) を追加
   - **Default locale**: `ja` を選択
4. **Save** をクリック

これにより、Keycloak Admin Console およびログイン画面が日本語で表示されるようになります。

#### 5.3 Client の作成

新規に作成した Realm 内で:

1. 左側メニュー → **Clients** をクリック
2. **Create client** をクリック
3. **General settings** で以下の情報を入力:
   - **Client ID**: `circle-portal-backend`
     - 📌 **重要**: Client ID は識別子として機能し、アプリケーション側の`KEYCLOAK_CLIENT_ID`環境変数と**完全に一致**する必要があります
     - Client ID は英数字・ハイフン・アンダースコアを使用した固定値として定義してください（例：`my-service`, `service_name`, `myapp123` など）
     - [Keycloak公式ドキュメント - Client ID](https://www.keycloak.org/docs/latest/server_admin/index.html#con-basic-settings) では英数字文字列（alphanumeric ID string）と定義されています
   - **Name**: `Circle Portal backend API`（Keycloak UI に表示される日本語の名前）
   - **Client type**: `OpenID Connect`
4. **Next** → **Save** をクリック

#### 5.3.1 Access Settings（アクセス設定）

**Settings** タブの **Access settings** セクションで以下を設定してください:

- **Root URL**: （空欄のままで可）
- **Valid Redirect URIs**: `http://localhost:8000/*` を追加
- **Valid post logout redirect URIs**: （空欄のままで可）
- **Web Origins**: `http://localhost:8000/*` を追加
- **Admin URL**: `http://localhost:8000`

#### 5.3.2 Capability Config（認証設定）

**Settings** タブの **Capability config** セクションで以下を有効化してください:

- **Client authentication**: **ON** に変更（Confidential Client に設定）

**Authentication flow** セクションで以下を有効化してください:
- **Standard Flow Enabled**: **ON** (OIDC Authorization Code Flow を有効化)
- **Direct Access Grants Enabled**: **ON** (Resource Owner Password Credentials Flow を有効化、テスト用)

参考: [Keycloak公式ドキュメント - Capability Config](https://www.keycloak.org/docs/latest/server_admin/index.html#_capability_config)

#### 5.3.3 保存

**Save** をクリック

#### 5.4 Client Credentials の確認

**Credentials** タブで以下を確認してください:

- **Client Authenticator Type**: `client-secret` が選択されていることを確認
- **Client secret**: 自動生成されたシークレットを確認・コピー（後ほど環境変数に設定）

#### 5.4.1 Login Settings（ログイン設定）

**Settings** タブの **Login settings** セクションで以下を確認してください:

- **Login theme**: `keycloak` （デフォルト）
- **Consent required**: **OFF** のままで可（本番環境では必要に応じて有効化）

#### 5.4.2 Logout Settings（ログアウト設定）

**Settings** タブの **Logout settings** セクションで以下を確認してください:

- **Front channel logout**: **ON** （推奨）
  - ブラウザ経由でのログアウトが有効になります
- **Backchannel logout URL**: （空欄のままで可、オプション）
- **Backchannel logout session required**: **ON** （セッション ID を含める）

**随時保存すること**
#### 5.5 Realm Role の作成

**Realm Role として以下の2つを作成してください:**

##### 5.5.1 system_admin ロール

1. 左側メニュー → **Realm Roles** をクリック
2. **Create role** をクリック
3. 以下の情報を入力:
   - **Role name**: `system_admin`
   - **Description**: `システム管理者ロール`
4. **Save** をクリック

このロールは、サークルの承認・停止、全体のお知らせ管理など、システム全体の管理権限を持ちます。

##### 5.5.2 general ロール

1. 左側メニュー → **Realm Roles** をクリック
2. **Create role** をクリック
3. 以下の情報を入力:
   - **Role name**: `general`
   - **Description**: `一般ユーザーロール`
4. **Save** をクリック

このロールは、全ユーザーのデフォルトロールです。サークル情報の閲覧やサークル内での特定の操作が可能です。

**参考:** サークル内での「代表者・幹部」権限は、このRealm Roleではなく、`CircleMembers` テーブルで管理されます。詳細は要件定義書の「3.1.1. 権限管理」を参照してください。


#### 5.6 ユーザーの作成

1. 左側メニュー → **Users** をクリック
2. **Add user** をクリック
3. 以下の情報を入力:
   - **Username**: `testadmin`（またはテスト用の任意のユーザー名）
   - **Email**: `testadmin@example.com`
   - **First Name**: `テスト`
   - **Last Name**: `管理者`
   - **Email Verified**: **ON** に設定（メール検証をスキップ）
4. **Create** をクリック
5. **Credentials** タブ → **Set password** で任意のパスワードを設定（例：`password123`）
   - **Temporary**: **OFF** に設定（永続パスワード）

#### 5.6.1 Role Mapping - Realm Role の割り当て

1. **Role mapping** タブをクリック
2. **Assign role** → **filter by realm roles** で以下を選択:
   - `system_admin`
   - `general`
3. **Assign** をクリック

参考: [Keycloak公式ドキュメント - Assigning Roles](https://www.keycloak.org/docs/latest/server_admin/index.html#assigning_role_mappings)

#### 5.8 環境変数の設定

テスト実行前に、以下の環境変数を設定してください:

```bash
# Keycloak 統合テストを有効化
export KEYCLOAK_INTEGRATION_TEST=1

# テストユーザーの資格情報
export KEYCLOAK_TEST_USERNAME=testadmin
export KEYCLOAK_TEST_PASSWORD=password123

# 必要に応じて以下も上書き（デフォルト値で動作）
export KEYCLOAK_URL=http://localhost:8080
export KEYCLOAK_REALM=CirclePortal-dev
export KEYCLOAK_CLIENT_ID=circle-portal-backend
export KEYCLOAK_CLIENT_SECRET=...  # Confidential Client の場合のみ設定
```

⚠️ **セキュリティに関する注意**:
- 環境変数にはセンシティブ情報（パスワード、Client Secret）が含まれるため、本番環境では `.env` ファイルや専用の Vault を使用してください
- Git リポジトリには環境変数ファイルをコミットしないようにしてください
- テスト用のユーザー・パスワードは本番環境では使用しないでください

### 6. Keycloak 統合テストの実行

Keycloak を使用した統合テストを実行するには:

```bash
# 環境変数を設定（上記の 5.8 を参照）
export KEYCLOAK_INTEGRATION_TEST=1
export KEYCLOAK_TEST_USERNAME=testadmin
export KEYCLOAK_TEST_PASSWORD=password123

# Backend テストの実行
mise run test-back
```

このテストは、実際の Keycloak から取得したトークンを使用してエンドポイントの認可を検証します。

### 7. 開発サーバーの起動

```bash
mise run dev
```

以下のURLでアクセス可能になります:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Keycloak Admin Console: http://localhost:8080

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
