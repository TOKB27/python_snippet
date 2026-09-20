# SystemA CLI
# 本ツールは、CLI から認証方式を選択し、ブラウザ認証またはデモ認証を実行して
# httpbin.org/get に GET リクエストを投げるデモとして作成しています。
# ADR に基づき、認証方式をターミナルで選択できるようにし、ブラウザ認証モードを起動する設計にしています。

import json
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional, Union
from urllib import parse, request

import keyring
import typer
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

API_URL = "https://httpbin.org/get"

# PyInstaller の onefile 実行時は __file__ が一時ディレクトリを指すことがあるため、
# 実行ファイル本体の配置場所を優先して token.json を保存するようにする。
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

DEFAULT_TOKEN_PATH = BASE_DIR / "token.json"
DEFAULT_KEYRING_SERVICE = "systema-cli"
DEFAULT_CURRENT_USERNAME_KEY = "__current_user__"
DEFAULT_BROWSER_PORT = 8080
console = Console()


# 1. 認証用トークンを生成する。
# ADR では idToken を発行する想定だが、デモ環境では「demo-token-<username>」という簡易トークンを使う。
# これにより、認証の仕組みそのものよりも、CLI での利用フローと保存・取得の動作を確認しやすくしている。
def create_demo_token(username: str) -> str:
    username = (username or "cli-user").strip()
    return f"demo-token-{username}"


# 2. Keyring に保存するユーザー名を正規化する。
# CLI から渡される username が None や空文字の場合でも、最低限のユーザー名に揃えることで
# Keychain / Credential Manager への保存処理が常に一貫した状態になる。
def _get_keyring_username(username: Optional[str] = None) -> str:
    return (username or "cli-user").strip() or "cli-user"


# 3. トークンを OS の Secure Store に保存する。
# keyring が利用できない環境では JSON のフォールバックを使う。
# これにより、ローカル開発環境でも実行可能な形で動作しつつ、本番寄りの保存方式を利用できる。
def save_token(token: str, token_path: Union[str, Path] = DEFAULT_TOKEN_PATH, username: Optional[str] = None) -> str:
    username_for_keyring = _get_keyring_username(username)
    try:
        # OS のセキュアストアに保存する。
        keyring.set_password(DEFAULT_KEYRING_SERVICE, username_for_keyring, token)
        # どのユーザーでログインしているかを別キーで保持し、status コマンドや refresh コマンドで参照しやすくする。
        keyring.set_password(DEFAULT_KEYRING_SERVICE, DEFAULT_CURRENT_USERNAME_KEY, username_for_keyring)
        return token
    except Exception:
        # keyring が使えない場合は JSON ファイルへ退避する。
        path = Path(token_path)
        path.write_text(json.dumps({"token": token}, ensure_ascii=False), encoding="utf-8")
        return token


# 4. 現在のログインユーザー名を取得する。
# Keyring に保存された current_user キーを見て、どのユーザーで認証済みかを判定する。
# 保存されていない場合はデフォルトの cli-user を使う。
def load_current_username() -> str:
    try:
        username = keyring.get_password(DEFAULT_KEYRING_SERVICE, DEFAULT_CURRENT_USERNAME_KEY)
        if username:
            return username
    except Exception:
        pass
    return "cli-user"


# 5. 認証状態をまとめて返す共通ヘルパー。
# status コマンドや他の処理で、ログイン判定とユーザー名・トークンを一括で取りたい場合に利用する。
def status_token(token_path: Union[str, Path] = DEFAULT_TOKEN_PATH, username: Optional[str] = None) -> dict:
    username_for_keyring = _get_keyring_username(username) if username is not None else load_current_username()
    token = load_token(token_path, username=username_for_keyring)
    return {
        "logged_in": bool(token),
        "username": username_for_keyring,
        "token": token,
    }


# 6. 保存済みトークンを更新する。
# refresh の意味としては「古いトークンを消す」ではなく、「新しいトークンを上書きして保持する」。
# ここではデモ用にユーザー名を含めて新しい値を生成している。
def refresh_token(token_path: Union[str, Path] = DEFAULT_TOKEN_PATH, username: Optional[str] = None) -> str:
    username_for_keyring = _get_keyring_username(username) if username is not None else load_current_username()
    refreshed = create_demo_token(f"{username_for_keyring}-refreshed")
    save_token(refreshed, token_path=token_path, username=username_for_keyring)
    return refreshed


