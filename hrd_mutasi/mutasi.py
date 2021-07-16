from openerp.osv import fields, osv
import math
import time
import datetime
from openerp.tools.translate import _
from openerp import tools
from datetime import date
from time import strptime
from time import strftime
from datetime import datetime

MUTASI_STATES =[
	('draft','Draft'),
	('verify','Korwil'),
	('approve','Pic'),
	('approve2','Deputi'),
	('approve3','Manager'),
	('approve4','Ass.Vp'),
	('approve5','Hrd Manager'),
	('reject','Reject'),
	('done','Done'),]

class mutasi_karyawan(osv.osv):
	_name = 'hr.mutasi'

	def action_draft(self,cr,uid,ids,context=None): 
		return self.write(cr,uid,ids,{'state':MUTASI_STATES[0][0]},context=context)

	def action_verify(self,cr,uid,ids,context=None):  
		return self.write(cr,uid,ids,{'state':MUTASI_STATES[1][0]},context=context)
	
	def action_approve(self,cr,uid,ids,context=None):
		if self.browse(cr,uid,ids).name.user_id.id == uid :
			  raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve'))
		return self.write(cr,uid,ids,{'state':MUTASI_STATES[2][0]},context=context)

	def action_approve2(self,cr,uid,ids,context=None):
		if self.browse(cr,uid,ids).name.user_id.id == uid :
			  raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve'))  
		return self.write(cr,uid,ids,{'state':MUTASI_STATES[3][0]},context=context)

	def action_approve3(self,cr,uid,ids,context=None):  
		if self.browse(cr,uid,ids).name.user_id.id == uid :
			  raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve'))
		return self.write(cr,uid,ids,{'state':MUTASI_STATES[4][0]},context=context)

	def action_approve4(self,cr,uid,ids,context=None):  
		if self.browse(cr,uid,ids).name.user_id.id == uid :
			  raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve'))
		return self.write(cr,uid,ids,{'state':MUTASI_STATES[5][0]},context=context)

	def action_approve5(self,cr,uid,ids,context=None): 
		if self.browse(cr,uid,ids).name.user_id.id == uid :
			  raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve')) 
		return self.write(cr,uid,ids,{'state':MUTASI_STATES[6][0]},context=context)

	def action_done(self,cr,uid,ids,context=None):
		if self.browse(cr,uid,ids).name.user_id.id == uid :
			  raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve'))
		dates = str(datetime.now().strftime('%Y-%m-%d'))
		obj = self.pool.get('hr.employee')
		brw = self.browse(cr,uid,ids)
		obj_cont = self.pool.get('hr.contract')
		src_cont = obj_cont.search(cr,uid,[('employee_id','=',brw.name.id),('date_start','<=',dates),('date_end','>=',dates)])
		brw_cont = obj_cont.browse(cr,uid,src_cont)
		if not src_cont :
			src_cont = obj_cont.search(cr,uid,[('employee_id','=',brw.name.id),('date_start','<=',dates),('date_end','=',False)])	
		if brw.pilih == 'mutasi' :
			obj.write(cr,uid,[brw.name.id],{'job_id':brw.job_id2.id,'address_id2':brw.lokasi_id2.id})  
			obj_cont.write(cr,uid,src_cont,{'payslip':brw.payslip_id2.id})
		else :
			obj.write(cr,uid,[brw.name.id],{'address_id2':brw.lokasi_id3.id})  
		return self.write(cr,uid,ids,{'state':MUTASI_STATES[8][0]},context=context)

	def action_reject(self,cr,uid,ids,context=None):
		if self.browse(cr,uid,ids).name.user_id.id == uid :
			  raise osv.except_osv(_('Warning!'),_('Anda Tidak Bisa Approve')) 
		return self.write(cr,uid,ids,{'state':MUTASI_STATES[7][0]},context=context) 

	def onchange_nik(self, cr, uid, ids, name) :
		result = {'value': {'job_id': False, 'lokasi_id': False}}
		obj_cont = self.pool.get('hr.contract')
		dates = str(datetime.now().strftime('%Y-%m-%d'))
		if name :
			names = self.pool.get('hr.employee').browse(cr,uid,name)
			##### Mencari Payslip Karyawan Di Kontrak #####
			
			src_cont = obj_cont.search(cr,uid,[('employee_id','=',names.id),('date_start','<=',dates),('date_end','>=',dates)])
			if not src_cont :
				src_cont = obj_cont.search(cr,uid,[('employee_id','=',names.id),('date_start','<=',dates),('date_end','=',False)])	
			if not src_cont :
				raise osv.except_osv(_('Warning!'),_('TIDAK ADA DATA KONTRAK'))
			for brw_cont in obj_cont.browse(cr,uid,src_cont):
				pay = brw_cont.payslip.id
			result['value'] = {'payslip_id':pay,'job_id': names.job_id.id, 'lokasi_id':names.address_id2.id, 'lokasi_id4':names.address_id2.id}
		return result

	def print_mutasi(self, cr, uid, ids, context=None):
	   
		#assert len(ids) == 1, 'This option should only be used for a single id at a time'
		#wf_service = netsvc.LocalService("workflow")
		#wf_service.trg_validate(uid, 'sale.order', ids[0], 'quotation_sent', cr)
		datas = {
				 'model': 'hr.mutasi',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}
		return {'type': 'ir.actions.report.xml', 'report_name': 'hr_mutasi_report', 'datas': datas, 'nodestroy': True}

	def print_penugasan(self, cr, uid, ids, context=None):
	   
		#assert len(ids) == 1, 'This option should only be used for a single id at a time'
		#wf_service = netsvc.LocalService("workflow")
		#wf_service.trg_validate(uid, 'sale.order', ids[0], 'quotation_sent', cr)
		datas = {
				 'model': 'hr.mutasi',
				 'ids': ids,
				 'form': self.read(cr, uid, ids[0], context=context),
		}
		return {'type': 'ir.actions.report.xml', 'report_name': 'hr_penugasan_report', 'datas': datas, 'nodestroy': True}	

	_columns = {
		'no' : fields.char("No"),
		'state': fields.selection(MUTASI_STATES, 'Status', help="Status Approval"),
		'pilih' : fields.selection([('mutasi','Mutasi'),('penugasan','Penugasan')],'Jenis Mutasi'),
		'start_date' : fields.date('Tanggal', required=True),
		'name' : fields.many2one('hr.employee','NIK Karyawan', required=True),
		'employee_name' : fields.related('name','employee_name',type='char',string="Nama Karyawan",readonly=True, store=True),
		'penugasan' :fields.text('Tugas & Tanggung jawab'),
		'tgng_jwb' : fields.text('Tugas & Tanggung jawab'),
		'job_id' : fields.many2one('hr.job','Jabatan Sebelum'),
		'lokasi_id' : fields.many2one('res.partner','Lokasi Kerja Sebelum'),
		'payslip_id' : fields.many2one('hr.gaji','Master Gaji Sebelum'),
		'job_id2' : fields.many2one('hr.job','Jabatan Setelah Mutasi'),
		'lokasi_id2' : fields.many2one('res.partner','Lokasi'),
		'payslip_id2' : fields.many2one('hr.gaji','Master Gaji Setelah Mutasi',required=True),
		'lokasi_id4' : fields.many2one('res.partner','Lokasi Kerja Sebelum'),
		'lokasi_id3' : fields.many2one('res.partner','Lokasi Penugasan'),
	}

	_defaults = {
		'state' : MUTASI_STATES[0][0],
	}