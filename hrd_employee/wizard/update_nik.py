# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import tools

class update_nik(osv.osv_memory):
	_name = "update.nik"
	_description = "update NIK"
	_columns = {
		'employee_id' : fields.many2one('hr.employee','employee'),
		'nik_br' : fields.char('NIK Baru',required=True),
	}
	_defaults = {
		'employee_id' : lambda self, cr, uid, ctx: ctx and ctx.get('active_id', False) or False,
		'nik_br': lambda self, cr, uid, context={}: self.pool.get('ir.sequence').get(cr, uid, 'hr.employee.nik'),
	}

	def change_nik(self, cr, uid, ids, context=None):
		""" Changes the Product Quantity by making a Physical Inventory.
		@param self: The object pointer.
		@param cr: A database cursor
		@param uid: ID of the user currently logged in
		@param ids: List of IDs selected
		@param context: A standard dictionary
		@return:
		"""
		if context is None:
			context = {}

		employee_obj = self.pool.get('hr.employee')

		for data in self.browse(cr, uid, ids, context=context):
			ctx = context.copy()
			ctx['name_related'] = data.nik_br
			employee_obj.write(cr,uid,[data.employee_id.id],{'name_related':data.nik_br,
															'nik':data.employee_id.name_related,
															'nik1':data.employee_id.nik,
															'nik2':data.employee_id.nik1,
															'nik3':data.employee_id.nik2,
															'nik4':data.employee_id.nik3,
															'nik5':data.employee_id.nik4,
															'nik6':data.employee_id.nik5,
															'nik7':data.employee_id.nik6,
															'nik8':data.employee_id.nik7,
															'nik9':data.employee_id.nik8,
															'nik10':data.employee_id.nik9,
															'nik11':data.employee_id.nik10,
															'nik12':data.employee_id.nik11,
															'nik13':data.employee_id.nik12,
															'nik14':data.employee_id.nik13,
															'nik15':data.employee_id.nik14,
															'nik16':data.employee_id.nik15,
															'nik17':data.employee_id.nik16,
															'nik18':data.employee_id.nik17,
															'nik19':data.employee_id.nik18,
															'nik20':data.employee_id.nik19,
															},context=context)
		return True