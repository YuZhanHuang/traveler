from blinker import Namespace

_signals = Namespace()

order_pre_create = _signals.signal("order.pre_create")
order_created = _signals.signal("order.created")
order_pre_update = _signals.signal("order.pre_update")
order_updated = _signals.signal("order.updated")
