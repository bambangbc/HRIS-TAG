import pytz
import re
import time
import openerp
import openerp.service.report
import uuid
import collections

from werkzeug.exceptions import BadRequest
from datetime import datetime, timedelta
from dateutil import parser
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from openerp import api
from openerp import tools, SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp.http import request
from operator import itemgetter
from openerp import api


class contract(osv.osv):
	_name = "hr.contract"
	_inherit = "hr.contract"

	@api.multi
	def name_get(self):
		res = []
		for asset in self:
			display_name = []
			res.append((asset.id,
						'['+ asset.name + ']' + '[' + asset.employee_id.name + ']' + '[' + asset.employee_id.employee_name + ']'))
		return res

	def onchange_date_from(self, cr, uid,ids, date_start,contract_type):
  
		result = {'value': {}}
		if contract_type == "add":
			date_to = datetime.strptime(date_start,"%Y-%m-%d") + relativedelta(months=12) - relativedelta(days=1)
			result['value']['date_end'] = str(date_to)
		elif contract_type == "training":
			date_to = datetime.strptime(date_start,"%Y-%m-%d") + relativedelta(months=3) - relativedelta(days=1)
			result['value']['date_end'] = str(date_to)
		elif contract_type == "pkwt":
			date_to = datetime.strptime(date_start,"%Y-%m-%d") + relativedelta(months=12) - relativedelta(days=1)
			result['value']['date_end'] = str(date_to)
		elif contract_type == "frelance":
			date_to = datetime.strptime(date_start,"%Y-%m-%d") + relativedelta(months=1) - relativedelta(days=1)
			result['value']['date_end'] = str(date_to)
		return result

	def auto_contract(self,cr,uid,ids=None,context=None):
		date = str(datetime.now())
		dates = date[:10]
		obj = self.pool.get('hr.contract')
		src = obj.search(cr,uid,[])
		for contract in obj.browse(cr,uid,src):
			if contract.date_end >= dates or contract.date_end == False :
				kontrak = True
			else :
				kontrak=False
			obj.write(cr,uid,[contract.id],{'kont_bol':kontrak})
		return True

	def _get_end_contract(self,cr,uid,ids,field,arg,context=None):
		result={}
		date = str(datetime.now())
		dates = date[:10]
		for contract in self.browse(cr,uid,ids,context=None):
			kontrak=False
			if contract.date_end >= dates or contract.date_end == False :
				kontrak = True
			result[contract.id] = kontrak
		return result

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
		years = str(datetime.strptime(vals['date_start'],"%Y-%m-%d").year)
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
		obj_emp.write(cr,uid,[vals['employee_id']],{'stat_kont': True})

		return super(contract,self).create(cr,uid,vals,context=context)

	_columns = {
		'tidakaktif_id' : fields.char('NIK Tidak Aktif'),
		'employee_id': fields.many2one('hr.employee', "NIK", required=True),
		'nama' : fields.char('Name'),
		'name': fields.char('No Kontrak', required=False),
		'kontrak_sebelum' : fields.many2one('hr.contract','No Kontrak Awal', domain="[('employee_id','=',employee_id)]"),
		'hari' :fields.char('hari'),
		'tanggal_rpt' : fields.char('Tanggal'),
		'bulan_rpt' : fields.char('Bulan'),
		'tahun_rpt' : fields.char('Tahun'),
		'tanggal' : fields.date('Tanggal'),
		'datess' : fields.char('Date Format'),
		'kontrak' : fields.function(_get_end_contract,'Status Kontrak'),
		'kont_bol' : fields.boolean('kontrak'),
		'nama_pihak' : fields.many2one('hr.employee', 'Nama Pihak I', domain="[('manager','=',1)]"),
		'bagian' : fields.selection([('guard', 'Guard'), ('operasional', 'Operasional'),('staff_operasional','Staff Operasional'),('staff','Staff')], 'Bagian'),
		'contract_type' : fields.selection([('add', 'Addendum'), ('training', 'Training'), ('frelance', 'frelance'), ('pkwt', 'pkwt')], 'Jenis Kontrak'),
		}

	_defaults = {
		'kont_bol' : True,
	}

class hr_contract_type(osv.osv):
	_name = 'hr.contract.type'
	_inherit = "hr.contract.type"

	_columns = {
		"code" : fields.char('Code'),
		"bank" : fields.boolean("Bank"),
		"nbank": fields.boolean("Non bank"),
	}