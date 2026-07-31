import logging

import pytest


@pytest.mark.asyncio
async def test_create_and_read_nested_logs(client, auth_headers):
    # # 🔑 1. 註冊與登入以取得 JWT Token
    # auth_payload = {
    #     "username": "Ben",
    #     "password": "password123",
    # }  # 👈 滿足 8 位數以上限制
    # await client.post("/auth/register", json=auth_payload)

    # 登入（注意：OAuth2 表單需要使用 data= 傳送 application/x-www-form-urlencoded）
    # login_resp = await client.post("/auth/login", data=auth_payload)
    # token = login_resp.json()["access_token"]

    # # 建立認證請求頭 (Authorization Header)
    # headers = {"Authorization": f"Bearer {token}"}

    # 1. 先建立一台機台
    m_resp = await client.post(
        "/machines", json={"name": "Test-Machine", "model": "M1"}, headers=auth_headers
    )
    assert m_resp.status_code == 201
    machine_id = m_resp.json()["id"]

    # 2. 測試 POST /machines/{machine_id}/logs
    log_data = {"level": "INFO", "message": "測試日誌訊息"}
    create_resp = await client.post(
        f"/machines/{machine_id}/logs", json=log_data, headers=auth_headers
    )
    assert create_resp.status_code == 201
    assert create_resp.json()["machine_id"] == machine_id

    # 3. 測試 GET /machines/{machine_id}/logs
    get_resp = await client.get(f"/machines/{machine_id}/logs", headers=auth_headers)
    assert get_resp.status_code == 200
    logs = get_resp.json()
    assert len(logs) == 1
    assert logs[0]["message"] == "測試日誌訊息"

    # 4. 測試 GET /logs (全域)
    global_resp = await client.get("/logs")
    assert global_resp.status_code == 200
    assert len(global_resp.json()) >= 1


async def test_create_log_triggers_background_task(
    client, test_machine, caplog, auth_headers
):
    caplog.set_level(logging.INFO)

    # 發送新增 Log 請求
    response = await client.post(
        f"/machines/{test_machine.id}/logs",
        json={"message": "測試背景任務"},
        headers=auth_headers,
    )
    assert response.status_code == 201

    # 斷言 Log 中確實印出了背景任務成功的訊息（證明背景任務沒爆，且真有抓到機台名稱）
    assert "[背景通知成功]" in caplog.text
    assert test_machine.name in caplog.text
