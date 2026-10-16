import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def test_register_bonus_flow():
    with TestClient(app) as c:
        nick = "tester_" + os.urandom(3).hex()
        r = c.post("/api/auth/register", json={"nickname": nick, "password": "secret1"})
        assert r.status_code == 200
        h = {"Authorization": f"Bearer {r.json()['token']}"}

        me = c.get("/api/me", headers=h).json()
        assert me["balance"] == 100 and me["bonus"]["can_claim"]

        me = c.post("/api/bonus/claim", headers=h).json()
        assert me["balance"] == 150 and not me["bonus"]["can_claim"]

        assert c.post("/api/bonus/claim", headers=h).status_code == 400
        assert c.post("/api/auth/register", json={"nickname": nick.upper(), "password": "secret1"}).status_code == 409
        assert c.post("/api/auth/login", json={"nickname": nick, "password": "wrong11"}).status_code == 401
        assert len(c.get("/api/ledger", headers=h).json()) == 2


def test_coinflip(monkeypatch):
    from app.games import coinflip

    with TestClient(app) as c:
        nick = "flip_" + os.urandom(3).hex()
        token = c.post("/api/auth/register", json={"nickname": nick, "password": "secret1"}).json()["token"]
        h = {"Authorization": f"Bearer {token}"}
        play = lambda **kw: c.post("/api/games/coinflip", headers=h, json={"choice": "heads", **kw})

        monkeypatch.setattr(coinflip, "flip", lambda: "heads")
        r = play(bet=10, request_id="a1").json()
        assert r["won"] and r["payout"] == 19 and r["balance"] == 109

        dup = play(bet=10, request_id="a1").json()  # повтор не списує двічі
        assert dup["round_id"] == r["round_id"] and dup["balance"] == 109

        monkeypatch.setattr(coinflip, "flip", lambda: "tails")
        r = play(bet=10, request_id="a2").json()
        assert not r["won"] and r["balance"] == 99

        assert play(bet=1000).status_code == 400  # більше за баланс
        assert play(bet=5).status_code == 422  # менше мінімуму
        types = [e["type"] for e in c.get("/api/ledger", headers=h).json()]
        assert types == ["bet", "win", "bet", "signup"]
