from decimal import Decimal

from backend.core import Service
from backend.exceptions import ValidationError
from backend.orders.model import Order, Address
from backend.signals import signals


class OrderService(Service):
    __model__ = Order

    def _preprocess_params(self, kwargs):
        self.address_data = kwargs.pop('address', None)
        price = Decimal(kwargs['price'])

        # 如果貨幣不是 USD，則將價格轉換為 TWD 並調整匯率
        if kwargs['currency'] == 'USD':
            kwargs['price'] = price * 31  # 固定匯率 31

        if kwargs['price'] > Decimal('2000'):
            raise ValidationError(detail='Price is over 2000')

        return kwargs


@signals.order_pre_create.connect
def on_pre_create_order(sender: OrderService, instance: OrderService.__model__, **kwargs):
    address_data = sender.address_data
    instance.address = Address(**address_data)  # noqa
