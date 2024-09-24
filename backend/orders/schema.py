"""
- name
    - 若有非英文字母，丟出400 - Name contains non-English characters
    - 每個單字自首非大寫，丟出400 - Name is not capitalized
- price
    - 訂單金額超過200，拋出400，Price is over 2000
- currency
    - 貨幣格式若非TWD或USD，丟出400 - Currency format is wrong
    - 當貨幣為非USD時，需修改price金額承上固定匯率31元，並且將 currency 為 TWD
"""


from decimal import Decimal
from voluptuous import Schema, All, Required, Match, Length, Coerce, Range, REMOVE_EXTRA, Invalid


def validate_number(value):
    try:
        return Decimal(value)
    except Exception:
        raise Invalid(f'Invalid number: {value}')


order_schema = Schema({
    Required('id'): All(str, Match(r'^[A-Z]\d{7}$')),  # 驗證id格式
    Required('name'): All(str, Length(min=1)),  # 確保名稱不為空
    Required('price'): All(Coerce(validate_number), Range(min=0)),  # 價格必須是非負數字
    Required('currency'): All(str, Length(min=3, max=3)),  # 貨幣必須是3個字元
    Required('address'): {
        Required('city'): All(str, Length(min=1)),  # 確保城市不為空
        Required('district'): All(str, Length(min=1)),  # 確保區域不為空
        Required('street'): All(str, Length(min=1)),  # 確保街道不為空
    }
}, extra=REMOVE_EXTRA)
