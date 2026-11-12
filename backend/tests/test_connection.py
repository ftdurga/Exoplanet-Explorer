import pytest

from backend.database.connection import DatabaseConnectionError, get_connection


def test_get_connection_returns_an_open_connection():
    connection = get_connection()
    try:
        assert connection.is_connected()
    finally:
        connection.close()
    assert not connection.is_connected()


def test_connection_can_run_a_query():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM planets")
        assert cursor.fetchone()[0] > 0
    finally:
        cursor.close()
        connection.close()


def test_wrong_password_raises_custom_error_without_leaking_it(monkeypatch):
    monkeypatch.setenv("DB_PASSWORD", "not_the_real_pw_123")
    with pytest.raises(DatabaseConnectionError) as error:
        get_connection()
    assert "not_the_real_pw_123" not in str(error.value)


def test_wrong_database_name_is_named_in_the_error(monkeypatch):
    monkeypatch.setenv("DB_NAME", "no_such_database")
    with pytest.raises(DatabaseConnectionError) as error:
        get_connection()
    assert "no_such_database" in str(error.value)