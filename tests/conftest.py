import pytest
import sqlite3
import socket
from storage import create_table

@pytest.fixture
def con():
    con = sqlite3.connect(':memory:')
    create_table(con)

    yield con

    con.close()


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def blocked(*a, **kwargs):
        raise RuntimeError("real network is blocked in test")

    monkeypatch.setattr(socket,'getaddrinfo', blocked)
    monkeypatch.setattr(socket.socket,'connect', blocked)