# 7. ログアウト時に keyring と JSON ファイルの両方を掃除する。
# 実運用では失効したトークンを削除する処理に相当する。今回は demo 環境のため、
# 保存された token を破棄して未認証状態に戻す動作を定義している。
def delete_token(token_path: Union[str, Path] = DEFAULT_TOKEN_PATH, username: Optional[str] = None) -> bool:
    username_for_keyring = _get_keyring_username(username) if username is not None else load_current_username()

    try:
        keyring.delete_password(DEFAULT_KEYRING_SERVICE, username_for_keyring)
    except Exception:
        pass

    try:
        keyring.delete_password(DEFAULT_KEYRING_SERVICE, DEFAULT_CURRENT_USERNAME_KEY)
    except Exception:
        pass

    path = Path(token_path)
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("token"):
                path.unlink()
        except Exception:
            pass

    return True


# 8. 保存済みトークンを読み込む。
# keyring から優先的に取り出し、それが無い場合だけ JSON ファイルを確認する。
# これにより、本番寄りのセキュア保存を使いながら、開発・テスト環境での運用性も確保している。
def load_token(token_path: Union[str, Path] = DEFAULT_TOKEN_PATH, username: Optional[str] = None) -> str:
    path = Path(token_path)

    if username is not None:
        username_for_keyring = _get_keyring_username(username)
        try:
            token = keyring.get_password(DEFAULT_KEYRING_SERVICE, username_for_keyring)
            if token:
                return token
        except Exception:
            pass

        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if data.get("token"):
                    return str(data.get("token", ""))
            except json.JSONDecodeError:
                return ""
        return ""

    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("token"):
                return str(data.get("token", ""))
        except json.JSONDecodeError:
            pass

    username_for_keyring = load_current_username()
    try:
        token = keyring.get_password(DEFAULT_KEYRING_SERVICE, username_for_keyring)
        if token:
            return token
    except Exception:
        pass

    return ""


# 9. httpbin の GET API を呼ぶヘルパークラス。
# Authorization ヘッダーにトークンを付与して、実際の API ユーザー認証と同じ動作を模倣する。
# これにより、CLI から API を呼ぶ前の認証・リクエスト構成を安全かつ簡潔に確認できる。
class SystemAClient:
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url

    def fetch_data(self, token: str) -> str:
        req = request.Request(
            self.api_url,
            method="GET",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        with request.urlopen(req, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))

        return json.dumps(payload, ensure_ascii=False, indent=2)


# 10. 認証方式の選択値を正規化する。
# 1 / browser / 2 / demo / 3 / cancel を統一した内部表現に変換する。
# こうしておくと、対話入力とオプション指定の両方を同じ処理で扱える。
def normalize_auth_choice(choice: str) -> str:
    value = (choice or "").strip().lower()
    mapping = {
        "1": "browser",
        "browser": "browser",
        "2": "demo",
        "demo": "demo",
        "3": "cancel",
        "cancel": "cancel",
    }
    return mapping.get(value, "cancel")


