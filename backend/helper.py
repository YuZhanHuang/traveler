import datetime
import importlib
import json
import os
import pkgutil
from decimal import Decimal, ROUND_HALF_UP
from ipaddress import IPv4Address

from delorean import Delorean
from flask import Blueprint
from flask.json import JSONEncoder as BaseJSONEncoder

from backend.constants import LOCAL_TZ


def register_blueprints(app, package_name, package_path):
    available_packages = [name for _, name, is_pkg in pkgutil.iter_modules([os.path.split(package_path)[0]]) if
                          is_pkg is True]
    for pkg_name in available_packages:
        m = importlib.import_module(f'{package_name}.{pkg_name}')
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)


class JsonSerializer:
    __json_public__ = None
    __json_hidden__ = None
    __json_modifiers__ = None
    __json_admin__ = None

    def get_field_names(self):  # 會將 db 的欄位 & 關聯到的 table 都抓出來
        for p in self.__mapper__.iterate_properties:  # noqa
            yield p.key

    def to_json(self, public=None, hidden=None, is_admin=False, extra=None):
        """
        hidden 若有給定，將會優先使用，複寫model中的
        """
        field_names = self.get_field_names()
        public = self.__json_public__ or public or field_names
        hidden = list(hidden or self.__json_hidden__ or [])
        modifiers = self.__json_modifiers__ or dict()
        extra = list(extra or [])
        if self.__json_admin__ and not is_admin:
            hidden += self.__json_admin__
        rv = dict()
        for key in public:
            if key not in hidden:
                rv[key] = getattr(self, key)
        for key, modifier in modifiers.items():
            print('key', key, 'modifier', modifier)
            value = getattr(self, key)
            rv[key] = modifier(value, self)
        for key in hidden:
            rv.pop(key, None)
        for key in extra:
            rv[key] = getattr(self, key, None)
        return rv


class JSONEncoder(BaseJSONEncoder):
    """
    :class:`JSONEncoder` which respects objects that include the
    :class:`JsonSerializer` mixin.
    """

    def default(self, obj):
        if isinstance(obj, IPv4Address):
            return str(obj)
        elif isinstance(obj, Decimal):
            return str(obj.quantize(Decimal('0.01'), ROUND_HALF_UP))
        elif isinstance(obj, JsonSerializer):
            return obj.to_json()
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, datetime.datetime):
            return Delorean(obj, 'UTC').shift(LOCAL_TZ).datetime.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")

        return super(JSONEncoder, self).default(obj)


def load_json(obj):
    if isinstance(obj, dict):
        return obj
    return json.loads(obj)
