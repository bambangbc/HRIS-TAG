# -*- coding: utf-8 -*-
# @Author: xrix
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from openerp.exceptions import except_orm


class purchaseConfirmWizard(models.TransientModel):
    _name = 'hr.leave.confirm'

    warning = fields.Char(readonly=True)

    @api.multi
    def leave_confirm(self):
        ctx = self._context.copy()
        # if not self.env['res.users'].has_group('hrd_leave.group_approve_hr'):
        #     raise except_orm(_('Warning!'),
        #                      _('Only Authorized user can do this operation.'))
        obj = self.env['hr.holidays']
        for leaves in ctx.get('active_ids',[]):
            leaves_id = obj.browse(leaves)
            if leaves_id.state == 'draft':
                leaves_id.write({'state':'confirm'})
            elif leaves_id.state == 'confirm' and True == self.env['res.users'].has_group('hrd_leave.group_approve_korwil'):
                leaves_id.write({'state':'approve1'})
            elif leaves_id.state == 'approve1' and True == self.env['res.users'].has_group('hrd_leave.group_approve_pic'):
                leaves_id.write({'state':'approve2'})
            elif leaves_id.state == 'approve2' and True == self.env['res.users'].has_group('hrd_leave.group_approve_deputi'):
                leaves_id.write({'state':'approve3'})
            elif leaves_id.state == 'approve3' and True == self.env['res.users'].has_group('hrd_leave.group_approve_manager'):
                leaves_id.write({'state':'validate'})
            #elif leaves_id.state == 'approve4' and True == self.env['res.users'].has_group('hrd_leave.group_approve_vp'):
            #    leaves_id.write({'state':'validate1'})
            #elif leaves_id.state == 'validate1' and True == self.env['res.users'].has_group('hrd_leave.group_approve_hr'):
            #    leaves_id.write({'state':'validate'})
            #elif leaves_id.state == 'validate' and True == self.env['res.users'].has_group('hrd_leave.group_approve_hr'):
            #    leaves_id.write({'state':'refuse'})

    @api.model
    def default_get(self, fields_list):
        warning = ''
        skipped = []
        ctx = self.env.context.copy()
        obj = self.env['hr.holidays']
        for leaves in ctx.get('active_ids',[]):
            leaves_id = obj.browse(leaves)
            if leaves_id.state != 'confirmed':
                skipped.append(leaves_id.employee_id.employee_name)
        if skipped:
            warning = 'Except for mentioned, orders will not processed (orders without lines or already confirmed) : '+', '.join(skipped)
        return {'warning' : warning}
