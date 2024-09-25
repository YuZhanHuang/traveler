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
import re
from decimal import Decimal
from voluptuous import Schema, All, Required, Match, REMOVE_EXTRA, Invalid


def validate_number(value):
    try:
        return Decimal(value)
    except Exception:
        raise Invalid(message=f'Invalid number: {value}')


def validate_name(value):
    """
    驗證名稱是否只包含英文字母且首字母是否大寫
    :param value:
    :return:
    """
    if not re.match(r'^[A-Za-z ]+$', value):
        raise Invalid(message='Name contains non-English characters')

    words = value.split()
    for word in words:
        if not word[0].isupper():
            raise Invalid(message='Name is not capitalized')
    return value


def validate_price_and_currency(value):
    """
    驗證價格是否超過 2000 並調整貨幣非 USD 時的價格
    :param value:
    :return:
    """
    if value not in ['TWD', 'USD']:
        raise Invalid(message='Currency format is wrong')

    return value


order_schema = Schema({
    Required('id'): All(str, Match(r'^[A-Z]\d{7}$')),  # 驗證id格式
    Required('name'): All(str, validate_name),  # 確保名稱不為空
    Required('price'): All(str, validate_number),  # 價格必須是非負數字
    Required('currency'): All(str, validate_price_and_currency),  # 貨幣必須是3個字元
    Required('address'): {
        Required('city'): str,  # 確保城市不為空
        Required('district'): str,  # 確保區域不為空
        Required('street'): str,  # 確保街道不為空
    }
}, extra=REMOVE_EXTRA)
