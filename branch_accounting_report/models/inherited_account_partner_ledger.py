# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from datetime import timedelta


class AccountPartnerLedger(models.AbstractModel):
    _inherit = 'account.partner.ledger'

    def _do_query_group_by_account(self, options, line_id):
        account_types = [a.get('id') for a in options.get('account_type') if a.get('selected', False)]
        if not account_types:
            account_types = [a.get('id') for a in options.get('account_type')]
        select = ',COALESCE(SUM(\"account_move_line\".debit-\"account_move_line\".credit), 0),SUM(\"account_move_line\".debit),SUM(\"account_move_line\".credit)'
        if options.get('cash_basis'):
            select = select.replace('debit', 'debit_cash_basis').replace('credit', 'credit_cash_basis')
        sql = "SELECT \"account_move_line\".partner_id%s FROM %s WHERE %s%s AND \"account_move_line\".partner_id IS NOT NULL GROUP BY \"account_move_line\".partner_id"
        tables, where_clause, where_params = self.env['account.move.line']._query_get([('account_id.internal_type', 'in', account_types)])
        line_clause = line_id and ' AND \"account_move_line\".partner_id = ' + str(line_id) or ''
        if options.get('unreconciled'):
            line_clause += ' AND \"account_move_line\".full_reconcile_id IS NULL'
        if options.get('branch'):
            where_clause += 'and ("account_move_line"."branch_id" in ('
            for a in range(len(options.get('branch'))):
                where_clause += '%s,'
            where_clause = where_clause[:-1]

            where_clause += '))'
            # branch_list = [1,2]
            for a in options.get('branch'):
                where_params.append(int(a))
        query = sql % (select, tables, where_clause, line_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        results = dict([(k[0], {'balance': k[1], 'debit': k[2], 'credit': k[3]}) for k in results])
        return results

    def _group_by_partner_id(self, options, line_id):
        partners = {}
        account_types = [a.get('id') for a in options.get('account_type') if a.get('selected', False)]
        if not account_types:
            account_types = [a.get('id') for a in options.get('account_type')]
        date_from = options['date']['date_from']
        results = self._do_query_group_by_account(options, line_id)
        initial_bal_results = self.with_context(
            date_from=False, date_to=fields.Date.from_string(date_from) + timedelta(days=-1)
        )._do_query_group_by_account(options, line_id)
        context = self.env.context
        base_domain = [('date', '<=', context['date_to']), ('company_id', 'in', context['company_ids']), ('account_id.internal_type', 'in', account_types)]
        base_domain.append(('date', '>=', date_from))
        if context['state'] == 'posted':
            base_domain.append(('move_id.state', '=', 'posted'))
        if options.get('unreconciled'):
            base_domain.append(('full_reconcile_id', '=', False))
        for partner_id, result in results.items():
            domain = list(base_domain)  # copying the base domain
            domain.append(('partner_id', '=', partner_id))
            partner = self.env['res.partner'].browse(partner_id)
            partners[partner] = result
            partners[partner]['initial_bal'] = initial_bal_results.get(partner.id, {'balance': 0, 'debit': 0, 'credit': 0})
            partners[partner]['balance'] += partners[partner]['initial_bal']['balance']
            partners[partner]['total_lines'] = 0
            if options.get('branch'):
                branch_list = []
                for a in options.get('branch'):
                    branch_list.append(int(a))
                domain.append(('branch_id','in',branch_list))
            if not context.get('print_mode'):
                partners[partner]['total_lines'] = self.env['account.move.line'].search_count(domain)
                offset = int(options.get('lines_offset', 0))
                limit = self.MAX_LINES
                partners[partner]['lines'] = self.env['account.move.line'].search(domain, order='date,id', limit=limit, offset=offset)
            else:
                partners[partner]['lines'] = self.env['account.move.line'].search(domain, order='date,id')

        # Add partners with an initial balance != 0 but without any AML in the selected period.
        prec = self.env.user.company_id.currency_id.rounding
        missing_partner_ids = set(initial_bal_results.keys()) - set(results.keys())
        for partner_id in missing_partner_ids:
            if not float_is_zero(initial_bal_results[partner_id]['balance'], precision_rounding=prec):
                partner = self.env['res.partner'].browse(partner_id)
                partners[partner] = {'balance': 0, 'debit': 0, 'credit': 0}
                partners[partner]['initial_bal'] = initial_bal_results[partner_id]
                partners[partner]['balance'] += partners[partner]['initial_bal']['balance']
                partners[partner]['lines'] = self.env['account.move.line']
                partners[partner]['total_lines'] = 0
        return partners