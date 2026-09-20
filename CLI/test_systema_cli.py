# このテストは、CLI 配下で動く認証メニューと GET API 呼び出しが仕様どおりに動くかを確認するためのものです。
# httpbin を利用して、Authorization ヘッダーが正しく付与されているかを見ています。

import json

import keyring
from keyring.errors import PasswordDeleteError
from typer.testing import CliRunner

from systema_cli import (
    SystemAClient,
    app,
    create_demo_token,
    delete_token,
    load_current_username,
    load_token,
    normalize_auth_choice,
    refresh_token,
    save_token,
    status_token,
)

runner = CliRunner()


# 認証方式の選択値を正規化できることを確認する。
def test_normalize_auth_choice_accepts_browser_and_demo():
    assert normalize_auth_choice("1") == "browser"
    assert normalize_auth_choice("browser") == "browser"
    assert normalize_auth_choice("2") == "demo"
    assert normalize_auth_choice("demo") == "demo"


# トークン生成にはユーザー名が含まれていることを確認する。
def test_create_demo_token_uses_user_and_prefix():
    token = create_demo_token("alice")
    assert token.startswith("demo-token-")
    assert "alice" in token


# トークン保存と復元が正しく行えるかを確認する。
def test_save_and_load_token_round_trip(tmp_path):
    token_path = tmp_path / "token.json"
    save_token("demo-token-123", token_path)
    loaded = load_token(token_path)
    assert loaded == "demo-token-123"


def test_save_and_load_token_round_trip_with_keyring():
    username = "keyring-user-001"
    try:
        keyring.delete_password("systema-cli", username)
    except PasswordDeleteError:
        pass

    try:
        save_token("demo-token-keyring", username=username)
        assert keyring.get_password("systema-cli", username) == "demo-token-keyring"
        assert load_token(username=username) == "demo-token-keyring"
    finally:
        try:
            keyring.delete_password("systema-cli", username)
        except PasswordDeleteError:
            pass


def test_refresh_token_replaces_existing_token():
    username = "refresh-user-001"
    try:
        keyring.delete_password("systema-cli", username)
    except PasswordDeleteError:
        pass

    save_token("demo-token-old", username=username)
    refreshed = refresh_token(username=username)
    assert refreshed.startswith("demo-token-")
    assert refreshed != "demo-token-old"
    assert load_token(username=username) == refreshed

    try:
        keyring.delete_password("systema-cli", username)
    except PasswordDeleteError:
        pass


def test_delete_token_removes_keyring_entry():
    username = "logout-user-001"
    save_token("demo-token-remove", username=username)
    assert delete_token(username=username) is True
    assert load_token(username=username) == ""
    assert load_current_username() == "cli-user"


def test_status_token_reports_logged_in_state():
    username = "status-user-001"
    save_token("demo-token-status", username=username)
    status = status_token(username=username)
    assert status["logged_in"] is True
    assert status["username"] == username
    assert status["token"].startswith("demo-token-")
    delete_token(username=username)


# GET リクエスト時に Authorization ヘッダーが含まれ、対象 URL が httpbin の GET であることを確認する。
def test_fetch_uses_httpbin_get_endpoint():
    client = SystemAClient()
    response = client.fetch_data("demo-token-123")
    payload = json.loads(response)
    assert payload["headers"]["Authorization"] == "Bearer demo-token-123"
    assert payload["url"] == "https://httpbin.org/get"


def test_typer_auth_login_command_runs():
    result = runner.invoke(app, ["auth", "login", "--method", "demo", "--username", "typer-user"])
    assert result.exit_code == 0
    assert "デモ認証完了" in result.stdout
