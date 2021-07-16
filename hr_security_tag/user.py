from openerp.osv import fields, osv

class res_users(osv.osv):
	_inherit = "res.users"

	_columns = {
		'employee_id' : fields.many2one('hr.employee',"Employee"),
	}
res_users()