from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute
from datetime import datetime
from werkzeug.exceptions import NotFound
from odoo import fields, http, tools, _
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.osv import expression
from odoo.tools import lazy
from collections import defaultdict
from itertools import product as cartesian_product


class WebsiteSaleInherit(WebsiteSale):
    @http.route()
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = 0
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = 0

        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        website = request.env['website'].get_current_website()

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = website.shop_ppg or 20

        ppr = website.shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL('/shop',
                        **self._shop_get_query_url_kwargs(category and int(category), search, min_price, max_price,
                                                          **post))

        now = datetime.timestamp(datetime.now())
        pricelist = request.env['product.pricelist'].browse(request.session.get('website_sale_current_pl'))
        if not pricelist or request.session.get('website_sale_pricelist_time',
                                                0) < now - 60 * 60:  # test: 1 hour in session

            pricelist = website.get_current_pricelist()
            request.session['website_sale_pricelist_time'] = now
            request.session['website_sale_current_pl'] = pricelist.id

        request.update_context(pricelist=pricelist.id, partner=request.env.user.partner_id)

        filter_by_price_enabled = website.is_view_active('website_sale.filter_products_price')
        if filter_by_price_enabled:
            company_currency = website.company_id.currency_id
            conversion_rate = request.env['res.currency']._get_conversion_rate(
                company_currency, pricelist.currency_id, request.website.company_id, fields.Date.today())
        else:
            conversion_rate = 1

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        options = self._get_search_options(
            category=category,
            attrib_values=attrib_values,
            pricelist=pricelist,
            min_price=min_price,
            max_price=max_price,
            conversion_rate=conversion_rate,
            **post
        )

        list_of_ids, sql = http.request.env['smart.search'].query_with_params(search)

        product_domain = [('id', 'in', list_of_ids)]

        fuzzy_search_term, product_count, search_product = self._custom_shop_lookup_products(attrib_set, options, post,
                                                                                             product_domain, website)

        filter_by_price_enabled = website.is_view_active('website_sale.filter_products_price')
        if filter_by_price_enabled:
            # TODO Find an alternative way to obtain the domain through the search metadata.
            Product = request.env['product.template'].with_context(bin_size=True)

            # Todo: Agregar el dominio de template id algo asi: domain = [('id', 'in', list_of_ids)]
            domain = self._get_custom_search_domain(product_domain, category, attrib_values)

            # This is ~4 times more efficient than a search for the cheapest and most expensive products
            from_clause, where_clause, where_params = Product._where_calc(domain).get_sql()
            query = f"""
                        SELECT COALESCE(MIN(list_price), 0) * {conversion_rate}, COALESCE(MAX(list_price), 0) * {conversion_rate}
                          FROM {from_clause}
                         WHERE {where_clause}
                    """
            request.env.cr.execute(query, where_params)
            available_min_price, available_max_price = request.env.cr.fetchone()

            if min_price or max_price:
                # The if/else condition in the min_price / max_price value assignment
                # tackles the case where we switch to a list of products with different
                # available min / max prices than the ones set in the previous page.
                # In order to have logical results and not yield empty product lists, the
                # price filter is set to their respective available prices when the specified
                # min exceeds the max, and / or the specified max is lower than the available min.
                if min_price:
                    min_price = min_price if min_price <= available_max_price else available_min_price
                    post['min_price'] = min_price
                if max_price:
                    max_price = max_price if max_price >= available_min_price else available_max_price
                    post['max_price'] = max_price

        website_domain = website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain
            ).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = lazy(lambda: Category.search(categs_domain))

        if category:
            url = "/shop/category/%s" % slug(category)

        pager = website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        products = search_product[offset:offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = lazy(lambda: ProductAttribute.search([
                ('product_tmpl_ids', 'in', search_product.ids),
                ('visibility', '=', 'visible'),
            ]))
        else:
            attributes = lazy(lambda: ProductAttribute.browse(attributes_ids))

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'
            request.session['website_sale_shop_layout_mode'] = layout_mode

        products_prices = lazy(lambda: products._get_sales_prices(pricelist))

        values = {
            'search': fuzzy_search_term or search,
            'original_search': fuzzy_search_term and search,
            'order': post.get('order', ''),
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_product': search_product,
            'search_count': product_count,  # common for all searchbox
            'bins': lazy(lambda: TableCompute().process(products, ppg, ppr)),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'products_prices': products_prices,
            'get_product_prices': lambda product: lazy(lambda: products_prices[product.id]),
            'float_round': tools.float_round,
        }
        if filter_by_price_enabled:
            values['min_price'] = min_price or available_min_price
            values['max_price'] = max_price or available_max_price
            values['available_min_price'] = tools.float_round(available_min_price, 2)
            values['available_max_price'] = tools.float_round(available_max_price, 2)
        if category:
            values['main_object'] = category
        values.update(self._get_additional_shop_values(values))
        return request.render("website_sale.products", values)

    def _custom_shop_lookup_products(self, attrib_set, options, post, domain, website):
        # No limit because attributes are obtained from complete product list

        print("DOMAIN", domain)
        product_count, details, fuzzy_search_term = website._search_with_fuzzy("products_only", domain, limit=None,
                                                                               order=self._get_search_order(post),
                                                                               options=options)

        search_result = details[0].get('results', request.env['product.template']).with_context(bin_size=True)

        if attrib_set:
            # Attributes value per attribute
            attribute_values = request.env['product.attribute.value'].browse(attrib_set)
            values_per_attribute = defaultdict(lambda: request.env['product.attribute.value'])
            # In case we have only one value per attribute we can check for a combination using those attributes directly
            multi_value_attribute = False
            for value in attribute_values:
                values_per_attribute[value.attribute_id] |= value
                if len(values_per_attribute[value.attribute_id]) > 1:
                    multi_value_attribute = True

            def filter_template(template, attribute_values_list):
                # Transform product.attribute.value to product.template.attribute.value
                attribute_value_to_ptav = dict()
                for ptav in template.attribute_line_ids.product_template_value_ids:
                    attribute_value_to_ptav[ptav.product_attribute_value_id] = ptav.id
                possible_combinations = False
                for attribute_values in attribute_values_list:
                    ptavs = request.env['product.template.attribute.value'].browse(
                        [attribute_value_to_ptav[val] for val in attribute_values if val in attribute_value_to_ptav]
                    )
                    if len(ptavs) < len(attribute_values):
                        # In this case the template is not compatible with this specific combination
                        continue
                    if len(ptavs) == len(template.attribute_line_ids):
                        if template._is_combination_possible(ptavs):
                            return True
                    elif len(ptavs) < len(template.attribute_line_ids):
                        if len(attribute_values_list) == 1:
                            if any(template._get_possible_combinations(necessary_values=ptavs)):
                                return True
                        if not possible_combinations:
                            possible_combinations = template._get_possible_combinations()
                        if any(len(ptavs & combination) == len(ptavs) for combination in possible_combinations):
                            return True
                return False

            # If multi_value_attribute is False we know that we have our final combination (or at least a subset of it)
            if not multi_value_attribute:
                possible_attrib_values_list = [attribute_values]
            else:
                # Cartesian product from dict keys and values
                possible_attrib_values_list = [request.env['product.attribute.value'].browse([v.id for v in values]) for
                                               values in cartesian_product(*values_per_attribute.values())]

            search_result = search_result.filtered(lambda tmpl: filter_template(tmpl, possible_attrib_values_list))
        return fuzzy_search_term, product_count, search_result

    def _get_custom_search_domain(self, product_domain, category, attrib_values):
        domains = [request.website.sale_product_domain()]

        if product_domain:
            domains[0].append(product_domain[0])

        if category:
            domains.append([('public_categ_ids', 'child_of', int(category))])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domains.append([('attribute_line_ids.value_ids', 'in', ids)])
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domains.append([('attribute_line_ids.value_ids', 'in', ids)])

        return expression.AND(domains)
