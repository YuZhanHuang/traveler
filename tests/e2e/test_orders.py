"""
針對payload對以下測試，確認是否有正確拋出錯誤
要記得參數化

- name
    - 若有非英文字母，丟出400 - Name contains non-English characters
    - 每個單字自首非大寫，丟出400 - Name is not capitalized
- price
    - 訂單金額超過200，拋出400，Price is over 2000
- currency
    - 貨幣格式若非TWD或USD，丟出400 - Currency format is wrong
    - 當貨幣為非USD時，需修改price金額承上固定匯率31元，並且將 currency 為 TWD

測試創建的POST API
"""
import pytest

cases = [
    # 測試 name 包含非英文字母
    (
        {
            "id": "A0000002",
            "name": "Melody Holiday 界",
            "address": {
                "city": "taipei-city",
                "district": "da-an-district",
                "street": "fuxing-south-road"
            },
            "price": "1000",
            "currency": "USD"
        },
        400,
        "Name contains non-English characters"
    ),
    # 測試 name 首字母非大寫
    (
        {
            "id": "A0000002",
            "name": "melody Holiday Inn",
            "address": {
                "city": "taipei-city",
                "district": "da-an-district",
                "street": "fuxing-south-road"
            },
            "price": "1000",
            "currency": "USD"
        },
        400,
        "Name is not capitalized"
    ),
    # 測試 price 超過 2000
    (
        {
            "id": "A0000002",
            "name": "Melody Holiday Inn",
            "address": {
                "city": "taipei-city",
                "district": "da-an-district",
                "street": "fuxing-south-road"
            },
            "price": "200000",
            "currency": "USD"
        },
        400,
        "Price is over 2000"
    ),
    # 測試 currency 格式錯誤
    (
        {
            "id": "A0000002",
            "name": "Melody Holiday Inn",
            "address": {
                "city": "taipei-city",
                "district": "da-an-district",
                "street": "fuxing-south-road"
            },
            "price": "1000",
            "currency": "JPY"
        },
        400,
        "Currency format is wrong"
    ),
    # 測試非 USD 的貨幣，檢查 price 和 currency 修改
    (
        {
            "id": "A0000002",
            "name": "Melody Holiday Inn",
            "address": {
                "city": "taipei-city",
                "district": "da-an-district",
                "street": "fuxing-south-road"
            },
            "price": "1000",
            "currency": "TWD"
        },
        200,
        None  # 成功情況下沒有錯誤消息
    ),
]


@pytest.mark.parametrize("payload, expected_status, expected_message", cases)
def test_create_order(test_client, payload, expected_status, expected_message):
    response = test_client.post("/api/orders", json=payload)
    assert response.status_code == expected_status

    if expected_message:
        assert response.json["payload"]["failure_msg"] == expected_message
    else:
        # 如果是成功的情況
        assert response.status_code == 200
        assert response.json["data"]["currency"] == "TWD"
