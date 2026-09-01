"""后端冒烟测试"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


def run_tests(client: TestClient):
    def test_health():
        r = client.get("/api/health")
        assert r.status_code == 200, r.text
        print("health OK:", r.json())

    def test_login():
        r = client.post("/api/auth/login", json={"password": "growth2026"})
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]
        print("login OK")
        return token

    def test_child():
        r = client.get("/api/child")
        assert r.status_code == 200, r.text
        print("child:", r.json())

    def test_tasks():
        r = client.get("/api/tasks")
        assert r.status_code == 200, r.text
        tasks = r.json()
        assert len(tasks) > 0
        print("tasks count:", len(tasks))
        return tasks

    def test_score_add(token):
        headers = {"Authorization": f"Bearer {token}"}
        tasks = client.get("/api/tasks").json()
        pos_task = next(t for t in tasks if t["score_value"] > 0)
        r = client.post(
            "/api/scores",
            json={"task_rule_id": pos_task["id"], "reason": "测试加分"},
            headers=headers,
        )
        assert r.status_code == 200, r.text
        print("add score:", r.json())

    def test_dashboard(token):
        headers = {"Authorization": f"Bearer {token}"}
        r = client.get("/api/scores/dashboard", headers=headers)
        assert r.status_code == 200, r.text
        print("dashboard:", r.json())

    def test_achievements(token):
        headers = {"Authorization": f"Bearer {token}"}
        r = client.get("/api/achievements", headers=headers)
        assert r.status_code == 200, r.text
        print("achievements count:", len(r.json()))

    test_health()
    token = test_login()
    test_child()
    test_tasks()
    test_score_add(token)
    test_dashboard(token)
    test_achievements(token)
    print("=== 冒烟测试全部通过 ===")


if __name__ == "__main__":
    with TestClient(app) as client:
        run_tests(client)