from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class KramerController(Website):
    @http.route('/website/snippet/kramer/smart-search', type='json', auth='public', website=True)
    def smart_search(self, term=None, options=None):
        list_of_ids = http.request.env['smart.search'].query_with_params(term)
        products = http.request.env['product.template'].search_read([('id', 'in', list_of_ids)])


        return products