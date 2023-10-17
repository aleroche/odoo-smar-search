from odoo import api, fields, models, _
from odoo.addons.website.models.website import Website
from odoo.osv import expression


class WebsiteInheritKramer(Website):
    _inherit = "website"

    def _search_with_fuzzy(self, search_type, search, limit, order, options):
        fuzzy_term = False
        search_details = self._search_get_details(search_type, order, options)

        search_details[0]['base_domain'].append(search)

        count, results = self._search_exact(search_details, search, limit, order)
        return count, results, fuzzy_term

    def _search_exact(self, search_details, search, limit, order):
        all_results = []
        total_count = 0

        for search_detail in search_details:
            model = self.env[search_detail['model']]
            results, count = self._kramer_search_fetch(search_detail, limit, order)
            search_detail['results'] = results
            total_count += count
            search_detail['count'] = count
            all_results.append(search_detail)
        return total_count, all_results

    def _kramer_search_fetch(self, search_detail, limit, order):
        fields = search_detail['search_fields']
        domain = search_detail['base_domain']
        base_domain = expression.AND(domain)
        model = self.env['product.template'].sudo() if search_detail.get('requires_sudo') else self.env[
            'product.template']

        results = model.search(base_domain)

        count = model.search_count(base_domain)
        return results, count
