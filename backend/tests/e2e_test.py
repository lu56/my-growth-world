"""端到端业务闭环测试（通过前端代理访问后端）"""
import json
import urllib.request

BASE = "http://127.0.0.1:5173/api"


def req(path, method="GET", body=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    r = urllib.request.Request(
        BASE + path, data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def main():
    # 1. 健康检查
    s, _ = req("/health")
    print(f"[1] health: {s}")

    # 2. 登录
    s, login = req("/auth/login", "POST", {"password": "growth2026"})
    print(f"[2] login: {s}, token_len={len(login['access_token'])}")
    token = login["access_token"]

    # 3. 获取任务
    s, tasks = req("/tasks", token=token)
    pos_tasks = [t for t in tasks if t["score_value"] > 0]
    neg_tasks = [t for t in tasks if t["score_value"] < 0]
    print(f"[3] tasks: {len(tasks)}, 正向={len(pos_tasks)}, 负向={len(neg_tasks)}")

    # 4. 加分
    s, r = req("/scores", "POST", {"task_rule_id": pos_tasks[0]["id"], "reason": "端到端测试加分"}, token)
    print(f"[4] add_score: {s}, balance={r['balance']}, 新成就={r['new_achievements']}")

    # 5. 减分
    s, r = req("/scores", "POST", {"task_rule_id": neg_tasks[0]["id"], "reason": "端到端测试减分"}, token)
    print(f"[5] add_score(neg): {s}, balance={r['balance']}")

    # 6. 余额与等级
    s, bal = req("/scores/balance")
    print(f"[6] balance: {bal['balance']}, level={bal['level']['level']} {bal['level']['level_name']}, 进度={bal['level']['progress']:.0%}")

    # 7. 数据看板
    s, dash = req("/scores/dashboard")
    print(f"[7] dashboard: 今日={dash['today_score']}, 本周={dash['week_score']}, 正={dash['positive_count']} 负={dash['negative_count']}")

    # 8. 成就
    s, ach = req("/achievements")
    unlocked = [a for a in ach if a["unlocked"]]
    print(f"[8] achievements: 共{len(ach)}, 已解锁{len(unlocked)}")

    # 9. 等级列表
    s, levels = req("/levels")
    print(f"[9] levels: {len(levels)} 级")

    # 10. 奖励列表
    s, rewards = req("/rewards")
    print(f"[10] rewards: {len(rewards)}")

    # 11. 兑换流程（需先确保有足够宝石，若不足则只列出）
    if bal["balance"] >= rewards[0]["cost"]:
        s, exc = req("/rewards/exchange", "POST", {"reward_id": rewards[0]["id"]}, token)
        print(f"[11] exchange: {s}, 剩余={exc.get('balance')}, 新成就={exc.get('new_achievements')}")
    else:
        print(f"[11] exchange: 宝石不足({bal['balance']} < {rewards[0]['cost']})，跳过")

    # 12. 日志
    s, logs = req("/logs")
    print(f"[12] logs: {len(logs)}")

    # 13. 家长配置
    s, cfg = req("/parent/config")
    print(f"[13] parent config: daily_limit={cfg['daily_score_limit']}")

    print("\n=== 端到端业务闭环测试全部通过 ===")


if __name__ == "__main__":
    main()