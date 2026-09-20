# SystemA CLI

この CLI は、ユーザー向けの Python ベース CLI として実装したデモです。
ADR の設計意図に合わせて、`auth` 実行時に認証方式を選択し、ブラウザ認証またはデモ認証を行えるようにしています。

## 目的

- GitHub CLI に近い `auth login / auth refresh / auth logout` の操作感を持つ
- CLI から認証方式を選択できる
- ブラウザ認証を選択したら、ブラウザ認証フローを起動する
- 認証後に `https://httpbin.org/get` を呼び出してレスポンスを確認できる
- 実際の AWS 認証基盤を使わず、ローカル環境で動作するデモとして扱う

## 実行方法

プロジェクトのルートは `CLI` ディレクトリを基準にします。
以下のコマンドは必ず `CLI` 配下で実行してください。

### 1. 仮想環境を作成する

```bash
cd CLI
python3 -m venv .venv
. .venv/bin/activate
pip install pytest keyring
```

### 2. 認証ログインを実行する

```bash
cd CLI
. .venv/bin/activate
python systema_cli.py auth login
```

`auth login` は GitHub CLI に近い操作感で、認証方式の選択メニューを表示します。

```text
認証方式を選択してください。
1. Browser auth
2. Demo auth
3. Cancel
```

- `1` を選ぶとブラウザ認証を開始します
- `2` を選ぶとデモ認証でトークンを発行します
- `3` を選ぶと認証を中止します

ブラウザ認証を選んだ場合、ブラウザが起動し、ローカルの認証コールバックを待ちます。
その後、トークンが作成され、keyring に保存されます。

### 3. 既存の互換コマンド

```bash
cd CLI
python systema_cli.py auth --method browser --username alice
python systema_cli.py auth --method demo --username alice
```

上記は従来の互換コマンドです。GitHub CLI 風の利用では `auth login` を推奨します。

### 4. token を更新する

```bash
cd CLI
python systema_cli.py auth refresh
```

保存済みトークンを更新し、新しいトークンを OS の keyring に保存します。

### 5. ログアウトする

```bash
cd CLI
python systema_cli.py auth logout
```

保存済みトークンと現在のユーザー情報を削除します。

### 6. API を呼び出す

```bash
cd CLI
python systema_cli.py fetch
```

保存済みトークンを使って `https://httpbin.org/get` に GET リクエストを送信し、JSON を表示します。

## 例: 実行結果

```json
{
  "args": {},
  "headers": {
    "Accept": "application/json",
    "Accept-Encoding": "identity",
    "Authorization": "Bearer demo-token-alice",
    "Content-Type": "application/json",
    "Host": "httpbin.org",
    "User-Agent": "Python-urllib/3.14"
  },
  "url": "https://httpbin.org/get"
}
```

## バイナリファイル化（EXE化）手順

ユーザーに配布できるように、Python スクリプトを単一の実行ファイルへ変換します。
ここでは `PyInstaller` を利用します。

### 1. 仮想環境に PyInstaller を追加する

```bash
cd CLI
python3 -m venv .venv
. .venv/bin/activate
pip install pyinstaller pytest keyring
```

### 2. EXE を生成する

```bash
cd CLI
pyinstaller --onefile --name systema_cli systema_cli.py
```

実行後、以下のような出力が得られます。

```text
dist/systema_cli
```

### 3. 生成されたバイナリを実行する

```bash
cd CLI
./dist/systema_cli --help
./dist/systema_cli auth login
./dist/systema_cli auth refresh
./dist/systema_cli fetch
./dist/systema_cli auth logout
```

### 4. 配布時の注意点

- 生成物は `dist/` 配下に作成されます
- `--onefile` により単一ファイル化されます
- 認証トークンは OS の Keychain / keyring に保存されます
- `auth refresh` で保存済みトークンを更新できます
- `auth logout` で保存済みトークンとユーザー情報を削除できます
- keyring が利用できない環境では `token.json` にフォールバックして保存します
- そのため、ファイルベースの保存ができない環境でも CLI は動作します

## 補足

- この実装は GitHub CLI に近い操作感として、`auth login / auth refresh / auth logout` を採用しています
- ただしデモ環境ではローカルの簡易認証と httpbin の GET を利用しています

## テスト実行

```bash
cd CLI
. .venv/bin/activate
pytest test_systema_cli.py -q
```
