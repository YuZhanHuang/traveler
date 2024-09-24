from backend.core import Service, db
from backend.orders.model import Order, Address
from backend.signals import signals


class OrderService(Service):
    __model__ = Order

    def _preprocess_params(self, kwargs):
        self.address_data = kwargs.pop('address', None)
        return kwargs


@signals.orders_pre_create.connect
def on_pre_create_order(sender: OrderService, instance: OrderService.__model__, **kwargs):
    address_data = sender.address_data
    instance.address = Address(**address_data)  # noqa
