from odoo import models, fields, api, _
from odoo.exceptions import UserError

WeakDays = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
from calendar import monthrange


class ApplyFormDesign(models.Model):
    _name = 'form.apply'
    _description = 'Form Apply'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'complete_name'
    form_id = fields.Many2one('form.design', 'Form', store=True, index=True, tracking=True)
    partner_id = fields.Many2one('res.partner', 'Partner', store=True, index=True, tracking=True, required=1)
    apply_ids = fields.One2many('form.apply.line', 'apply_id', store=True, index=True, tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Closed')], default='draft', store=True,
                             tracking=True)
    date = fields.Date('Date', default=fields.Date.today(), tracking=True, store=True, index=True, required=1)
    complete_name = fields.Char('Name', compute='_compute_name', store=True, index=True, tracking=True)
    allow_add = fields.Boolean("Allow Add Line", compute="compute_allow_add_line")

    def view_form_fill_in_line(self):
        return {
            'name': _('Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'form.apply.line',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.apply_ids.ids)],
            'context': self.env.context,
        }

    @api.depends('form_id', 'date', 'partner_id')
    def _compute_name(self):
        for record in self:
            name = ''
            if record.form_id:
                name += record.form_id.name
            if record.partner_id:
                name += ' ' + record.partner_id.name
            if record.date:
                name += ' ' + str(record.date)
            record.complete_name = name

    def set_close(self):
        self.state = 'confirmed'

    @api.onchange('form_id')
    def form_change(self):
        if self.state == 'draft':
            self.apply_ids.unlink()
            lines = self.apply_ids
            for line in self.form_id.question_ids:
                matrix_lines = []
                if line.question_type == 'matrix':
                    for m in line.suggested_answer_ids:
                        if line.matrix_answer_ids:
                            for c in line.matrix_answer_ids:
                                matrix_lines.append((0, 0, {
                                    'name': m.value,
                                    'val_name': c.value,

                                }))
                        elif line.matrix_coltype == 'month':
                            if not self.date:
                                raise UserError(_('Please Select Date'))
                            num_days = monthrange(self.date.year, self.date.month)[1]
                            for c in range(1, num_days + 1):
                                matrix_lines.append((0, 0, {
                                    'name': m.value,
                                    'val_name': c,

                                }))
                        elif line.matrix_coltype == 'week':
                            for c in range(0, 7):
                                matrix_lines.append((0, 0, {
                                    'name': m.value,
                                    'val_name': WeakDays[c],

                                }))
                lines += self.apply_ids.create({
                    'name': line.title,
                    'sequence': line.sequence,
                    'form_line_id': line.id,
                    'form_id': self.form_id.id,
                    'apply_id': self._origin.id,
                    'question_type': line.question_type,
                    'matrix_answer_type': line.matrix_answer_type,
                    'answers_ids': matrix_lines,
                })
            self.apply_ids = lines

    @api.onchange("form_id")
    def compute_allow_add_line(self):
        for record in self:
            if record.form_id:
                record.allow_add = record.form_id.allow_add
            else:
                record.allow_add = False

    def action_done(self):
        self.state = 'confirmed'

    def confirm(self):
        if self.apply_ids.filtered(lambda line: not line.answer or line.question_type == 'matrix'):
            return {
                'name': _('Answers'),
                'type': 'ir.actions.act_window',
                'res_model': 'form.apply.line',
                'view_mode': 'form',
                'view_id': self.env.ref('form_design.form_apply_line_form_view2').id,
                'res_id': self.apply_ids.filtered(lambda line: not line.answer)[0].id,
                'target': 'new',
                'domain': [('id', '=', self.apply_ids[0].id)],
                'context': self.env.context,
            }

    def add_line(self):
        if self.form_id.question_ids:
            return {
                'name': _('Answers'),
                'type': 'ir.actions.act_window',
                'res_model': 'form.apply.line',
                'view_mode': 'form',
                'view_id': self.env.ref('form_design.form_apply_line_form_view').id,
                'target': 'new',
                'context': {
                    'default_form_id': self.form_id.id,
                    'default_apply_id': self.id,
                    'default_form_line_id': self.form_id.question_ids[0].id
                },
            }


class FormApplyLine(models.Model):
    _name = 'form.apply.line'
    _description = 'Form Apply Line'
    _order = 'id'

    @api.onchange('form_line_id')
    def _onchange_form_line(self):
        for record in self:
            if record.form_line_id:
                record.name = record.form_line_id.title
                record.question_type = record.form_line_id.question_type

    @api.constrains('form_line_id')
    def constraint_form_line(self):
        for record in self:
            if record.form_line_id:
                record.name = record.form_line_id.title
                record.question_type = record.form_line_id.question_type

    sequence = fields.Integer('Label Sequence order', default=10)
    name = fields.Char('Title', store=True, index=True)
    answer = fields.Char('Answer', compute='compute_answer')
    note = fields.Char('Note', store=True, index=True)
    text_char = fields.Char('Answer', store=True, index=True)
    text = fields.Text('Answer', store=True, index=True)
    numerical_box = fields.Float('Numerical', store=True, index=True)
    date = fields.Date('Date', store=True, index=True)
    check = fields.Boolean('Check', store=True, index=True)
    date_time = fields.Datetime('Date Time', store=True, index=True)
    form_line_id = fields.Many2one('form.design.line', 'Question', domain="[('form_id','=',form_id)]", store=True,
                                   index=True)
    form_id = fields.Many2one('form.design', 'Form', store=True, index=True)
    apply_id = fields.Many2one('form.apply')
    suggested_id = fields.Many2one('form.line.answer', 'Suggested Answer', domain="[('question_id','=',form_line_id)]")
    suggested_ids = fields.Many2many('form.line.answer', string='Suggested Answer',
                                     domain="[('question_id','=',form_line_id)]")
    answers_ids = fields.One2many('form.apply.line.matrix', 'form_line_id', string='Matrix Answer', )
    answers_text_ids = fields.One2many('form.apply.line.matrix', 'form_line_id', string='Matrix Answer', )
    answers_date_ids = fields.One2many('form.apply.line.matrix', 'form_line_id', string='Matrix Answer', )
    answers_datetime_ids = fields.One2many('form.apply.line.matrix', 'form_line_id', string='Matrix Answer', )
    answers_char_ids = fields.One2many('form.apply.line.matrix', 'form_line_id', string='Matrix Answer', )
    question_type = fields.Selection([
        ('text_box', 'Multiple Lines Text Box'),
        ('char_box', 'Single Line Text Box'),
        ('numerical_box', 'Numerical Value'),
        ('check', 'True or False'),
        ('date', 'Date'),
        ('datetime', 'Datetime'),
        ('simple_choice', 'Multiple choice: only one answer'),
        ('multiple_choice', 'Multiple choice: multiple answers allowed'),
        ('matrix', 'Matrix')], string='Question Type',
        readonly=False, store=True)
    matrix_answer_type = fields.Selection([('date', 'Date'),
                                           ('datetime', 'DateTime'),
                                           ('boolean', 'Check Box'),
                                           ('char', 'Single Line Text Box'),
                                           ('text', 'Multiple Lines Text Box')], string='Matrix Answer Type',
                                          default='boolean')

    def confirm(self):
        ids = self.apply_id.apply_ids.mapped('id')
        ids.sort()
        if self.id in ids:
            next_index = ids.index(self.id) + 1
            if next_index < len(ids):
                return {
                    'name': _('Answers'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'form.apply.line',
                    'view_mode': 'form',
                    'view_id': self.env.ref('form_design.form_apply_line_form_view2').id,
                    'res_id': ids[next_index],
                    'target': 'new',
                    'context': self.env.context,
                }
            else:
                return {'type': 'ir.actions.act_window_close'}

    @api.onchange('text_char', 'text', 'check','numerical_box','date','date_time','suggested_id' 'suggested_ids','answers_ids')
    def compute_answer(self):
        for record in self:
            if record.question_type == 'char_box' and record.text_char:
                record.answer = record.text_char
            elif record.question_type == 'text_box' and record.text:
                record.answer = record.text
            elif record.question_type == 'check':
                record.answer = str(record.check)
            elif record.question_type == 'numerical_box' and record.numerical_box:
                record.answer = str(record.numerical_box)
            elif record.question_type == 'date' and record.date:
                record.answer = str(record.date)
            elif record.question_type == 'datetime' and record.date_time:
                record.answer = str(record.date_time)
            elif record.question_type == 'simple_choice' and record.suggested_id:
                record.answer = str(record.suggested_id.value)
            elif record.question_type == 'multiple_choice' and record.suggested_ids:
                record.answer = ','.join([l.value for l in record.suggested_ids])
            elif record.question_type == 'matrix':
                record.answer = ','.join([l.name + ' ' + l.val_name for l in record.answers_ids.filtered(lambda x: x.check)])
            else:
                record.answer=False


class FormApplyLineMatrix(models.Model):
    _name = 'form.apply.line.matrix'
    _description = 'Form Apply Line Matrix'
    check = fields.Boolean('Check')
    textChar = fields.Char('Answer')
    date = fields.Date('Answer')
    date_time = fields.Datetime('Answer')
    text = fields.Text('Answer')
    name = fields.Char('Row')
    val_name = fields.Char('Col')
    form_line_id = fields.Many2one('form.apply.line', 'Form Fill IN', ondelete='cascade', index=True)
