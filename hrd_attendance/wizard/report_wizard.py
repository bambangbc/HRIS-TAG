import time
import pprint
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import api, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval


class report_rekap_absen(osv.TransientModel):
	_name = 'report_rekap_absen'

	_columns = {
		'name' : fields.selection((('laporan_rekap_perorang','Laporan Rekap Absen Perorang'),
									('laporan_rekap_absen','Laporan Rekap Absen Per divisi-lokasi')), "Report", required=True),
		'employee_id':fields.many2one('hr.employee',"Nama Karyawan"),
		'department_id' : fields.many2one('hr.department','Department'),
		'lokasi_id' : fields.many2one('res.partner' , 'Lokasi Kerja' , domain="[('category_id','=','LOKASI')]" ),
		'date_from' : fields.date('Date From',required=True),
		'date_to' : fields.date('Date To', required=True),
	}

	def hasil_rekap_absen_perorangan(self, cr, SUPERUSER_ID, desc, report, view_id, domain, context):
		return {
			'name' : _(desc),
			'view_type': 'form',
			'view_mode': 'tree',
			'res_model': 'laporan.rekap.absen.perorangan',
			'res_id': report,
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			'nodestroy': False,
			'domain' : [('user_id','=',SUPERUSER_ID)],
			'context': context,
			}

	def hasil_rekap_absen_perdivisi(self, cr, SUPERUSER_ID, desc, report, view_id, domain, context):
		return {
			'name' : _(desc),
			'view_type': 'form',
			'view_mode': 'tree',
			'res_model': 'laporan.rekap.absen.perdivisi',
			'res_id': report,
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			'nodestroy': False,
			'domain' : [('user_id','=',SUPERUSER_ID)],
			'context': context,
			}

	def fill_table(self, cr, SUPERUSER_ID, ids, context=None):

		wizard = self.browse(cr,1,ids[0], context=context)
		########################## Laporan Rekap Perorangan ###############################
		dat = []
		#hour_from = 7
		if wizard.name == "laporan_rekap_perorang" :
			#sql = "delete from laporan_rekap_absen_perorangan where user_id = 1"
			#import pdb;pdb.set_trace()
			cr.execute("DELETE FROM laporan_rekap_absen_perorangan sw "\
						"WHERE sw.user_id = %s " , (SUPERUSER_ID,))

			####################################### Mencari Data Cuti Dan Sakit ###################################
			date_from = wizard.date_from
			date_to = wizard.date_to
			nama_karyawan = wizard.employee_id.id

			type_name = 100
			leaves_cuti = 0
			leaves_sakit = 0
			fingerprint_code = '0'
			jumlah_lembur = 0
			lembur2 = 0
			obj_leave_stat = self.pool.get('hr.holidays.status')
			src_leave_stat = obj_leave_stat.search(cr,1,[])
			for objk in obj_leave_stat.browse(cr,1,src_leave_stat):
				if objk.name == "SAKIT" :
					type_name_sakit = objk.id
				if objk.name == "LIBUR NASIONAL" :
					type_name_nasional = objk.id
				if objk.name == "PERJALANAN DINAS" :
					type_name_dinas = objk.id


			###################################################################################################

			############################## Mencari keterlambatan, alpa, pulang cepat ##########################

			day_from = datetime.strptime(date_from,"%Y-%m-%d")
			day_to = datetime.strptime(date_to,"%Y-%m-%d")

			nb_of_days = (day_to - day_from).days + 1

			terlambat = 0
			terlambat1 = 0
			pc = 0
			pc1 = 0
			attendances = 0
			delta = {}
			delta['att'] = 0
			delta['telat'] = 0
			delta['pulang'] = 0
			total_lembur = 0
			real_lembur = 0
			lembur1 = 0
			lembur11 = 0
			tk = 0

			obj_leave = self.pool.get('hr.holidays')

			for day in range(0, nb_of_days) :

				date = (day_from + timedelta(days=day))
				date_lembur1 = str(date-timedelta(hours=7))
				date_lembur2 = str(date+timedelta(hours=17))
				date_cuti_from = str(day_from + timedelta(days=day) + timedelta(hours=17))
				date_cuti_to = str(day_from + timedelta(days=day) - timedelta(hours=7))
				datess = str(date)[:10]
				cuti_hari_ini = False

				day = str(date-timedelta(hours=7))
				day2 = str(date+timedelta(hours=23))
				day3 = str(date+timedelta(hours=41))
				time1=0
				time2=0
				telat=False
				pulang=False
				delta['lembur']=0
				lembur=0
				shift1=False
				cutis = False
				tipe_lembur = "A"
				tks = False
				## mencari data cuti ###
				src_leave = obj_leave.search(cr,1,[('date_from','<=',date_cuti_from),('date_to','>=',date_cuti_to),('employee_id','=',nama_karyawan),('state','=','validate')])
				for ln1 in obj_leave.browse(cr,1,src_leave) :
					#cutis = objk.holiday_status_id.name
					if ln1.holiday_status_id.name == "LIBUR NASIONAL" :
						src_leave = []
				if wizard.employee_id.category_ids :
					src_leave1 = obj_leave.search(cr,1,[('date_from','<=',date_cuti_from),('date_to','>=',date_cuti_to),('holiday_type','=','category'),('state','=','validate')])
					if src_leave1 :
						for tags in wizard.employee_id.category_ids :
							for leave_ in obj_leave.browse(cr,1,src_leave1) :
								if tags.id == leave_.category_id.id :
									src_leave = [leave_.id]
				brw_leave = obj_leave.browse(cr,1,src_leave)
				for objk in brw_leave :
					#import pdb;pdb.set_trace()
					if objk.holiday_status_id.id != type_name_nasional and objk.holiday_status_id.id != type_name_sakit and objk.holiday_status_id.id != type_name_dinas:
						leaves_cuti += 1
					if objk.holiday_status_id.id == type_name_sakit :
						leaves_sakit += 1
					cuti_hari_ini = True
					cutis = objk.holiday_status_id.name
				## mencari data cuti tahunan ##

				# src_leave = obj_leave.search(cr,1,[('date_from','<=',datess),('date_to','>=',datess),('employee_id','=',nama_karyawan),('state','=','validate'),('holiday_status_id','!=',type_name_sakit),('holiday_status_id','!=',type_name_nasional)])
				# brw_leave = obj_leave.browse(cr,1,src_leave)
				# for objk in brw_leave :
				# 	leaves_cuti += 1
				# 	cuti_hari_ini = True
				## mencari data sakit ##

				# src_leave_1 = obj_leave.search(cr,1,[('date_from','<=',datess),('date_to','>=',datess),('employee_id','=',nama_karyawan),('state','=','validate'),('holiday_status_id','=',type_name_sakit)])
				# brw_leave_1 = obj_leave.browse(cr,1,src_leave_1)
				# for objk in brw_leave_1:
				# 	leaves_sakit += 1
				# 	cuti_hari_ini = True

				# cari kontrak karyawan
				brw_contract = self.pool.get('hr.contract')
				src_contract = brw_contract.search(cr,1,['&','&',('employee_id','=',wizard.employee_id.id),('date_start','<=',datess),'|',('date_end','>=',datess),('date_end', '=', False),])
				#import pdb;pdb.set_trace()
				xxx = 0
				if cuti_hari_ini == False :

					for contract in brw_contract.browse(cr,1,src_contract):
						if contract.working_hours :
							shift1 = contract.working_hours
						else :
							obj_shift = self.pool.get('hr.shift_karyawan')
							src_shift = obj_shift.search(cr,1,[('employee_id','=',wizard.employee_id.id),('date_from','<=',datess),('date_to','>=',datess)])
							for shf in obj_shift.browse(cr,1,src_shift) :
								daysss = date.day
								if daysss == 1 :
									shift1 = shf.h1
								elif daysss == 2 :
									shift1 = shf.h2
								elif daysss == 3 :
									shift1 = shf.h3
								elif daysss == 4 :
									shift1 = shf.h4
								elif daysss == 5 :
									shift1 = shf.h5
								elif daysss == 6 :
									shift1 = shf.h6
								elif daysss == 7 :
									shift1 = shf.h7
								elif daysss == 8 :
									shift1 = shf.h8
								elif daysss == 9 :
									shift1 = shf.h9
								elif daysss == 10 :
									shift1 = shf.h10
								if daysss == 11 :
									shift1 = shf.h11
								elif daysss == 12 :
									shift1 = shf.h12
								elif daysss == 13 :
									shift1 = shf.h13
								elif daysss == 14 :
									shift1 = shf.h14
								elif daysss == 15 :
									shift1 = shf.h15
								elif daysss == 16 :
									shift1 = shf.h16
								elif daysss == 17 :
									shift1 = shf.h17
								elif daysss == 18 :
									shift1 = shf.h18
								elif daysss == 19 :
									shift1 = shf.h19
								elif daysss == 20 :
									shift1 = shf.h20
								if daysss == 21 :
									shift1 = shf.h21
								elif daysss == 22 :
									shift1 = shf.h22
								elif daysss == 23 :
									shift1 = shf.h23
								elif daysss == 24 :
									shift1 = shf.h24
								elif daysss == 25 :
									shift1 = shf.h25
								elif daysss == 26 :
									shift1 = shf.h26
								elif daysss == 27 :
									shift1 = shf.h27
								elif daysss == 28 :
									shift1 = shf.h28
								elif daysss == 29 :
									shift1 = shf.h29
								elif daysss == 30 :
									shift1 = shf.h30
								elif daysss == 31 :
									shift1 = shf.h31


						##### jadwal shift non ganti hari #######

						if shift1 :
							if shift1.shift_gt_hr == False :
								non_shift = True
								for shift in shift1.attendance_ids :
									if int(shift.dayofweek)+1 == date.isoweekday() :
										hour_from = shift.hour_from
										hour_to = shift.hour_to
										non_shift = False
										xxx = 1

								if non_shift == False :

									time1=0
									time2=0

									sign_in = "3016-01-01"
									sign_out = "1016-01-01"

									#fingerprint_code = wizard.employee_id.fingerprint_code
									brw_nomesin = self.pool.get('no.mesin')
									src_nomesin = brw_nomesin.search(cr,1,[('employee_id','=',wizard.employee_id.id)])
									tmp_date = '1990-01-01'
									for nmesin in brw_nomesin.browse(cr,1,src_nomesin) :
										date_nmesin = (day)[:10]
										if nmesin.date <= date_nmesin and tmp_date <= nmesin.date:
											tmp_date = nmesin.date
											fingerprint_code = int(nmesin.fingerprint_code)
											no_mesin = nmesin.no_mesin
									# no_mesin = int(wizard.employee_id.no_mesin)
									if src_nomesin == False :
										 raise osv.except_osv(_('Warning!'),_('Fingerprint ID Kosong'))
									obj_att = self.pool.get('hr.attendance')
									atts_ids = obj_att.search(cr, 1, [('no_mesin','=',no_mesin),('fingerprint_code', '=', fingerprint_code), ('name', '>', day), ('name', '<', day2)], order='name asc' )

									for att in obj_att.browse(cr, 1, atts_ids, context=context):
										#mencari log in dan log out
										action = 0
										hour = float((datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")+timedelta(hours=7)).hour)
										minute = ((float(datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S").minute)*100)/60)/100

										if hour + minute >= hour_from - 4 and hour + minute <= hour_from + 3 :
											action = 'sign_in'
										elif str(datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")+timedelta(hours=7)) >= str(date+timedelta(hours=17)) or hour + minute >= hour_to - 3 :
											action = 'sign_out'

										if action == 'sign_in':

											if sign_in > att.name :

												# menghitung keterlambatan
												#import pdb;pdb.set_trace()
												telat1 = (((hour + minute) - hour_from)*60)/100
												telat = (hour + minute) - hour_from
												if telat1 >= 0.059 and telat1 <= 1.19:
													delta['telat'] = 1
												elif telat1 >= 1.2 :
													tks = True
													delta['telat'] = 0
												else :
													delta['telat'] = 0

												time1 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
												sign_in = att.name
										elif action == 'sign_out':

											if sign_out < att.name :

												# menghitung keterlambatan
												pulang = (hour + minute) - hour_to
												if pulang >= 0 or str(datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")+timedelta(hours=7)) >= str(date+timedelta(hours=23)):
													delta['pulang'] = 0
													pulang = 0
												else :
													delta['pulang'] = 1

												time2 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
												sign_out = att.name
									if time2 and time1:
										delta['att'] = 0
									elif time2 or time1 :
										delta['att'] = 0
									else:
										delta['att'] = 1
										delta['pulang'] = 0
										delta['telat'] = 0

								#################################### lembur tidak ganti hari ###########################################
								if datess >= "2017-04-01" and non_shift == False :
									obj_over = self.pool.get('hr.overtime')
									src_over = obj_over.search(cr,1,[('employee_id','=',wizard.employee_id.id),('date_from','>=',str(date+timedelta(hours=hour_from)-timedelta(hours=10))),('date_from','<=',date_lembur2),('state','=','validate')])
									for overt in obj_over.browse(cr,1,src_over) :
										#import pdb;pdb.set_tarce()
										x = 0
										tot = 0
										if overt.overtime_type_id.name == 'Lembur' :
											tipe_lembur = overt.overtime_type.name
											lembur2 = overt.jam_lembur
											if tipe_lembur != "HARI LIBUR NASIONAL" :
												jumlah_ril = overt.jam_lembur - delta['telat'] - delta['pulang']
											else :
												jumlah_ril = overt.jam_lembur - delta['telat']
											if jumlah_ril > 0 :
												for over in overt.overtime_type.jam_ids :
													sampai = float(over.sampai)
													dari = float(over.name)
													#import pdb;pdb.set_trace()
													if sampai == 0.0 :
														sampai = float(10000000)
													if dari != 0.0 and jumlah_ril > 0:
														nx = sampai - dari + 1
														if jumlah_ril >= nx :
															tot = nx * over.pengali
														elif jumlah_ril <= nx :
															tot = jumlah_ril * over.pengali
														jumlah_ril = jumlah_ril - nx
														x = x + tot
												if time2 and time1:
													delta['lembur'] = x
													if tipe_lembur != "HARI LIBUR NASIONAL" :
														jumlah_lembur = overt.jam_lembur - delta['telat'] - delta['pulang']
													else :
														jumlah_lembur = overt.jam_lembur - delta['telat']
												elif tipe_lembur == "HARI LIBUR NASIONAL" :
													jumlah_lembur = overt.jam_lembur - delta['telat']
													delta['lembur'] = x
												else :
													delta['lembur'] = 0
													jumlah_lembur = 0

							##### jadwal shift ganti hari #######

							elif shift1.shift_gt_hr == True :
								hour_form = -10
								for shift in shift1.attendance_ids :
									if int(shift.dayofweek)+1 == date.isoweekday() :
										if shift.name == "1" :
											hour_from = shift.hour_from
										xxx=1
									elif int(shift.dayofweek)+1 == date.isoweekday()+1:
										if shift.name == "2" :
											hour_to = shift.hour_to
										xxx=1
									elif date.isoweekday() == 7 and shift.dayofweek == "0" :
										if shift.name == "2" :
											hour_to = shift.hour_to
										xxx = 1
								time1=0
								time2=0

								sign_in = "1016-01-01"
								sign_out = "3016-01-01"

								brw_nomesin = self.pool.get('no.mesin')
								src_nomesin = brw_nomesin.search(cr,1,[('employee_id','=',wizard.employee_id.id)])
								tmp_date = '1990-01-01'
								for nmesin in brw_nomesin.browse(cr,1,src_nomesin) :
									date_nmesin = (day)[:10]
									if nmesin.date <= date_nmesin and tmp_date <= nmesin.date:
										tmp_date = nmesin.date
										fingerprint_code = int(nmesin.fingerprint_code)
										no_mesin = nmesin.no_mesin

								if src_nomesin == False :
										 raise osv.except_osv(_('Warning!'),_('Fingerprint ID Kosong'))

								obj_att = self.pool.get('hr.attendance')
								atts_ids = obj_att.search(cr, 1, [('fingerprint_code', '=', fingerprint_code), ('no_mesin','=',no_mesin),('name', '>', day), ('name', '<', day3)], order='name asc' )

								for att in obj_att.browse(cr, 1, atts_ids, context=context):
									#mencari log in dan log out
									action = 0
									hour = float((datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")+timedelta(hours=7)).hour)
									minute = ((float(datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S").minute)*100)/60)/100

									dates_name = str(datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S") + timedelta(hours=7))
									#if hour_form <= 0 :
									#	raise osv.except_osv(_('Warning!'),_('ada kesalahan di setting working schedule'))
									# import pdb;pdb.set_trace()
									if hour + minute >= hour_from - 4 and hour + minute <= hour_from + 3 :
										action = 'sign_in'
									elif hour + minute >= hour_to - 3 :
										action = 'sign_out'
									#import pdb;pdb.set_trace()
									if action == 'sign_in' and  str(date)[:10] == dates_name[:10] :
										#pprint.pprint('sign_in')
										#pprint.pprint(att.name)
										if sign_in < att.name :

											# menghitung keterlambatan
											telat = (hour + minute) - hour_from
											telat1 = (((hour + minute) - hour_from)*60)/100
											if telat1 >= 0.059 and telat1 <= 1.19:
												delta['telat'] = 1
											elif telat1 >= 1.19 :
												tks = True
												delta['telat'] = 0
											else :
												delta['telat'] = 0

											time1 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
											sign_in = att.name
									elif action == 'sign_out' and  str(date+timedelta(days=0.85)) <= dates_name:
										#pprint.pprint('sign_out')
										#pprint.pprint(att.name)
										if sign_out > att.name :

											# menghitung keterlambatan

											if datetime.strptime(dates_name,"%Y-%m-%d %H:%M:%S") >= date+timedelta(days=1)+timedelta(hours=hour_to) :
												delta['pulang'] = 0
												pulang = 0
											else :
												delta['pulang'] = 1
												pulang = -float((date+timedelta(days=1)+timedelta(hours=hour_to) - datetime.strptime(dates_name,"%Y-%m-%d %H:%M:%S")).seconds)/3600
											time2 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
											sign_out = att.name

								if time2 and time1:
									delta['att'] = 0
								elif time2 or time1 :
									delta['att'] = 0
								else:
									delta['att'] = 1
									delta['pulang'] = 0
									delta['telat'] = 0

								# ################################## lembur Ganti Hari ###########################################
								if datess >= "2017-04-01" :
									obj_over = self.pool.get('hr.overtime')
									clause_1 = ['&',('date_from','>=',str(date+timedelta(hours=hour_from)-timedelta(hours=10))),('date_from','<=',str(date + timedelta(days=1) + timedelta(hours=5)))]
									clause_final =  [('employee_id','=',wizard.employee_id.id),('state','=','validate')] + clause_1
									src_over = obj_over.search(cr,1,clause_final)
									for overt in obj_over.browse(cr,1,src_over) :
										x = 0
										tot = 0
										if overt.overtime_type_id.name == 'Lembur' :
											tipe_lembur = overt.overtime_type.name
											if tipe_lembur != "HARI LIBUR NASIONAL" :
												jumlah_ril = overt.jam_lembur - delta['telat'] - delta['pulang']
											else :
												jumlah_ril = overt.jam_lembur - delta['telat']
											lembur2 = overt.jam_lembur
											if jumlah_ril > 0 :
												for over in overt.overtime_type.jam_ids :
													sampai = float(over.sampai)
													dari = float(over.name)
													#import pdb;pdb.set_trace()
													if sampai == 0.0 :
														sampai = float(10000000)
													if dari != 0.0 and jumlah_ril > 0:
														nx = sampai - dari + 1
														if jumlah_ril >= nx :
															tot = nx * over.pengali
														elif jumlah_ril <= nx :
															tot = jumlah_ril * over.pengali
														jumlah_ril = jumlah_ril - nx
														x = x + tot
												if time2 and time1:
													delta['lembur'] = x
													if tipe_lembur != "HARI LIBUR NASIONAL" :
														jumlah_lembur = overt.jam_lembur - delta['telat'] - delta['pulang']
													else :
														jumlah_lembur = overt.jam_lembur - delta['telat']
												elif tipe_lembur == "HARI LIBUR NASIONAL" :
													jumlah_lembur = overt.jam_lembur - delta['telat']
													delta['lembur'] = x
												else :
													delta['lembur'] = 0
													jumlah_lembur = 0

						# menghitung lembur
						if datess <= '2017-03-31':
							obj_lembur = self.pool.get('hr.overtime.tag')
							src_lembur = obj_lembur.search(cr,1,[('employee_id','=',wizard.employee_id.id),('date_from','<=',datess),('date_to','>=',datess)])
							lembur1=0
							for lemburs in obj_lembur.browse(cr,1,src_lembur):
								day_lembur = date.day
								if day_lembur == 1 :
									lembur1 = lemburs.h1
								elif day_lembur == 2 :
									lembur1 = lemburs.h2
								elif day_lembur == 3 :
									lembur1 = lemburs.h3
								elif day_lembur == 4 :
									lembur1 = lemburs.h4
								elif day_lembur == 5 :
									lembur1 = lemburs.h5
								elif day_lembur == 6 :
									lembur1 = lemburs.h6
								elif day_lembur == 7 :
									lembur1 = lemburs.h7
								elif day_lembur == 8 :
									lembur1 = lemburs.h8
								elif day_lembur == 9 :
									lembur1 = lemburs.h9
								elif day_lembur == 10 :
									lembur1 = lemburs.h10
								elif day_lembur == 11 :
									lembur1 = lemburs.h11
								elif day_lembur == 12 :
									lembur1 = lemburs.h12
								elif day_lembur == 13 :
									lembur1 = lemburs.h13
								elif day_lembur == 14 :
									lembur1 = lemburs.h14
								elif day_lembur == 15 :
									lembur1 = lemburs.h15
								elif day_lembur == 16 :
									lembur1 = lemburs.h16
								elif day_lembur == 17 :
									lembur1 = lemburs.h17
								elif day_lembur == 18 :
									lembur1 = lemburs.h18
								elif day_lembur == 19 :
									lembur1 = lemburs.h19
								elif day_lembur == 20 :
									lembur1 = lemburs.h20
								elif day_lembur == 21 :
									lembur1 = lemburs.h21
								elif day_lembur == 22 :
									lembur1 = lemburs.h22
								elif day_lembur == 23 :
									lembur1 = lemburs.h23
								elif day_lembur == 24 :
									lembur1 = lemburs.h24
								elif day_lembur == 25 :
									lembur1 = lemburs.h25
								elif day_lembur == 26 :
									lembur1 = lemburs.h26
								elif day_lembur == 27 :
									lembur1 = lemburs.h27
								elif day_lembur == 28 :
									lembur1 = lemburs.h28
								elif day_lembur == 29 :
									lembur1 = lemburs.h29
								elif day_lembur == 30 :
									lembur1 = lemburs.h30
								elif day_lembur == 31 :
									lembur1 = lemburs.h31
							lembur2 = lembur1
							if lembur1 >= 9 :
								lembur1 = lembur1 - 1

							lembur11 = 0
							obj_per_lembur = self.pool.get('perhitungan.lembur')
							src_per_lembur = obj_per_lembur.search(cr,1,[('date_from','<=',datess),('date_to','>=',datess)])
							for per_lembur in obj_per_lembur.browse(cr,1,src_per_lembur):
								day_per_lembur = date.day
								if day_per_lembur == 1 :
									lembur11 = per_lembur.h1
								elif day_per_lembur == 2 :
									lembur11 = per_lembur.h2
								elif day_per_lembur == 3 :
									lembur11 = per_lembur.h3
								elif day_per_lembur == 4 :
									lembur11 = per_lembur.h4
								elif day_per_lembur == 5 :
									lembur11 = per_lembur.h5
								elif day_per_lembur == 6 :
									lembur11 = per_lembur.h6
								elif day_per_lembur == 7 :
									lembur11 = per_lembur.h7
								elif day_per_lembur == 8 :
									lembur11 = per_lembur.h8
								elif day_per_lembur == 9 :
									lembur11 = per_lembur.h9
								elif day_per_lembur == 10 :
									lembur11 = per_lembur.h10
								elif day_per_lembur == 11 :
									lembur11 = per_lembur.h11
								elif day_per_lembur == 12 :
									lembur11 = per_lembur.h12
								elif day_per_lembur == 13 :
									lembur11 = per_lembur.h13
								elif day_per_lembur == 14 :
									lembur11 = per_lembur.h14
								elif day_per_lembur == 15 :
									lembur11 = per_lembur.h15
								elif day_per_lembur == 16 :
									lembur11 = per_lembur.h16
								elif day_per_lembur == 17 :
									lembur11 = per_lembur.h17
								elif day_per_lembur == 18 :
									lembur11 = per_lembur.h18
								elif day_per_lembur == 19 :
									lembur11 = per_lembur.h19
								elif day_per_lembur == 20 :
									lembur11 = per_lembur.h20
								elif day_per_lembur == 21 :
									lembur11 = per_lembur.h21
								elif day_per_lembur == 22 :
									lembur11 = per_lembur.h22
								elif day_per_lembur == 23 :
									lembur11 = per_lembur.h23
								elif day_per_lembur == 24 :
									lembur11 = per_lembur.h24
								elif day_per_lembur == 25 :
									lembur11 = per_lembur.h25
								elif day_per_lembur == 26 :
									lembur11 = per_lembur.h26
								elif day_per_lembur == 27 :
									lembur11 = per_lembur.h27
								elif day_per_lembur == 28 :
									lembur11 = per_lembur.h28
								elif day_per_lembur == 29 :
									lembur11 = per_lembur.h29
								elif day_per_lembur == 30 :
									lembur11 = per_lembur.h30
								elif day_per_lembur == 31 :
									lembur11 = per_lembur.h31

							x = 0
							tot = 0
							if lembur11 == 0 :
								raise osv.except_osv(_('Warning!'),_('Perhitungan Point lembur belum Di isi'))
							if tipe_lembur != "HARI LIBUR NASIONAL" :
								jumlah_ril = lembur1 - delta['telat'] - delta['pulang']
							else :
								jumlah_ril = lembur1 - delta['telat']
							if jumlah_ril > 0 :
								for penghitung in lembur11.jam_ids :
									sampai = float(penghitung.sampai)
									dari = float(penghitung.name)
									if sampai == 0.0 :
										sampai = float(10000000)
									if dari != 0.0 and jumlah_ril > 0:
										nx = sampai - dari + 1
										if jumlah_ril >= nx :
											tot = nx * penghitung.pengali
										elif jumlah_ril <= nx :
											tot = jumlah_ril * penghitung.pengali
										jumlah_ril = jumlah_ril - nx
										x = x + tot
								if time2 and time1:
									delta['lembur'] = x
									if tipe_lembur != "HARI LIBUR NASIONAL" :
										jumlah_lembur = lembur1 - delta['telat'] - delta['pulang']
									else :
										jumlah_lembur = lembur1 - delta['telat']
								elif tipe_lembur == "HARI LIBUR NASIONAL" :
									jumlah_lembur = lembur1 - delta['telat']
									delta['lembur'] = x
								else :
									delta['lembur'] = 0
									jumlah_lembur = 0

				if tipe_lembur != "HARI LIBUR NASIONAL":
					pc1 += delta['pulang']
				if tipe_lembur != "HARI LIBUR NASIONAL":
					attendances  += delta['att']

				terlambat1 += delta['telat']

				#cuti_hari_ini = False
				delta['att'] = 0
				delta['telat'] = 0
				delta['pulang'] = 0

				# keterlambatan
				if telat > 0 :
					terlambat = telat
				else :
					terlambat = False

				# pulang cepat
				if pulang <= 0 and tipe_lembur != "HARI LIBUR NASIONAL":
					pc = pulang
				else :
					pc = False

				# shift
				if xxx == 1 :
					shift11 = shift1.name
				else :
					shift11 = False

				# lembur
				if jumlah_lembur >= 0 :
					jumlah_lembur = jumlah_lembur
				else :
					jumlah_lembur = 0

				if cutis == False :
					if time1 == False and time2 == False and shift11 :
						cutis = "Alfa"
					elif time2 == False and time1 == False :
						cutis = False
					elif time1 == False or time2 == False or tks == True :
						if tipe_lembur != "HARI LIBUR NASIONAL" :
							cutis = "TK"
							tk += 1

				total_lembur += delta['lembur']
				real_lembur += jumlah_lembur
				dat.append((0,0,{'date':datess,
								 'shift_id':shift11,
								 'jam_masuk':time1,
								 'jam_pulang':time2,
								 'pc':pc,
								 'terlambat':terlambat,
								 'spl': lembur2,
								 'lembur':jumlah_lembur,
								 'PL':delta['lembur'],
								 'ket':cutis}))

				jumlah_ril = 0
				lembur2 = 0
				jumlah_lembur = 0
				pulang = 0
			alpa = attendances
			rekap_absen_perorangan = self.pool.get('laporan.rekap.absen.perorangan').create(cr,1,{'name':wizard.employee_id.id,
																'department_id' : wizard.employee_id.department_id.name,
																'lokasi_id' : wizard.employee_id.address_id2.name,
																'job_id' : wizard.employee_id.job_id.id,
																'date_from':wizard.date_from,
																'date_to':wizard.date_to,
																'terlambat':terlambat1,
																'pc' : pc1,
																'lembur' : total_lembur,
																'real_lembur' : real_lembur,
																'alpa' : alpa,
																'tk' : tk,
																'user_id':SUPERUSER_ID,
																'cuti':leaves_cuti,
																'detail_ids' : dat,
																'sakit':leaves_sakit})
			view_ref = self.pool.get('ir.model.data').get_object_reference(cr, SUPERUSER_ID, 'hrd_attendance', 'laporan_rekap_absen_perorangan_tree')
			view_id = view_ref and view_ref[1] or False,

			desc 	= 'Laporan Rekap Absen Perorangan'
			domain 	= []
			context = {}

			return self.hasil_rekap_absen_perorangan(cr, SUPERUSER_ID, desc, rekap_absen_perorangan, view_id, domain, context)
			################################################################################################

		elif wizard.name == "laporan_rekap_absen" :
			#sql = "delete from laporan_rekap_absen_perdivisi"

			cr.execute("DELETE FROM laporan_rekap_absen_perdivisi sm "\
						"WHERE sm.user_id = %s " , (SUPERUSER_ID,))

			####################################### Mencari Data Cuti Dan Sakit ###################################
			date_from = wizard.date_from
			date_to = wizard.date_to
			#nama_karyawan = wizard.employee_id.id

			type_name = 100
			leaves_cuti = 0
			leaves_sakit = 0
			jumlah_lembur = 0
			lembur2 = 0

			type_name_sakit = 0
			type_name_nasional = 0
			obj_leave_stat = self.pool.get('hr.holidays.status')
			src_leave_stat = obj_leave_stat.search(cr,1,[])
			for objk in obj_leave_stat.browse(cr,1,src_leave_stat):
				if objk.name == "SAKIT" :
					type_name_sakit = objk.id
				if objk.name == "LIBUR NASIONAL" :
					type_name_nasional = objk.id
				if objk.name == "PERJALANAN DINAS" :
					type_name_dinas = objk.id


			###################################################################################################

			############################## Mencari keterlambatan, alpa, pulang cepat ##########################
			day_from = datetime.strptime(date_from,"%Y-%m-%d")
			day_to = datetime.strptime(date_to,"%Y-%m-%d")

			nb_of_days = (day_to - day_from).days + 1

			obj_leave = self.pool.get('hr.holidays')

			obj_emps = self.pool.get('hr.employee')
			src_emps = obj_emps.search(cr,1,[('address_id2','=',wizard.lokasi_id.id),('department_id','=',wizard.department_id.id)])
			for brw_emps in obj_emps.browse(cr,1,src_emps) :

				employee_ids = brw_emps.id

				dat = []
				terlambat = 0
				pc = 0
				attendances = 0
				delta = {}
				delta['att'] = 0
				delta['telat'] = 0
				delta['pulang'] = 0
				fingerprint_code = '0'
				rekap_absen_perdivisi = []
				total_lembur = 0
				real_lembur = 0
				leaves_cuti = 0
				leaves_sakit = 0
				tk = 0
				for day in range(0, nb_of_days) :

					date = (day_from + timedelta(days=day))
					date_cuti_from = str(day_from + timedelta(days=day) + timedelta(hours=17))
					date_cuti_to = str(day_from + timedelta(days=day) - timedelta(hours=7))
					datess = str(date)[:10]
					cuti_hari_ini = False

					day = str(date-timedelta(hours=7))
					day2 = str(date+timedelta(hours=23))
					day3 = str(date+timedelta(hours=41))
					shift1 = False
					time1=0
					time2=0
					telat=False
					pulang=False
					delta['lembur']=0
					lembur=0
					date_lembur1 = str(date-timedelta(hours=7))
					date_lembur2 = str(date+timedelta(hours=17))
					no_mesin = 0
					cutis = False
					tipe_lembur = "A"
					tks = False
					## mencari data cuti ###
					src_leave = obj_leave.search(cr,1,[('date_from','<=',date_cuti_from),('date_to','>=',date_cuti_to),('employee_id','=',employee_ids),('state','=','validate')])
					for ln1 in obj_leave.browse(cr,1,src_leave) :
						#cutis = objk.holiday_status_id.name
						if ln1.holiday_status_id.name == "LIBUR NASIONAL" :
							src_leave = []
					if brw_emps.category_ids :
						src_leave1 = obj_leave.search(cr,1,[('date_from','<=',date_cuti_from),('date_to','>=',date_cuti_to),('holiday_type','=','category'),('state','=','validate')])
						if src_leave1 :
							for tags in brw_emps.category_ids :
								for leave_ in obj_leave.browse(cr,1,src_leave1) :
									if tags.id == leave_.category_id.id :
										src_leave = [leave_.id]
					brw_leave = obj_leave.browse(cr,1,src_leave)
					for objk in brw_leave :
						if objk.holiday_status_id.id != type_name_nasional and objk.holiday_status_id.id != type_name_sakit and objk.holiday_status_id.id != type_name_dinas:
							leaves_cuti += 1
						if objk.holiday_status_id.id == type_name_sakit :
							leaves_sakit += 1
						cuti_hari_ini = True
						cutis = objk.holiday_status_id.name
					## mencari data cuti tahunan ##

					# src_leave = obj_leave.search(cr,1,[('date_from','<=',datess),('date_to','>=',datess),('employee_id','=',employee_ids),('state','=','validate'),('holiday_status_id','!=',type_name_sakit),('holiday_status_id','!=',type_name_nasional)])
					# brw_leave = obj_leave.browse(cr,1,src_leave)
					# for objk in brw_leave :
					# 	leaves_cuti += 1
					# 	cuti_hari_ini = True
					## mencari data sakit ##

					# src_leave_1 = obj_leave.search(cr,1,[('date_from','<=',datess),('date_to','>=',datess),('employee_id','=',employee_ids),('state','=','validate'),('holiday_status_id','=',type_name_sakit)])
					# brw_leave_1 = obj_leave.browse(cr,1,src_leave_1)
					# for objk in brw_leave_1:
					# 	leaves_sakit += 1
					# 	cuti_hari_ini = True

					# cari kontrak karyawan
					brw_contract = self.pool.get('hr.contract')
					src_contract = brw_contract.search(cr,1,['&','&',('employee_id','=',employee_ids),('date_start','<=',datess),'|',('date_end','>=',datess),('date_end', '=', False),])
					#src_contract = brw_contract.search(cr,1,[('employee_id','=',employee_ids),('date_start','<=',datess),('date_end','>=',datess)])
					# import pdb;pdb.set_trace()
					xxx = 0
					if cuti_hari_ini == False :
						# import pdb;pdb.set_trace()
						for contract in brw_contract.browse(cr,1,src_contract):
							if contract.working_hours :
								shift1 = contract.working_hours
							else :
								obj_shift = self.pool.get('hr.shift_karyawan')
								src_shift = obj_shift.search(cr,1,[('employee_id','=',employee_ids),('date_from','<=',datess),('date_to','>=',datess)])

								for shf in obj_shift.browse(cr,1,src_shift) :
									daysss = date.day
									if daysss == 1 :
										shift1 = shf.h1
									elif daysss == 2 :
										shift1 = shf.h2
									elif daysss == 3 :
										shift1 = shf.h3
									elif daysss == 4 :
										shift1 = shf.h4
									elif daysss == 5 :
										shift1 = shf.h5
									elif daysss == 6 :
										shift1 = shf.h6
									elif daysss == 7 :
										shift1 = shf.h7
									elif daysss == 8 :
										shift1 = shf.h8
									elif daysss == 9 :
										shift1 = shf.h9
									elif daysss == 10 :
										shift1 = shf.h10
									if daysss == 11 :
										shift1 = shf.h11
									elif daysss == 12 :
										shift1 = shf.h12
									elif daysss == 13 :
										shift1 = shf.h13
									elif daysss == 14 :
										shift1 = shf.h14
									elif daysss == 15 :
										shift1 = shf.h15
									elif daysss == 16 :
										shift1 = shf.h16
									elif daysss == 17 :
										shift1 = shf.h17
									elif daysss == 18 :
										shift1 = shf.h18
									elif daysss == 19 :
										shift1 = shf.h19
									elif daysss == 20 :
										shift1 = shf.h20
									if daysss == 21 :
										shift1 = shf.h21
									elif daysss == 22 :
										shift1 = shf.h22
									elif daysss == 23 :
										shift1 = shf.h23
									elif daysss == 24 :
										shift1 = shf.h24
									elif daysss == 25 :
										shift1 = shf.h25
									elif daysss == 26 :
										shift1 = shf.h26
									elif daysss == 27 :
										shift1 = shf.h27
									elif daysss == 28 :
										shift1 = shf.h28
									elif daysss == 29 :
										shift1 = shf.h29
									elif daysss == 30 :
										shift1 = shf.h30
									elif daysss == 31 :
										shift1 = shf.h31


							##### jadwal shift non ganti hari #######
							#import pdb;pdb.set_trace()
							if shift1 :
								if shift1.shift_gt_hr == False :
									non_shift = True
									for shift in shift1.attendance_ids :
										if int(shift.dayofweek)+1 == date.isoweekday() :
											hour_from = shift.hour_from
											hour_to = shift.hour_to
											non_shift = False
											xxx = 1

									if non_shift == False :

										time1=0
										time2=0

										sign_in = "3016-01-01"
										sign_out = "1016-01-01"

										#fingerprint_code = brw_emps.fingerprint_code
										brw_nomesin = self.pool.get('no.mesin')
										src_nomesin = brw_nomesin.search(cr,1,[('employee_id','=',brw_emps.id)])
										tmp_date = '1990-01-01'
										for nmesin in brw_nomesin.browse(cr,1,src_nomesin) :
											date_nmesin = (day)[:10]
											if nmesin.date <= date_nmesin and tmp_date <= nmesin.date:
												tmp_date = nmesin.date
												fingerprint_code = int(nmesin.fingerprint_code)
												no_mesin = nmesin.no_mesin

										if src_nomesin == False :
											raise osv.except_osv(_('Warning!'),_('Fingerprint ID Kosong'))

										obj_att = self.pool.get('hr.attendance')
										atts_ids = obj_att.search(cr, 1, [('no_mesin','=',no_mesin),('fingerprint_code', '=', fingerprint_code), ('name', '>', day), ('name', '<', day2)], order='name asc' )

										for att in obj_att.browse(cr, 1, atts_ids, context=context):
											#mencari log in dan log out
											action = 0
											hour = float((datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")+timedelta(hours=7)).hour)
											minute = ((float(datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S").minute)*100)/60)/100

											if hour + minute >= hour_from - 4 and hour + minute <= hour_from + 3 :
												action = 'sign_in'
											elif str(datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")+timedelta(hours=7)) >= str(date+timedelta(hours=22)) or hour + minute >= hour_to - 3 :
												action = 'sign_out'

											if action == 'sign_in':

												if sign_in > att.name :

													# menghitung keterlambatan
													telat = (hour + minute) - hour_from
													telat1 = (((hour + minute) - hour_from)*60)/100
													if telat1 >= 0.059 and telat1 <= 1.19:
														delta['telat'] = 1
													elif telat1 >= 1.19 :
														tks = True
														delta['telat'] = 0
													else :
														delta['telat'] = 0

													time1 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
													sign_in = att.name
											elif action == 'sign_out':

												if sign_out < att.name :

													# menghitung keterlambatan
													pulang = (hour + minute) - hour_to
													if pulang >= 0 or str(datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")+timedelta(hours=7)) >= str(date+timedelta(hours=23)):
														delta['pulang'] = 0
														pulang = 0
													else :
														delta['pulang'] = 1

													time2 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
													sign_out = att.name

										if time2 and time1:
											delta['att'] = 0
										elif time2 or time1:
											delta['att'] = 0
										else:
											delta['att'] = 1
											delta['pulang'] = 0
											delta['telat'] = 0

									################################## lembur Tidak Ganti ###########################################
									if datess >= "2017-04-01"  and non_shift == False:
										obj_over = self.pool.get('hr.overtime')
										src_over = obj_over.search(cr,1,[('employee_id','=',employee_ids),('date_from','>=',str(date+timedelta(hours=hour_from)-timedelta(hours=10))),('date_from','<=',date_lembur2),('state','=','validate')])
										for overt in obj_over.browse(cr,1,src_over) :
											x = 0
											tot = 0
											if overt.overtime_type_id.name == 'Lembur' :
												tipe_lembur = overt.overtime_type.name
												if tipe_lembur != "HARI LIBUR NASIONAL" :
													jumlah_ril = overt.jam_lembur - delta['telat'] - delta['pulang']
												else :
													jumlah_ril = overt.jam_lembur - delta['telat']
												lembur2 = overt.jam_lembur
												if jumlah_ril > 0 :
													for over in overt.overtime_type.jam_ids :
														sampai = float(over.sampai)
														dari = float(over.name)
														#import pdb;pdb.set_trace()
														if sampai == 0.0 :
															sampai = float(10000000)
														if dari != 0.0 and jumlah_ril > 0:
															nx = sampai - dari + 1
															if jumlah_ril >= nx :
																tot = nx * over.pengali
															elif jumlah_ril <= nx :
																tot = jumlah_ril * over.pengali
															jumlah_ril = jumlah_ril - nx
															x = x + tot
													if time2 and time1:
														delta['lembur'] = x
														if tipe_lembur != "HARI LIBUR NASIONAL":
															jumlah_lembur = overt.jam_lembur - delta['telat'] - delta['pulang']
														else :
															jumlah_lembur = overt.jam_lembur - delta['telat']
													elif tipe_lembur == "HARI LIBUR NASIONAL":
														jumlah_lembur = overt.jam_lembur - delta['telat']
														delta['lembur'] = x
													else :
														delta['lembur'] = 0
														jumlah_lembur = 0

								##### jadwal shift ganti hari #######
								elif shift1.shift_gt_hr == True :
									for shift in shift1.attendance_ids :
										if int(shift.dayofweek)+1 == date.isoweekday() :
											if shift.name == "1" :
												hour_from = shift.hour_from
											xxx = 1
										elif int(shift.dayofweek)+1 == date.isoweekday()+1:
											if shift.name == "2" :
												hour_to = shift.hour_to
											xxx = 1
										elif date.isoweekday() == 7 and shift.dayofweek == "0" :
											if shift.name == "2" :
												hour_to = shift.hour_to
											xxx = 1
									time1=0
									time2=0

									sign_in = "1016-01-01"
									sign_out = "3016-01-01"

									#fingerprint_code =brw_emps.fingerprint_code
									brw_nomesin = self.pool.get('no.mesin')
									src_nomesin = brw_nomesin.search(cr,1,[('employee_id','=',brw_emps.id)])
									tmp_date = '1990-01-01'
									for nmesin in brw_nomesin.browse(cr,1,src_nomesin) :
										date_nmesin = str(datetime.strptime(day,"%Y-%m-%d %H:%M:%S")+timedelta(hours=7))[:10]
										if nmesin.date <= date_nmesin and tmp_date <= nmesin.date:
											tmp_date = nmesin.date
											fingerprint_code = int(nmesin.fingerprint_code)
											no_mesin = nmesin.no_mesin

									if src_nomesin == False :
										 raise osv.except_osv(_('Warning!'),_('Fingerprint ID Kosong'))

									obj_att = self.pool.get('hr.attendance')
									atts_ids = obj_att.search(cr, 1, [('no_mesin','=',no_mesin),('fingerprint_code', '=', fingerprint_code), ('name', '>', day), ('name', '<', day3)], order='name asc' )

									for att in obj_att.browse(cr, 1, atts_ids, context=context):
										#mencari log in dan log out
										action = 0
										hour = float((datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")+timedelta(hours=7)).hour)
										minute = ((float(datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S").minute)*100)/60)/100

										dates_name = str(datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S") + timedelta(hours=7))

										if hour + minute >= hour_from - 4 and hour + minute <= hour_from + 3 :
											action = 'sign_in'
										elif hour + minute >= hour_to - 3 :
											action = 'sign_out'
										#import pdb;pdb.set_trace()
										if action == 'sign_in' and  str(date)[:10] == dates_name[:10] :
											#pprint.pprint('sign_in')
											#pprint.pprint(att.name)
											if sign_in < att.name :

												# menghitung keterlambatan
												telat = (hour + minute) - hour_from
												telat1 = (((hour + minute) - hour_from)*60)/100
												if telat1 >= 0.059 and telat1 <= 1.19:
													delta['telat'] = 1
												elif telat1 >= 1.2 :
													tks = True
													delta['telat'] = 0
												else :
													delta['telat'] = 0

												time1 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
												sign_in = att.name
										elif action == 'sign_out' and  str(date+timedelta(days=0.85)) <= dates_name:
											#pprint.pprint('sign_out')
											#pprint.pprint(att.name)
											if sign_out > att.name :

												# menghitung keterlambatan
												if datetime.strptime(dates_name,"%Y-%m-%d %H:%M:%S") >= date+timedelta(days=1)+timedelta(hours=hour_to) :
													delta['pulang'] = 0
													pulang = 0
												else :
													delta['pulang'] = 1
													pulang = -float((date+timedelta(days=1)+timedelta(hours=hour_to) - datetime.strptime(dates_name,"%Y-%m-%d %H:%M:%S")).seconds)/3600

												time2 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
												sign_out = att.name

									if time2 and time1:
										delta['att'] = 0
									elif time2 or time1 :
										delta['att'] = 0
									else:
										delta['att'] = 1
										delta['pulang'] = 0
										delta['telat'] = 0

									# ################################## lembur Ganti Hari ###########################################
									if datess >= "2017-04-01" :
										obj_over = self.pool.get('hr.overtime')
										clause_1 = ['&',('date_from','>=',str(date+timedelta(hours=hour_from)-timedelta(hours=10))),('date_from','<=',str(date + timedelta(days=1) + timedelta(hours=5)))]
										clause_final =  [('employee_id','=',employee_ids),('state','=','validate')] + clause_1
										src_over = obj_over.search(cr,1,clause_final)
										#src_over = obj_over.search(cr,1,[('employee_id','=',wizard.employee_id.id),('date_from','>=',str(date + timedelta(days=1))),('date_from','<=',str(date + timedelta(days=1) + timedelta(hours=24))),('state','=','validate')])
										for overt in obj_over.browse(cr,1,src_over) :
											x = 0
											tot = 0
											if overt.overtime_type_id.name == 'Lembur' :
												tipe_lembur = overt.overtime_type.name
												if tipe_lembur != "HARI LIBUR NASIONAL" :
													jumlah_ril = overt.jam_lembur - delta['telat'] - delta['pulang']
												else :
													jumlah_ril = overt.jam_lembur - delta['telat']
												lembur2 = overt.jam_lembur
												if jumlah_ril > 0 :
													for over in overt.overtime_type.jam_ids :
														sampai = float(over.sampai)
														dari = float(over.name)
														#import pdb;pdb.set_trace()
														if sampai == 0.0 :
															sampai = float(10000000)
														if dari != 0.0 and jumlah_ril > 0:
															nx = sampai - dari + 1
															if jumlah_ril >= nx :
																tot = nx * over.pengali
															elif jumlah_ril <= nx :
																tot = jumlah_ril * over.pengali
															jumlah_ril = jumlah_ril - nx
															x = x + tot
													if time2 and time1:
														delta['lembur'] = x
														if tipe_lembur != "HARI LIBUR NASIONAL":
															jumlah_lembur = overt.jam_lembur - delta['telat'] - delta['pulang']
														else :
															jumlah_lembur = overt.jam_lembur - delta['telat']
													elif tipe_lembur == "HARI LIBUR NASIONAL":
														jumlah_lembur = overt.jam_lembur - delta['telat']
														delta['lembur'] = x
													else :
														delta['lembur'] = 0
														jumlah_lembur = 0

						# menghitung lembur
						lembur1 = 0
						if datess <= "2017-03-31":
							obj_lembur = self.pool.get('hr.overtime.tag')
							src_lembur = obj_lembur.search(cr,1,[('employee_id','=',brw_emps.id),('date_from','<=',datess),('date_to','>=',datess)])
							for lemburs in obj_lembur.browse(cr,1,src_lembur):
								day_lembur = date.day
								if day_lembur == 1 :
									lembur1 = lemburs.h1
								elif day_lembur == 2 :
									lembur1 = lemburs.h2
								elif day_lembur == 3 :
									lembur1 = lemburs.h3
								elif day_lembur == 4 :
									lembur1 = lemburs.h4
								elif day_lembur == 5 :
									lembur1 = lemburs.h5
								elif day_lembur == 6 :
									lembur1 = lemburs.h6
								elif day_lembur == 7 :
									lembur1 = lemburs.h7
								elif day_lembur == 8 :
									lembur1 = lemburs.h8
								elif day_lembur == 9 :
									lembur1 = lemburs.h9
								elif day_lembur == 10 :
									lembur1 = lemburs.h10
								elif day_lembur == 11 :
									lembur1 = lemburs.h11
								elif day_lembur == 12 :
									lembur1 = lemburs.h12
								elif day_lembur == 13 :
									lembur1 = lemburs.h13
								elif day_lembur == 14 :
									lembur1 = lemburs.h14
								elif day_lembur == 15 :
									lembur1 = lemburs.h15
								elif day_lembur == 16 :
									lembur1 = lemburs.h16
								elif day_lembur == 17 :
									lembur1 = lemburs.h17
								elif day_lembur == 18 :
									lembur1 = lemburs.h18
								elif day_lembur == 19 :
									lembur1 = lemburs.h19
								elif day_lembur == 20 :
									lembur1 = lemburs.h20
								elif day_lembur == 21 :
									lembur1 = lemburs.h21
								elif day_lembur == 22 :
									lembur1 = lemburs.h22
								elif day_lembur == 23 :
									lembur1 = lemburs.h23
								elif day_lembur == 24 :
									lembur1 = lemburs.h24
								elif day_lembur == 25 :
									lembur1 = lemburs.h25
								elif day_lembur == 26 :
									lembur1 = lemburs.h26
								elif day_lembur == 27 :
									lembur1 = lemburs.h27
								elif day_lembur == 28 :
									lembur1 = lemburs.h28
								elif day_lembur == 29 :
									lembur1 = lemburs.h29
								elif day_lembur == 30 :
									lembur1 = lemburs.h30
								elif day_lembur == 31 :
									lembur1 = lemburs.h31
							lembur2 = lembur1
							if lembur1 >= 9 :
								lembur1 = lembur1 - 1

							lembur11 = 0
							obj_per_lembur = self.pool.get('perhitungan.lembur')
							src_per_lembur = obj_per_lembur.search(cr,1,[('date_from','<=',datess),('date_to','>=',datess)])
							for per_lembur in obj_per_lembur.browse(cr,1,src_per_lembur):
								day_per_lembur = date.day
								if day_per_lembur == 1 :
									lembur11 = per_lembur.h1
								elif day_per_lembur == 2 :
									lembur11 = per_lembur.h2
								elif day_per_lembur == 3 :
									lembur11 = per_lembur.h3
								elif day_per_lembur == 4 :
									lembur11 = per_lembur.h4
								elif day_per_lembur == 5 :
									lembur11 = per_lembur.h5
								elif day_per_lembur == 6 :
									lembur11 = per_lembur.h6
								elif day_per_lembur == 7 :
									lembur11 = per_lembur.h7
								elif day_per_lembur == 8 :
									lembur11 = per_lembur.h8
								elif day_per_lembur == 9 :
									lembur11 = per_lembur.h9
								elif day_per_lembur == 10 :
									lembur11 = per_lembur.h10
								elif day_per_lembur == 11 :
									lembur11 = per_lembur.h11
								elif day_per_lembur == 12 :
									lembur11 = per_lembur.h12
								elif day_per_lembur == 13 :
									lembur11 = per_lembur.h13
								elif day_per_lembur == 14 :
									lembur11 = per_lembur.h14
								elif day_per_lembur == 15 :
									lembur11 = per_lembur.h15
								elif day_per_lembur == 16 :
									lembur11 = per_lembur.h16
								elif day_per_lembur == 17 :
									lembur11 = per_lembur.h17
								elif day_per_lembur == 18 :
									lembur11 = per_lembur.h18
								elif day_per_lembur == 19 :
									lembur11 = per_lembur.h19
								elif day_per_lembur == 20 :
									lembur11 = per_lembur.h20
								elif day_per_lembur == 21 :
									lembur11 = per_lembur.h21
								elif day_per_lembur == 22 :
									lembur11 = per_lembur.h22
								elif day_per_lembur == 23 :
									lembur11 = per_lembur.h23
								elif day_per_lembur == 24 :
									lembur11 = per_lembur.h24
								elif day_per_lembur == 25 :
									lembur11 = per_lembur.h25
								elif day_per_lembur == 26 :
									lembur11 = per_lembur.h26
								elif day_per_lembur == 27 :
									lembur11 = per_lembur.h27
								elif day_per_lembur == 28 :
									lembur11 = per_lembur.h28
								elif day_per_lembur == 29 :
									lembur11 = per_lembur.h29
								elif day_per_lembur == 30 :
									lembur11 = per_lembur.h30
								elif day_per_lembur == 31 :
									lembur11 = per_lembur.h31

							x = 0
							tot = 0
							if lembur11 == 0 :
								raise osv.except_osv(_('Warning!'),_('Perhitungan Point lembur belum Di isi'))
							if tipe_lembur != "HARI LIBUR NASIONAL" :
								jumlah_ril = overt.jam_lembur - delta['telat'] - delta['pulang']
							else :
								jumlah_ril = overt.jam_lembur - delta['telat']
							if jumlah_ril > 0 :
								for penghitung in lembur11.jam_ids :
									sampai = float(penghitung.sampai)
									dari = float(penghitung.name)
									if sampai == 0.0 :
										sampai = float(10000000)
									if dari != 0.0 and jumlah_ril > 0:
										nx = sampai - dari + 1
										if jumlah_ril >= nx :
											tot = nx * penghitung.pengali
										elif jumlah_ril <= nx :
											tot = jumlah_ril * penghitung.pengali
										jumlah_ril = jumlah_ril - nx
										x = x + tot
								if time2 and time1:
									delta['lembur'] = x
									if tipe_lembur != "HARI LIBUR NASIONAL":
										jumlah_lembur = overt.jam_lembur - delta['telat'] - delta['pulang']
									else :
										jumlah_lembur = overt.jam_lembur - delta['telat']
								elif tipe_lembur == "HARI LIBUR NASIONAL":
									delta['lembur'] = x
									jumlah_lembur = overt.jam_lembur - delta['telat']
								else :
									delta['lembur'] = 0
									jumlah_lembur = 0


					terlambat += delta['telat']
					if tipe_lembur != "HARI LIBUR NASIONAL" :
						pc += delta['pulang']
					if tipe_lembur != "HARI LIBUR NASIONAL" :
						attendances  += delta['att']

					#cuti_hari_ini = False
					delta['att'] = 0
					delta['telat'] = 0
					delta['pulang'] = 0

					# keterlambatan
					if telat > 0 :
						terlambat1 = telat
					else :
						terlambat1 = False

					# pulang cepat
					if pulang <= 0 and tipe_lembur != "HARI LIBUR NASIONAL" :
						pc1 = pulang
					else :
						pc1 = False

					# shift
					if xxx == 1 :
						shift11 = shift1.name
					else :
						shift11 = False

					if jumlah_lembur >= 0 :
						jumlah_lembur = jumlah_lembur
					else :
						jumlah_lembur = 0

					if cutis == False :
						if time1 == False and time2 == False and shift11 :
							cutis = "Alfa"
						elif time2 == False and time1 == False :
							cutis = False
						elif time1 == False or time2 == False or tks == True:
							if tipe_lembur != "HARI LIBUR NASIONAL" :
								cutis = "TK"
								tk += 1


					total_lembur += delta['lembur']
					real_lembur += jumlah_lembur
					dat.append((0,0,{'date':datess,
									 'shift_id':shift11,
									 'jam_masuk':time1,
									 'jam_pulang':time2,
									 'pc':pc1,
									 'spl':lembur2,
									 'terlambat':terlambat1,
									 'lembur':jumlah_lembur,
									 'PL':delta['lembur'],
									 'ket' : cutis}))
					jumlah_ril = 0
					lembur2 = 0
					jumlah_lembur = 0
				alpa = attendances
				rekap_absen_perdivisi = self.pool.get('laporan.rekap.absen.perdivisi').create(cr,1,{'name':employee_ids,
																'date_from':wizard.date_from,
																'date_to':wizard.date_to,
																'department_id' : wizard.department_id.name,
																'lokasi_id' : brw_emps.address_id2.name,
																'job_id' : brw_emps.job_id.name,
																'terlambat':terlambat,
																'pc' : pc,
																'lembur' : total_lembur,
																'real_lembur' : real_lembur,
																'detail_ids' : dat,
																'alpa' : alpa,
																'user_id':SUPERUSER_ID,
																'tk' : tk,
																'cuti':leaves_cuti,
																'sakit':leaves_sakit})

			view_ref = self.pool.get('ir.model.data').get_object_reference(cr, SUPERUSER_ID, 'hrd_attendance', 'laporan_rekap_absen_perdivisi_tree')
			view_id = view_ref and view_ref[1] or False,

			desc 	= 'Laporan Rekap Absen Perdivisi'
			domain 	= []
			context = {}

			return self.hasil_rekap_absen_perdivisi(cr, SUPERUSER_ID, desc, ids[0], view_id, domain, context)