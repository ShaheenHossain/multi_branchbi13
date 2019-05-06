# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class ClosedSessionReport(models.TransientModel):
	_name = 'closed.session.report'
	
	start_date = fields.Date(required=True, default=datetime.now().date())
	end_date = fields.Date(required=True, default=datetime.now().date())
	company_id = fields.Many2one("res.company",string="Company",default=1)
	pos_config_ids = fields.Many2many('pos.config', 'pos_config_session',string="POS Configs")
	pos_session_ids = fields.Many2many('pos.session', 'pos_sessions',string="POS Sessions")
	
	@api.onchange('start_date')
	def _onchange_start_date(self):
		if self.start_date and self.end_date and self.end_date < self.start_date:
			self.end_date = self.start_date

	@api.onchange('end_date')
	def _onchange_end_date(self):
		if self.end_date and self.end_date < self.start_date:
			self.start_date = self.end_date

	@api.onchange('pos_config_ids')
	def _onchange_pos_config_ids(self):
		lst =[]
		for i in self.pos_config_ids:
			for j in i.session_ids:
				if j.state == 'closed':
					lst.append(j.id)
		return {'domain': {'pos_session_ids': [('id', 'in', lst)]}}

	@api.multi
	def generate_pos_report(self):
		if (not self.env.user.company_id.logo):
			raise UserError(_("You have to set a logo or a layout for your company."))
		elif (not self.env.user.company_id.external_report_layout_id):
			raise UserError(_("You have to set your reports's header and footer layout."))
		data = {'date_start': self.start_date, 'date_stop': self.end_date, 'config_ids': self.pos_config_ids.ids,'session_ids':self.pos_session_ids.ids}
		return self.env.ref('bi_pos_multi_ticket.pos_report').report_action([], data=data)

