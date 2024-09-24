from blinker import Namespace

_signals = Namespace()

orders_pre_create = _signals.signal("")
orders_created = _signals.signal("")
orders_pre_update = _signals.signal("")
orders_pre_updated = _signals.signal("")