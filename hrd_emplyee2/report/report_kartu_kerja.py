import datetime
import time
from openerp.report import report_sxw
from openerp.osv import osv
 


class kartukerjaPrint(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(kartukerjaPrint, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })


class kartukerja(osv.AbstractModel):
    _name = 'report.hrd_employee2.report_kartu_kerja'
    _inherit = 'report.abstract_report'
    _template = 'hrd_employee2.report_kartu_kerja'
    _wrapped_report_class = kartukerjaPrint
