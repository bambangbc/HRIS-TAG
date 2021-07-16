import time
from openerp.report import report_sxw 

class rekap_perorangan(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(rekap_perorangan, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.rekap_perorangan', 'laporan.rekap.absen.perorangan', 'TAG/hrd_attendance/report/rekap_perorangan.rml', parser=rekap_perorangan) 