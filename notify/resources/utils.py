from flask import request
from flask_restplus import fields, Namespace

namespace = Namespace('Base', description='Base schema')

filters = namespace.model('Filters', {
    'field': fields.String(),
    'op': fields.String(),
    'value': fields.String(),
})

search = namespace.model('Search', {
    'filters': fields.Nested(filters),
    'order_by': fields.String(default='created')
})

base_fields = namespace.model('Base', {
    'id': fields.String(readonly=True),
    'updated': fields.DateTime(dt_format='rfc822', readonly=True),
    'created': fields.DateTime(dt_format='rfc822', readonly=True),
})


def paginate_fields(current_page, page_obj):
    return {"next": page_obj.has_next,
            "prev": page_obj.has_prev,
            "current": current_page,
            "pages": page_obj.pages,
            "per_page": page_obj.per_page,
            "total": page_obj.total}


class SearchParam:
    def __init__(self, model):
        self.model = model

    def paginate_fields_with_filter(self, current_page, page_obj):
        return {"next": page_obj.has_next,
                "total": self.model.query.count(),
                "prev": page_obj.has_prev,
                "current": current_page,
                "pages": page_obj.pages,
                "filters": request.json.get('filters'),
                "per_page": page_obj.per_page,
                "filtered": page_obj.total}
