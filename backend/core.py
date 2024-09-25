import os

from flask import abort
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from sqlalchemy.orm import declarative_base
from werkzeug.local import LocalProxy

from backend import timetools
from backend.constants import LOCAL_TZ
from backend.signals import signals

Base = declarative_base()
metadata = Base.metadata

# basic setting
root_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()


class Service:
    __model__ = None
    __query_params_forbidden__ = []

    @classmethod
    def get_service(cls, name):
        for kls in Service.__subclasses__():
            if kls.__name__ == name:
                return kls()

    def _isinstance(self, model, raise_error=True):
        """
        檢查模型實例是否與服務配置的相同，如果不匹配，默認則會拋出 ValueError的錯誤

        :param model: 模型實例
        :param raise_error: 不匹配是否拋出異常
        """
        if isinstance(model, LocalProxy):
            model = model._get_current_object()  # noqa
        rv = isinstance(model, self.__model__)
        if not rv and raise_error:
            raise ValueError('%s is not of type %s' % (model, self.__model__))
        return rv

    @staticmethod
    def _preprocess_params(kwargs):
        """預處理參數"""
        kwargs.pop('csrf_token', None)
        return kwargs

    def save(self, model):
        """
        提交模型，並返回模型實例
        :param model: 需要保存的模型實例
        """
        self._isinstance(model)
        db.session.add(model)
        db.session.commit()
        return model

    def save_all(self, model_list):
        for model in model_list:
            self._isinstance(model)
        db.session.add_all(model_list)
        db.session.commit()

    @staticmethod
    def transform_query_value(field, value, **kwargs):
        return field, value

    def to_filter(self, filters, tz=LOCAL_TZ, **kwargs):
        keys = {
            'k': lambda _attr, _value: _attr.ilike(f'%{_value}%'),
            'ipp': lambda _attr, _value: _attr.ilike(f'%{_value}'),
            'ie': lambda _attr, _value: _attr.ilike(f'{_value}%'),
            'in': lambda _attr, _value: _attr.in_(_value),
            'ge': lambda _attr, _value: _attr >= _value,
            'gt': lambda _attr, _value: _attr > _value,
            'ne': lambda _attr, _value: _attr != _value,
            'eq': lambda _attr, _value: _attr == _value,
            'lt': lambda _attr, _value: _attr < _value,
            'le': lambda _attr, _value: _attr <= _value,
            'dr': self.parse_dr,
        }
        model = self.__model__
        forbidden_params = self.__query_params_forbidden__
        ops = []

        for attr, value in filters.items():
            segments = [attr, 'eq']  # as default value
            for key in keys:
                if attr.endswith(f'_{key}'):
                    segments = attr.rsplit('_', 1)

            field, suffix = segments
            field, value = self.transform_query_value(field, value, suffix=suffix)

            if field in forbidden_params:
                continue
            if suffix in keys and hasattr(model, field):
                func = keys[suffix]
                v = func(getattr(model, field), value)
                if v is not None:
                    ops.append(v)
        return ops

    def search(self, filters, order_by='created', custom=None, sort_type='desc'):
        """
        預設時區為台北時間
        {
            'date_ge': '2022-10-1T01:45:36',
            'date_le': '2022-10-3T01:45:36'
        }
        or
        {
            'date_dr': '2022-10-1T01:45:36 ~ 2022-10-1T01:45:36',
        }
        """
        query = self.to_filter(filters or {})
        if custom:
            query.extend(custom)

        if not isinstance(order_by, list):
            _order_by = [getattr(getattr(self.__model__, order_by), sort_type)()]
        else:
            _order_by = map(lambda x: getattr(getattr(self.__model__, x), sort_type)(), order_by)
        return db.session.query(self.__model__).filter(and_(*query)).order_by(*_order_by)

    def all(self):
        db.session.commit()
        return db.session.query(self.__model__).all()

    def get(self, _id):
        return db.session.query(self.__model__).get(_id)

    def exists(self, **kwargs):
        return db.session.query(self.__model__.id).filter_by(**kwargs).count() > 0

    def count(self, **kwargs):
        return db.session.query(self.__model__.id).filter_by(**kwargs).count()

    def get_or_create(self, defaults=None, **kwargs):
        """
        如果模型不存在，可以通過defaults創建一個模型
        :param defaults:
        :param kwargs:
        :return:
        """
        obj = self.first(**kwargs)
        if not obj:
            return self.create(**dict(defaults or (), **kwargs)), True
        return obj, False

    def get_all(self, *_ids):
        """
        查找一批id的模型實例
        """
        return db.session.query(self.__model__).filter(self.__model__.id.in_(_ids)).all()

    def find(self, **kwargs):
        """查找模型數據"""
        return db.session.query(self.__model__).filter_by(**kwargs)

    def first(self, **kwargs):
        """返回查找數據結果的第一項"""
        return db.session.query(self.__model__).filter_by(**kwargs).first()

    def last(self, order_by='created', sort_type='desc', **kwargs):
        """
        返回查找數據結果的最後一項
        """
        if not isinstance(order_by, list):
            _order_by = [getattr(getattr(self.__model__, order_by), sort_type)()]
        else:
            _order_by = map(lambda x: getattr(getattr(self.__model__, x), sort_type)(), order_by)
        return db.session.query(self.__model__).filter_by(**kwargs).order_by(*_order_by).limit(1).first()

    def first_or_404(self, **kwargs):
        obj = self.first(**kwargs)
        if not obj:
            return abort(404)
        return obj

    def get_or_404(self, _id):
        """
        param _id: instance id
        """

        return db.session.query(self.__model__).get_or_404(_id)

    def new(self, **kwargs):
        """
        構建一個模型實例，但是不提交
        """
        return self.__model__(**self._preprocess_params(kwargs))

    def create(self, **kwargs):
        """
        創建一個實例
        """
        model = self.new(**kwargs)
        self.dispatch_model_event('pre_create', instance=model, **kwargs)
        instance = self.save(model)
        self.dispatch_model_event('created', instance=instance, **kwargs)
        return instance

    def dispatch(self, event, **kwargs):
        """觸發事件處理"""
        if hasattr(signals, event):
            getattr(signals, event).send(self, **kwargs)

    def dispatch_model_event(self, name_, **kwargs):
        """觸發模型事件"""
        event = '{model}_{event}'.format(
            model=self.__model__.__tablename__.lower(), event=name_)
        self.dispatch(event, **kwargs)

    def update(self, model, **kwargs):
        """更新實例

        :param model: 要更新的模型實例
        :param kwargs: 更新的參數
        """
        self._isinstance(model)
        for k, v in self._preprocess_params(kwargs).items():
            setattr(model, k, v)
        self.dispatch_model_event('pre_update', instance=model, **kwargs)
        instance = self.save(model)
        self.dispatch_model_event('updated', instance=instance, **kwargs)
        return instance

    def delete(self, model_or_id):
        if model_or_id is None:
            return
        model = model_or_id if isinstance(
            model_or_id, self.__model__) else self.get(model_or_id)
        self._isinstance(model)
        self.dispatch_model_event('pre_delete', instance=model)
        db.session.delete(model)
        db.session.commit()
        self.dispatch_model_event('deleted', instance=model)

    @staticmethod
    def parse_dr(attr, value, sep='~'):
        if sep not in value:
            return None
        start, end = [i.strip() for i in value.split(sep)]

        start = timetools.parse_time(start)
        end = timetools.parse_time(end)
        if start and end:
            return and_(start.shift('UTC').datetime <= attr, attr <= end.shift('UTC').datetime)
