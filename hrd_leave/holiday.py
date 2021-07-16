from openerp.osv import fields, osv
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _

class hr_holiday(osv.osv):
	_inherit = "hr.holidays.status"

	_columns = {
		'double_validation': fields.boolean('Apply Six Validation', help="When selected, the Allocation/Leave Requests for this type require a second validation to be approved."),
	}
class hr_holiday(osv.osv):
	_inherit = "hr.holidays"

	_columns = {
		'holiday_type': fields.selection([('employee','By Employee'),('category','By Employee Tag')], 'Allocation Mode', help='By Employee: Allocation/Request for individual Employee, By Employee Tag: Allocation/Request for group of employees in category', required=True),
		'state': fields.selection([('draft', 'To Submit'), ('cancel', 'Cancelled'),('confirm', 'first Approved'), ('approve1', 'second Approved'), ('approve2', 'third Approved'), ('approve3', 'fourth Approved'), ('refuse', 'Refused'), ('validate', 'Approved')],
			'Status', readonly=True, track_visibility='onchange', copy=False,
			help='The status is set to \'To Submit\', when a holiday request is created.\
			\nThe status is \'To Approve\', when holiday request is confirmed by user.\
			\nThe status is \'Refused\', when holiday request is refused by manager.\
			\nThe status is \'Approved\', when holiday request is approved by manager.'),
		}

	def holidays_refuse(self, cr, uid, ids, context=None):
		self.write(cr,uid,ids,{'state':'refuse'})

	def confirm(self, cr, uid, ids, context=None):
		self.write(cr,uid,ids,{'state':'confirm'})

	def confirm_app(self, cr, uid, ids, context=None):
		if self.browse(cr,uid,ids).employee_id.user_id.id == uid :
			  raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve'))
		self.write(cr,uid,ids,{'state':'approve1'})

	def confirm_app2(self, cr, uid, ids, context=None):
		if self.browse(cr,uid,ids).employee_id.user_id.id == uid :
			  raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve'))
		self.write(cr,uid,ids,{'state':'approve2'})

	def confirm_app3(self, cr, uid, ids, context=None):
		if self.browse(cr,uid,ids).employee_id.user_id.id == uid :
			  raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve'))
		self.write(cr,uid,ids,{'state':'approve3'})

	def confirm_app4(self, cr, uid, ids, context=None):
		obj = self.browse(cr,uid,ids)
		obj_emp = self.pool.get('hr.employee')
		obj_con = self.pool.get('hr.contract')
		dates_hol = obj.date_from[:10]
		clause_1 = ['&',('date_start','<=', dates_hol),'|',('date_end', '=', False),('date_end','>=', dates_hol)]
		clause_final = [('employee_id', '=', obj.employee_id.id)] + clause_1 
		src_con = obj_con.search(cr, uid, clause_final, context=context)
		mth = datetime.strptime(obj.date_from,"%Y-%m-%d %H:%M:%S")+timedelta(hours=7)
		if src_con or obj.holiday_type == 'category':
			for src_con in obj_con.browse(cr,uid,src_con):
				if src_con.flat == False :
					if datetime.now().day > 12 and datetime.now().month > mth.month and uid != 1 :
						raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve Karna Sudah Lewat Tannggal 12'))
				else :
					if datetime.now().month >= datetime.strptime(obj.date_from,"%Y-%m-%d %H:%M:%S").month and datetime.now().year >= datetime.strptime(obj.date_from,"%Y-%m-%d %H:%M:%S").year and uid != 1 :
						if datetime.now().day > 21 and datetime.strptime(obj.date_from,"%Y-%m-%d %H:%M:%S").day < 21 :
							raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve Karna Sudah Lewat Tannggal 21'))
				if self.browse(cr,uid,ids).employee_id.user_id.id == uid :
					  raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve'))
			self.write(cr,uid,ids,{'state':'validate'})
		else :
			raise osv.except_osv(_('Warning!'),_('Tidak Ada Kontrak / Kontrak Sudah Habis'))

	def confirm_app5(self, cr, uid, ids, context=None):
		if self.browse(cr,uid,ids).employee_id.user_id.id == uid :
			  raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve'))
		self.write(cr,uid,ids,{'state':'validate1'})

	def confirm_app6(self, cr, uid, ids, context=None):
		obj_emp = self.pool.get('hr.employee')
		obj = self.browse(cr,uid,ids)
		if self.browse(cr,uid,ids).employee_id.user_id.id == uid :
			  raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve'))
		# if obj.holiday_type == 'category':
		# 	emp_ids = obj_emp.search(cr, uid, [('category_ids', 'child_of', [obj.category_id.id])])
		# 	leave_ids = []
		# 	for emp in obj_emp.browse(cr, uid, emp_ids):
		# 		domain = [
		# 		('date_from', '<=', obj.date_to),
		# 		('date_to', '>=', obj.date_from),
		# 		('employee_id', '=', emp.id),
		# 		('state', 'not in', ['cancel', 'refuse']),
		# 		]
		# 		nholidays = self.search_count(cr, uid, domain, context=context)
		# 		if not nholidays :
		# 			vals = {
		# 				'name': obj.name,
		# 				'type': obj.type,
		# 				'holiday_type': 'employee',
		# 				'holiday_status_id': obj.holiday_status_id.id,
		# 				'date_from': obj.date_from,
		# 				'date_to': obj.date_to,
		# 				'notes': obj.notes,
		# 				'number_of_days_temp': obj.number_of_days_temp,
		# 				'parent_id': obj.id,
		# 				'employee_id': emp.id,
		# 				'state':'validate',
		# 			}
		# 			leave_ids.append(self.create(cr, uid, vals, context=None))
		# 	for leave_id in leave_ids:
		# 	   for sig in ('confirm', 'validate', 'second_validate'):
		# 			self.signal_workflow(cr, uid, [leave_id], sig)
		# 	self.write(cr,uid,ids,{'state':'validate'})
		# else:
		self.write(cr,uid,ids,{'state':'validate'})

hr_holiday()