from openerp.osv import fields, osv
import datetime
import time
from datetime import date
from time import strptime
from time import strftime
from datetime import datetime
from openerp.tools.translate import _
from openerp import pooler
from openerp import tools
from openerp import SUPERUSER_ID
from openerp import api

class empoyees(osv.osv):
	_inherit = 'hr.employee'

	_columns = {
		'habis_contract' : fields.date('Habis Kontrak'),
		'jamsostek' : fields.boolean("Jamsostek"),
		'insentif' : fields.boolean("Insentif"),
		'jpk' : fields.boolean('JPK'),
		#'tgl_masuk' : fields.date('Tgl Masuk'),
	}

	_sql_constraints = [
        ('ktp_uniq', 'unique(ktp)', 'KTP Tidak Boleh Sama')
    ]

	def _get_end_contract(self,cr,uid,ids,field,arg,context=None):
		result = {}
		date = str(datetime.now())
		dates = date[:10] 
		obj_cont = self.pool.get('hr.contract')
		kontrak = False
		date_con = "2010-01-01"
		for emp in self.browse(cr,uid,ids,context=None):
			src = obj_cont.search(cr,uid,[('employee_id','=',emp.id)])
			for contract in obj_cont.browse(cr,uid,src) :
				if contract.date_end >= dates or contract.date_end == False :
					kontrak = True
				# if contract.date_end >= date_con or contract.date_end == False :
				# 	date_con = contract.date_ends 
			#import pdb;pdb.set_trace()
			result[emp.id] = kontrak
		return result

	def cron_habis_kontrak(self, cr,uid,id=None,context=None):
		obj_emp = self.pool.get('hr.employee')
		obj_cont = self.pool.get('hr.contract')
		src_emp = obj_emp.search(cr,uid,[('active','=',True)])
		for emps in obj_emp.browse(cr,uid,src_emp):
			date_cont = "2010-01-01"
			src_cont = obj_cont.search(cr,uid,[('employee_id','=',emps.id)])
			for cont in obj_cont.browse(cr,uid,src_cont):
				if cont.date_end >= date_cont or cont.date_end == False :
					date_cont = cont.date_end
			if date_cont != "2010-01-01" :
				obj_emp.write(cr,uid,[emps.id],{'habis_contract':date_cont})
			else :
				obj_emp.write(cr,uid,[emps.id],{'habis_contract':False})
		return True


class hr_contrak(osv.osv):
	_inherit = 'hr.contract'

	_columns = {
		'bagian' : fields.selection([('guard', 'Guard'), ('operasional', 'Operasional'),('staff_operasional','Staff Operasional'),('staff','Staff'),('logistik','Logistik'),('sekretariat','Sekretariat'),('marketing','Marketing')], 'Bagian'),
	}

	def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
		if not employee_id:
			return {'value': {'job_id': False}}
		emp_obj = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
		job_id = False
		if emp_obj.job_id:
			job_id = emp_obj.job_id.id
		if emp_obj.employee_name :
			name_id = emp_obj.employee_name
		return {'value': {'job_id': job_id,'nama':name_id}}

	def create(self, cr, uid, vals, context=None):
		obj_sequence = self.pool.get('ir.sequence')
		xxx = obj_sequence.next_by_code(cr, uid, 'hr.contract.sequence', context=context)
		
		obj_emp = self.pool.get('hr.employee')
		dept = obj_emp.browse(cr,uid,vals['employee_id']).department_id.code
		if not dept :
			dept = ""
		obj_type = self.pool.get('hr.contract.type')
		cod = obj_type.browse(cr,uid,vals['type_id']).code
		bnk = obj_type.browse(cr,uid,vals['type_id']).bank
		nbnk = obj_type.browse(cr,uid,vals['type_id']).nbank
		if not cod :
			cod = ""
		aray_bln = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']
		momon = (datetime.strptime(vals['date_start'],"%Y-%m-%d").month)-1
		months =  aray_bln[momon]
		years = str(datetime.now().year)
		if bnk :
			vals['name'] = xxx+"-B"+"/"+cod+"/"+dept+"/"+months+"/"+years
		elif nbnk :
			vals['name'] = xxx+"-NB"+"/"+cod+"/"+dept+"/"+months+"/"+years
		else :	
			vals['name'] = xxx+"/"+cod+"/"+dept+"/"+months+"/"+years

		#menentukan Hari
		# vals['tanggal'] = datetime.now().strftime("%Y-%m-%d")
		# if datetime.now().isoweekday() == 0 :
		# 	vals['hari'] = 'Senin'
		# if datetime.now().isoweekday() == 1 :
		# 	vals['hari'] = 'Selasa'
		# if datetime.now().isoweekday() == 2 :
		# 	vals['hari'] = 'Rabu'
		# if datetime.now().isoweekday() == 3 :
		# 	vals['hari'] = 'Kamis'
		# if datetime.now().isoweekday() == 4 :
		# 	vals['hari'] = 'Jumat'
		# if datetime.now().isoweekday() == 5 :
		# 	vals['hari'] = 'Sabtu'
		# if datetime.now().isoweekday() == 6 :
		# 	vals['hari'] = 'Minggu'

		# merubah status employee menjadi tidak habis kontrak
		obj_emp = self.pool.get('hr.employee')
		if obj_emp.browse(cr,uid,vals['employee_id']).habis_contract <= vals['date_end'] :
			obj_emp.write(cr,uid,[vals['employee_id']],{'stat_kont': True,'habis_contract':vals['date_end']})
		else :
			obj_emp.write(cr,uid,[vals['employee_id']],{'stat_kont': True})
		return super(hr_contrak,self).create(cr,uid,vals,context=context)