# 11. ブラウザ認証の擬似フローを実行する。
# ADR では localhost のコールバックを利用する設計になっているが、ここではデモのために
# ローカルの待受サーバーを立ち上げて、ブラウザから callback を受け取り token を返す。
# 実際の OAuth/IDP 連携を模したデモとして機能する。
def run_browser_auth_flow(username: str = "cli-user", port: int = DEFAULT_BROWSER_PORT) -> str:
    class CallbackHandler(BaseHTTPRequestHandler):
        captured_token = None

        def do_GET(self):
            parsed = parse.urlparse(self.path)

            if parsed.path == "/cli-login":
                # ブラウザに表示するデモページ。
                # JavaScript により 1 秒後に callback URL へ遷移し、token を CLI に返す想定である。
                html = """
                <!doctype html>
                <html lang="ja">
                <head>
                  <meta charset="utf-8">
                  <title>SystemA Browser Auth</title>
                  <script>
                    setTimeout(function() {
                      const user = new URLSearchParams(window.location.search).get('user') || 'cli-user';
                      window.location.href = '/callback?token=' + encodeURIComponent('demo-token-' + user);
                    }, 1000);
                  </script>
                </head>
                <body style="font-family: sans-serif; padding: 40px;">
                  <h2>SystemA Browser Auth</h2>
                  <p>ブラウザ認証を開始しています...</p>
                </body>
                </html>
                """
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
                return

            if parsed.path == "/callback":
                # 認証完了後にブラウザ側から token が返ってくるので、それを保存している。
                params = parse.parse_qs(parsed.query)
                token = params.get("token", [create_demo_token(username)])[0]
                type(self).captured_token = token
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"<html><body><h2>認証完了</h2><p>{token}</p></body></html>".encode("utf-8"))
                return

            self.send_response(404)
            self.end_headers()

        def log_message(self, format, *args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", port), CallbackHandler)
    browser_url = f"http://127.0.0.1:{port}/cli-login?user={username}"

    # ブラウザを開く前に、サーバーを開始し、待ち受け状態を作っておく。
    # callback を受け取るまで CLI が止まっている状態を作り、認証完了時に token を受け取れるようにする。
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    console.print(Panel.fit(f"[cyan]ブラウザ認証を開始します[/cyan]\n[bold]{browser_url}[/bold]", title="Browser Auth"))
    try:
        webbrowser.open(browser_url)
    except Exception:
        pass

    # このループが callback を待つ本体。
    # 30 秒以内に token が返ってこなければ、デモ認証として fallback する。
    deadline = time.time() + 30
    while CallbackHandler.captured_token is None and time.time() < deadline:
        time.sleep(0.2)

    token = CallbackHandler.captured_token or create_demo_token(username)
    server.shutdown()
    server.server_close()
    return token


# 12. 認証方式を選択するメニューを出力する。
# 利用者がブラウザ認証・デモ認証・中止のどれを選ぶかを対話形式で決める。
# ここでの選択自体は、後段の normalize_auth_choice により一貫した内部値へ変換される。
def prompt_auth_method() -> str:
    console.print(Panel.fit("[bold]認証方式を選択してください。[/bold]\n1. Browser auth\n2. Demo auth\n3. Cancel", title="Select Auth Method"))
    choice = input("選択してください [1/2/3]: ").strip()
    return normalize_auth_choice(choice)


# 13. auth コマンドの本体。
# ブラウザ認証を選択された場合はブラウザを開き、デモ認証ならローカルで token を生成する。
# 最後に保存処理を行い、次の API 呼び出しで使える状態を作る。
def run_auth_command(username: str = "cli-user", method: Optional[str] = None) -> int:
    selected = normalize_auth_choice(method) if method else prompt_auth_method()

    if selected == "cancel":
        console.print(Panel.fit("[yellow]認証を中止しました。[/yellow]", title="Cancelled"))
        return 1

    if selected == "browser":
        token = run_browser_auth_flow(username=username, port=DEFAULT_BROWSER_PORT)
        save_token(token, DEFAULT_TOKEN_PATH, username=username)
        console.print(Panel.fit(f"[green]ブラウザ認証完了[/green]\n[bold]{token}[/bold]", title="Authentication Success"))
        return 0

    token = create_demo_token(username)
    save_token(token, DEFAULT_TOKEN_PATH, username=username)
    console.print(Panel.fit(f"[green]デモ認証完了[/green]\n[bold]{token}[/bold]", title="Authentication Success"))
    return 0


# 14. fetch コマンドの本体。
# 保存済みトークンを読み込み、httpbin の GET API を呼ぶ。
# 実際の運用時はバックエンド API へ置き換えられるが、ここでは public な endpoint を使って
# Authorization ヘッダー付きの動作を検証しやすくしている。
def run_fetch_command() -> int:
    username = load_current_username()
    token = load_token(DEFAULT_TOKEN_PATH, username=username)
    if not token:
        console.print(Panel.fit("[red]認証トークンが見つかりません。[/red]\n[bold]まず 'auth login' を実行してください。[/bold]", title="Not Authenticated"))
        return 1

    try:
        # API 取得中であることをユーザーに伝えるために Rich の status を利用する。
        with console.status("[bold green]API を取得しています...[/bold green]"):
            result = SystemAClient().fetch_data(token)
        console.print(Panel.fit(result, title="httpbin GET Response"))
        return 0
    except Exception as exc:
        console.print(Panel.fit(f"[red]API 呼び出しに失敗しました:[/red] {exc}", title="Request Failed"))
        return 1


# 15. 保存済みトークンを更新する。
# refresh は既存トークンを無効化するのではなく、別のトークンへ置き換える役割である。
# これにより、今後実際の OAuth / JWT の更新フローに近い形に拡張しやすい。
def run_refresh_command(username: Optional[str] = None) -> int:
    current_username = load_current_username() if username is None else _get_keyring_username(username)
    token = load_token(DEFAULT_TOKEN_PATH, username=current_username)
    if not token:
        console.print(Panel.fit("[red]認証トークンが見つかりません。[/red]\n[bold]まず 'auth login' を実行してください。[/bold]", title="Not Authenticated"))
        return 1

    refreshed = refresh_token(DEFAULT_TOKEN_PATH, username=current_username)
    console.print(Panel.fit(f"[green]トークンを更新しました[/green]\n[bold]{refreshed}[/bold]", title="Token Refreshed"))
    return 0


# 16. ログアウト処理。
# keyring と JSON の両方からトークンを削除し、未認証状態へ戻す。
# 今回はデモ用途のため、簡潔に削除後の結果を表示している。
def run_logout_command(username: Optional[str] = None) -> int:
    current_username = load_current_username() if username is None else _get_keyring_username(username)
    if delete_token(DEFAULT_TOKEN_PATH, username=current_username):
        console.print(Panel.fit(f"[yellow]ログアウトしました[/yellow]\n[bold]{current_username}[/bold]", title="Logged Out"))
        return 0
    console.print(Panel.fit(f"[yellow]ログアウト対象のトークンが見つかりませんでした[/yellow]\n[bold]{current_username}[/bold]", title="Logout Result"))
    return 1


# 17. 認証状態の確認処理。
# status コマンド用に、ログイン済みかどうかとユーザー名・トークンの状態をまとめて返す。
# ここでの情報は利用者に見せる重要な UI として使う。
def run_status_command(username: Optional[str] = None) -> int:
    current_username = load_current_username() if username is None else _get_keyring_username(username)
    info = status_token(DEFAULT_TOKEN_PATH, username=current_username)
    if not info["logged_in"]:
        console.print(Panel.fit(f"[yellow]未認証です[/yellow]\n[bold]{current_username}[/bold]", title="Authentication Status"))
        return 1

    table = Table(title="Authentication Status")
    table.add_column("項目", style="bold cyan")
    table.add_column("値")
    table.add_row("ユーザー名", info["username"])
    table.add_row("トークン", info["token"])
    console.print(table)
    return 0


# 18. Typer による CLI のエントリーポイント定義。
# GitHub CLI 風のサブコマンド構造を再現し、auth login / auth refresh / auth logout / auth status を扱えるようにする。
# add_completion=False は補完機能を無効化し、より簡潔な CLI として運用するための設定。
app = typer.Typer(add_completion=False, rich_markup_mode="rich")
auth_app = typer.Typer(help="認証コマンド", add_completion=False, rich_markup_mode="rich")
app.add_typer(auth_app, name="auth")


# auth コマンドのコールバック。
# サブコマンドが指定されていない場合は、通常の auth login と同じ動作をするようにする。
@auth_app.callback()
def auth_callback(
    ctx: typer.Context,
    method: Optional[str] = typer.Option(None, "--method", help="認証方式を直接指定します"),
    username: str = typer.Option("cli-user", "--username", help="認証で利用するユーザー名"),
) -> None:
    if ctx.invoked_subcommand is None:
        raise typer.Exit(run_auth_command(username=username, method=method))


# 19. auth login コマンド。
# ユーザーが CLI から明示的にログインしたい場合に利用する最重要のコマンド。
@auth_app.command("login")
def auth_login(
    method: Optional[str] = typer.Option(None, "--method", help="認証方式を直接指定します"),
    username: str = typer.Option("cli-user", "--username", help="認証で利用するユーザー名"),
) -> None:
    raise typer.Exit(run_auth_command(username=username, method=method))


# 20. auth refresh コマンド。
# 既存トークンを更新し、認証済み状態を保ちながら新しい値へ切り替える。
@auth_app.command("refresh")
def auth_refresh(
    username: Optional[str] = typer.Option(None, "--username", help="更新対象のユーザー名"),
) -> None:
    raise typer.Exit(run_refresh_command(username=username))


# 21. auth logout コマンド。
# 保存済みトークンを破棄し、ログイン状態をリセットする。
@auth_app.command("logout")
def auth_logout(
    username: Optional[str] = typer.Option(None, "--username", help="ログアウト対象のユーザー名"),
) -> None:
    raise typer.Exit(run_logout_command(username=username))


# 22. auth status コマンド。
# 保存済みトークンの有無とユーザーを確認し、CLI 上でログイン状態を表示する。
@auth_app.command("status")
def auth_status(
    username: Optional[str] = typer.Option(None, "--username", help="確認対象のユーザー名"),
) -> None:
    raise typer.Exit(run_status_command(username=username))


# 23. fetch コマンド.
# 認証済みユーザーが保存した token を使って、外部 API にアクセスして結果を表示する。
@app.command()
def fetch() -> None:
    raise typer.Exit(run_fetch_command())


if __name__ == "__main__":
    app()
