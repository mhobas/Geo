from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta


class res_partner_category(models.Model):
    _name = 'alfolk.partner.category'
    _description = 'Partner Category'
    _rec_name = 'name'

    name = fields.Char('Name', store=True)

    category_type = fields.Selection([
        ('resident', 'resident'), ('non', 'Non-resident')], string='Category Type')


class res_partner_edit(models.Model):
    _inherit = 'res.partner'
    category = fields.Many2one('alfolk.partner.category', store=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], store=True)
    father_name = fields.Char('Father Name', store=True)
    mother_name = fields.Char('Mother Name', store=True)
    date_of_birth = fields.Date('Birth Of Date', store=True)

    @api.depends('date_of_birth')
    def compute_age(self):
        for record in self:
            if record.date_of_birth:
                rdelta = relativedelta(date.today(), record.date_of_birth)
                record.age = rdelta
            else:
                record.age = False

    age = fields.Char('Age', store=True, compute='compute_age')
