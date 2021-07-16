from openerp.osv import osv,fields
from openerp.tools.translate import _
import datetime
import openerp.addons.decimal_precision as dp

class laporan_rekap_absen_perorangan(osv.osv):
	_name = "laporan.rekap.absen.perorangan"

	_columns = {
		'name' : fields.many2one('hr.employee', 'Nama Karyawan'),
		'user_id': fields.many2one('res.users', 'users'),
		'department_id' : fields.char('Divisi'),
		'job_id' : fields.many2one('hr.job', 'Posisi'),
		'lokasi_id' : fields.char('Lokasi Kerja'),
		'date_from' : fields.date('dari'),
		'date_to' : fields.date('Sampai'),
		'terlambat' : fields.integer('Terlambat'),
		'pc' : fields.integer('Pulang Cepat'),
		'alpa' : fields.integer('Alpa'),
		'tk' : fields.integer('TK'),
		'cuti' : fields.integer('Cuti'),
		'sakit' : fields.integer('Sakit'),
		'lembur' : fields.float('Total Point lembur'),
		'real_lembur' : fields.float('Total Jam Lembur'),
		'flat' : fields.boolean('Flat'),
		'detail_ids' : fields.one2many('rekap.detail','rekap_id','Detail Absensi'),
	}

class rekap_detail(osv.osv):
	_name = "rekap.detail"

	_columns = {
		'date' : fields.date('Tanggal'),
		'shift_id' : fields.char('Shift'),
		'user' : fields.many2one('res.users'),
		'jam_masuk' : fields.datetime('Jam Masuk'),
		'jam_pulang' : fields.datetime('Jam Pulang'),
		'terlambat' : fields.float('Terlambat'),
		'pc' : fields.float('Pulang Cepat'),
		'lembur' : fields.float('Lembur'),
		'spl' : fields.float('SPL'),
		'PL' : fields.float('Point Lembur'),
		'ket' : fields.char('Keterangan'),
		'rekap_id' : fields.many2one('laporan.rekap.absen.perorangan','Absensi'),
	}

class laporan_rekap_absen_perdivisi(osv.osv):
	_name = "laporan.rekap.absen.perdivisi"

	_columns = {
		'name' : fields.many2one('hr.employee', 'Nama Karyawan'),
		'user_id': fields.many2one('res.users', 'users'),
		'date_from' : fields.date('dari'),
		'date_to' : fields.date('Sampai'),
		'department_id' : fields.char('Divisi'),
		'lokasi_id' : fields.char('Lokasi Kerja'),
		'job_id' : fields.char("posisi"),
		'terlambat' : fields.integer('Terlambat'),
		'pc' : fields.integer('Pulang Cepat'),
		'alpa' : fields.integer('Alpa'),
		'tk' : fields.integer('TK'),
		'cuti' : fields.integer('Cuti'),
		'sakit' : fields.integer('Sakit'),
		'lembur' : fields.float('Total Point lembur'),
		'flat' : fields.boolean('Flat'),
		'real_lembur' : fields.float('Total Jam Lembur'),
		'detail_ids' : fields.one2many('rekap.detail.divisi','rekap_id','Detail Absensi'),
	}


class rekap_detail(osv.osv):
	_name = "rekap.detail.divisi"

	_columns = {
		'date' : fields.date('Tanggal'),
		'shift_id' : fields.char('Shift'),
		'jam_masuk' : fields.datetime('Jam Masuk'),
		'jam_pulang' : fields.datetime('Jam Pulang'),
		'terlambat' : fields.float('Terlambat'),
		'pc' : fields.float('Pulang Cepat'),
		'spl' : fields.float('SPL'),
		'lembur' : fields.float('Lembur'),
		'PL' : fields.float('Point Lembur'),
		'ket' : fields.char('Keterangan'),
		'rekap_id' : fields.many2one('laporan.rekap.absen.perdivisi','Absensi'),
	}