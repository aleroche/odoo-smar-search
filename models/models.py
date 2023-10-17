# -*- coding: utf-8 -*-
import re
import os
from langchain import SQLDatabase
from odoo import models, fields, api
from langchain.chains import create_sql_query_chain
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv


load_dotenv()


class SmartSearch(models.Model):
    _name = "smart.search"
    _description = "An inteligent search with IA"

    @api.model
    def query_with_params(self, question, *args, **kwargs):
        list_of_ids = []

        # SOTO METHOD
        sql_string = self.get_ai_query(question)
        sql_string_formatted = self.convert_string(sql_string)
        # END SOTO METHOD

        # sql_string_formatted = f"select pt.id, pt.name->>'en_US' as name, description from product_template pt where pt.name->>'en_US' ilike '%{question}%' limit 20 "
        self.env.cr.execute(sql_string_formatted)
        result = self.env.cr.dictfetchall()
        for res in result:
            list_of_ids.append(res['id'])

        return list_of_ids, sql_string_formatted

    def convert_string(self, sql_string):
        select_clause = re.search(r'SELECT(.+?)FROM', sql_string, flags=re.IGNORECASE | re.DOTALL)
        select_part = ''
        where_part = ''

        # Todo:  check if select_clause is not null

        if select_clause:
            select_part = select_clause.group(1)
            select_part = re.sub(r'(\w+\.)', '', select_part)
            select_part = select_part.strip()

        where_clause = re.search(r'WHERE(.+?)LIMIT|WHERE(.+?)$', sql_string, flags=re.IGNORECASE | re.DOTALL)

        # Todo: check if select_clause is not null

        if where_clause:
            where_part = where_clause.group(1) or where_clause.group(2)
            where_part = re.sub(r'(\w+\.)', '', where_part)
            where_part = where_part.strip()

        sql_resul = f"SELECT id, {select_part} FROM product_template WHERE {where_part} LIMIT 20"

        return sql_resul

    def get_ai_query(self, question):
        db = SQLDatabase.from_uri(
            os.environ['POSTGRES_URL'],
            schema='ai',
        )
        chain = create_sql_query_chain(ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"), db, k=24)
        response = chain.invoke({"question": question})
        return response

    def query(self):
        list_of_ids = []
        for record in self:
            # question = record.name
            # sql_string = self.get_ai_query(question)
            # sql_string_formatted = self.convert_string(sql_string)

            # record.sql_format = sql_string_formatted
            sql_string_formatted = f"select id, name, description from product_template limit 20"
            self.env.cr.execute(sql_string_formatted)
            result = self.env.cr.dictfetchall()
            for res in result:
                list_of_ids.append(res['id'])

            # products_ids = self.env['product.product'].search([('product_tmpl_id', 'in', list_of_ids)])
            # products = self.env['product.product'].browse(products_ids)
            # print("PRODUCTS", products)

            actions = {
                'name': False,
                'type': 'ir.actions.act_window',
                'res_model': 'product.product',
                'view_mode': 'kanban',
                'domain': [('product_tmpl_id', 'in', list_of_ids)]
            }

            # action = self.env.ref('product_kanban_view').read()[0]
            # action['domain'] = [('field1', '=', 'value1'), ('field2', '>', 100)]

            # Handle case when action is not found

            return actions


