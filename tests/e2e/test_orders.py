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

還要測試創建的POST API
"""