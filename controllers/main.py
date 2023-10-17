
from odoo import http
from odoo.addons.website.controllers.main import Website



class KramerController(Website):
    @http.route('/website/snippet/kramer/smart-search', type='json', auth='public', website=True)
    def smart_search(self, term=None, options=None):
        list_of_ids, sql = http.request.env['smart.search'].query_with_params(term)
        products = http.request.env['product.template'].search_read([('id', 'in', list_of_ids)])
        return {
            'products': products,
            'sql_ai': sql
        }

    @http.route('/website/snippet/kramer/search', type='http', auth='public', website=True)
    def search(self, page=1, search='', search_type='all', **kw):
        if not search:
            return http.request.render("smart_search.kramer_search_page")

        list_of_ids, sql = http.request.env['smart.search'].query_with_params(search)
        data = http.request.env['product.template'].search_read([('id', 'in', list_of_ids)])

        search_count = len(data)

        values = {
            'results': data,
            'parts': {},
            'search': search,
            'fuzzy_search': False,
            'search_count': search_count,
        }
        return http.request.render("smart_search.kramer_search_page", values)








