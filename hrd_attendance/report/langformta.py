import datetime
import time
from openerp.report import report_sxw
from openerp.osv import osv
 


class rekapPrint(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(rekapPrint, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })


class quotation(osv.AbstractModel):
    _name = 'report.hrd_attendance.print_rekap_absen'
    _inherit = 'report.abstract_report'
    _template = 'hrd_attendance.print_rekap_absen'
    _wrapped_report_class = rekapPrint

class rekap_divisi(osv.AbstractModel):
    _name = 'report.hrd_attendance.print_rekap_absen_perdivisi'
    _inherit = 'report.abstract_report'
    _template = 'hrd_attendance.print_rekap_absen_perdivisi'
    _wrapped_report_class = rekapPrint