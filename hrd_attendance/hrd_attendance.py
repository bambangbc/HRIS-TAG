from openerp.osv import fields, osv
from datetime import datetime
from datetime import timedelta
from openerp.tools.translate import _

class employee(osv.osv):
	_name = "hr.employee"
	_inherit = 'hr.employee'

	_columns = {
		'fingerprint_code' : fields.char('Fingerprint ID'),
		'no_mesin' : fields.integer('No Mesin'),
	}

	
class hr_attendance(osv.osv):
	'''
	PPI Absensi
	'''
	_name = "hr.attendance"
	_inherit = "hr.attendance"
	_description = "Attendance for PPI"	

	# def _fill_attendance(self, cr, uid, vals, context=None):
	# 	em = self.pool.get('hr.employee')
	# 	ff = em.search(cr, uid, [('fingerprint_code','=',vals['fingerprint_code'])], context=context)
	# 	if ff == []:
	# 		#raise osv.except_osv(_('Fingerprint Error!'), _("Kode Fingerprint tidak ada!"))
	# 		vals['employee_id'] = False
	# 	else :	
	# 		vals['employee_id']=ff[0]
	# 	vals['name_date']=vals['name'][:10]
	# 	return vals

	# def create(self, cr, uid, vals, context=None):

	# 	vals = self._fill_attendance(cr, uid, vals, context=None)
	# 	date = vals['name']
	# 	date_akhir = datetime.strptime(date,"%Y-%m-%d %H:%M:%S")
	# 	date_y = datetime.strptime(date,"%Y-%m-%d %H:%M:%S").year
	# 	date_m = datetime.strptime(date,"%Y-%m-%d %H:%M:%S").month
	# 	date_d = datetime.strptime(date,"%Y-%m-%d %H:%M:%S").day
	# 	dates =str(date_y) + "-" + str(date_m) + '-' + str(date_d)
	# 	employee = vals["employee_id"]
		
	# 	if any('no_mesin' in att for att in vals) and vals['no_mesin'] <> '0':
	# 		new_id = super(hr_attendance,self).create(cr,uid,vals,context=context)
	# 		return new_id
	# 	else :
	# 		return super(hr_attendance,self).create(cr,uid,vals,context=context)

	_columns = {
		"fingerprint_code" : fields.integer('Fingerprint ID', required=True, help="Fingerprint ID"),
		"binary_action": fields.selection([('1','Sign Out'),('0','Sign In'),('2','Other')],'Kehadiran'),
		"no_mesin" : fields.char('No Mesin',size=4, help="Apakah dimport?", required=True),
		"name_date": fields.char('Date', readonly=True),
		'action_desc': fields.many2one("hr.action.reason", "Action Reason", help='Specifies the reason for Signing In/Signing Out in case of extra hours.'),
		'employee_id': fields.many2one('hr.employee', "Employee", required=False, select=True),
		'action': fields.selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('action','Action')], 'Action', required=False),
	}

	_defaults = {
		'no_mesin':'0',
	}

hr_attendance()
