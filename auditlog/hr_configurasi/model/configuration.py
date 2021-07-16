from openerp.osv import fields, osv

class hr_sinc(osv.osv):
	_name = 'hr.sinc'

	def sinc_attendance(self,cr,uid,ids,context=None):
		emp = self.pool.get('hr.employee')
		obj = self.pool.get('hr.attendance')
		src =obj.search(cr,uid,[('employee_id','=',False)],context=context)
		import pdb;pdb.set_trace()
		for att in obj.browse(cr,uid,src):
			finger = emp.search(cr,uid,[('fingerprint_code','=',att.fingerprint_code)],context=context)
			for emps in emp.browse(cr,uid,finger):
				empss = emps.id
				emp.write(cr,uid,[emps.id],{'employee_id':empss},context=context)
		return True

hr_sinc()