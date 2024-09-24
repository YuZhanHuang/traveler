from blinker import Namespace

_signals = Namespace()

orders_pre_create = _signals.signal("order.pre_create")
orders_created = _signals.signal("order.created")
orders_pre_update = _signals.signal("order.pre_update")
orders_updated = _signals.signal("order.updated")
