import datetime
import time
from openerp.report import report_sxw
from openerp.osv import osv
 


class addendumPrint(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(addendumPrint, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })


class addendum(osv.AbstractModel):
    _name = 'report.hrd_employee.report_addendum'
    _inherit = 'report.abstract_report'
    _template = 'hrd_employee.report_addendum'
    _wrapped_report_class = addendumPrint
