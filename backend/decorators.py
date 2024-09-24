from functools import wraps

from flask import request, Response, jsonify
from voluptuous import Schema, Invalid
from werkzeug.exceptions import HTTPException

from backend.exceptions import ValidationError


def data_schema(schema: Schema, is_replace=False):
    """request json schema"""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # FIXME 修正 load_json 我記得有新的寫法
                json_data = schema(load_json(request.json))
                if is_replace:
                    request.json_data = json_data
            except Invalid as e:
                raise ValidationError(f'輸入參數錯誤: {e}')
            except Exception as e:
                raise ValidationError('請輸入正確參數')

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def paginate(default_per_page=10, max_per_page=50, hidden=None, hidden_info=None, public=None, extra=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            page = request.args.get('page', 1, type=int)
            per_page = default_per_page
            default_max_per_page = 100

            if request.args.get('per_page'):
                per_page = min(request.args.get('per_page', max_per_page, type=int), default_max_per_page)

            query = f(*args, **kwargs)

            empty_result = {
                'data': [],
                'meta': {
                    'page': 1,
                    'per_page': per_page,
                    'total': 0,
                    'pages': 1,
                },
                'code': 200
            }

            if query is None:
                return jsonify(empty_result)

            try:
                result = query.paginate(page, per_page)
            except HTTPException:
                return jsonify(empty_result)

            pages = {
                'page': page,  # 當前頁
                'per_page': per_page,  # 每頁筆數
                'total': result.total,  # 總筆數
                'pages': result.pages,  # 共幾頁
            }
            data = []
            if hidden_info:
                for r, v in result.items:
                    tmp = {}
                    for obj in r:
                        tmp.update(obj.to_json(hidden=hidden_info.get(obj.__tablename__, None), public=public))
                    data.append(tmp)
            else:
                data = [r.to_json(hidden=hidden, public=public, extra=extra) for r in result.items]

            return jsonify({
                'data': data,
                'meta': pages,
                'code': 200,
            })

        return wrapped

    return decorator


def route(bp, *args, **kwargs):
    """
    被裝飾的function，無須登入
    """
    kwargs.setdefault('strict_slashes', False)

    def decorator(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            status = 200
            rv = f(*args, **kwargs)
            rv = rv if rv else {}

            if isinstance(rv, Response):
                return rv

            if isinstance(rv, tuple):
                status = rv[1]
                rv = rv[0] if rv[0] else {}
                if isinstance(rv, Response):
                    return rv, status

            return jsonify(dict(code=status, data=rv)), status

        return wrapper

    return decorator