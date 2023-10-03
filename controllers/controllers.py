# -*- coding: utf-8 -*-
import json
import re
from odoo import http
from odoo.http import request
from textwrap import shorten
from odoo.tools import OrderedSet, escape_psql, html_escape as escape
from odoo.addons.website.controllers.main import Website


class SmartSearch(Website):
    @http.route('/website/snippet/smart-search', type='json', auth='public', website=True)
    def smart_search(self, search_type=None, term=None, order=None, limit=5, max_nb_chars=999, options=None):

        order = self._get_search_order(order)

        options = options or {}

        if 'display_currency' not in options:
            options['display_currency'] = request.website.currency_id

        results_count, search_results, fuzzy_term = request.website._search_with_fuzzy(
            search_type, term, limit, order, options)

        list_of_ids = http.request.env['smart.search'].query_with_params('desk')

        for sr in search_results:
            if sr['model'] == 'product.template':
                sr['base_domain'][0].append(('product_tmpl_id', 'in', list_of_ids))
                # print("SSSSSSSSSSSSSS", sr['base_domain'][0])

        # print("RESULT COUNTS", results_count)
        # print("SEARCH_RESULTS", search_results)
        # print("FUZZY_TERM", fuzzy_term)
        # return
        if not results_count:
            return {
                'results': [],
                'results_count': 0,
                'parts': {},
            }
        term = fuzzy_term or term
        search_results = request.website._search_render_results(search_results, limit)

        print("DDDDDDDDDDDDDDDDDDDDDDDDD", search_results)

        mappings = []
        results_data = []
        for search_result in search_results:
            results_data += search_result['results_data']
            mappings.append(search_result['mapping'])
        if search_type == 'all':
            # Only supported order for 'all' is on name
            results_data.sort(key=lambda r: r.get('name', ''), reverse='name desc' in order)
        results_data = results_data[:limit]
        result = []
        for record in results_data:
            mapping = record['_mapping']
            mapped = {
                '_fa': record.get('_fa'),
            }
            for mapped_name, field_meta in mapping.items():
                value = record.get(field_meta.get('name'))
                if not value:
                    mapped[mapped_name] = ''
                    continue
                field_type = field_meta.get('type')
                if field_type == 'text':
                    if value and field_meta.get('truncate', True):
                        value = shorten(value, max_nb_chars, placeholder='...')
                    if field_meta.get('match') and value and term:
                        pattern = '|'.join(map(re.escape, term.split()))
                        if pattern:
                            parts = re.split(f'({pattern})', value, flags=re.IGNORECASE)
                            if len(parts) > 1:
                                value = request.env['ir.ui.view'].sudo()._render_template(
                                    "website.search_text_with_highlight",
                                    {'parts': parts}
                                )
                                field_type = 'html'

                if field_type not in ('image', 'binary') and ('ir.qweb.field.%s' % field_type) in request.env:
                    opt = {}
                    if field_type == 'monetary':
                        opt['display_currency'] = options['display_currency']
                    value = request.env[('ir.qweb.field.%s' % field_type)].value_to_html(value, opt)
                mapped[mapped_name] = escape(value)
            result.append(mapped)

        return {
            'results': result,
            'results_count': results_count,
            'parts': {key: True for mapping in mappings for key in mapping},
            'fuzzy_search': fuzzy_term,
        }
