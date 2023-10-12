from odoo import http
from odoo.addons.website.controllers.main import Website
from odoo.addons.portal.controllers.portal import pager as portal_pager


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
        print("PAGE", page)
        print("SEARCH", search)
        print("SEARCH_TYPE", search_type)
        print("KW", kw)
        if not search:
            return http.request.render("smart_search.kramer_search_page")

        list_of_ids, sql = http.request.env['smart.search'].query_with_params(search)
        data = http.request.env['product.template'].search_read([('id', 'in', list_of_ids)])

        print("DATA", data)
        # results = data.get('results', [])
        search_count = len(data)
        # parts = data.get('parts', {})

        # print("=================")
        # print("RESULTS", results)
        print("SEARCH_COUNT", search_count)
        # print("PARTS", parts)


        #
        #
        #
        values = {
            'results': data,
            'parts': {},
            'search': search,
            'fuzzy_search': False,
            'search_count': search_count,
        }
        return http.request.render("smart_search.kramer_search_page", values)
