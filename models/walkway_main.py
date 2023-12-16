from odoo import models, fields, api, _
from datetime import datetime, timedelta


class WalkwayProgramForm(models.Model):
    _name = 'walkway.program'
    _description = 'Walkway Program'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    class_teacher_id = fields.Many2one('res.users', string='Class Teacher', required=True)
    scheduled_date = fields.Date(string='Scheduled Date', required=True)
    branch = fields.Many2one('logic.base.branches', related='batch_id.branch_id', string='Branch')
    state = fields.Selection([
        ('draft', 'Draft'), ('done', 'Done'), ('cancelled', 'Cancelled')], default='draft', tracking=True)
    walk_ids = fields.One2many('walkway.students.list', 'walk_id', string="Walkway", default=False)
    batch_strength = fields.Integer(string='Batch Strength', compute='_compute_batch_strength', store=True)
    attended_students = fields.Integer(string='Attended Students', compute="onchange_walk_ids")
    attend_out_of_strength = fields.Char(string='Attended Students', compute="onchange_walk_ids")
    program_coordinator_id = fields.Many2one('res.users', string='Program Coordinator', default=lambda self: self.env.user)

    @api.depends('batch_id')
    def _compute_batch_strength(self):
        for rec in self:

            if rec.batch_id:
                strength = self.env['logic.students'].sudo().search_count([('batch_id', '=', rec.batch_id.id)])
                print(strength, 'strength')
                rec.batch_strength = strength
            # rec.attend_out_of_strength = str(rec.attended_students) + '/' + str(rec.batch_strength)

    @api.depends('walk_ids.student_id', 'batch_id')
    def onchange_walk_ids(self):
        for rec in self:
            if rec.walk_ids:
                rec.attended_students = len(rec.walk_ids)
                rec.attend_out_of_strength = str(rec.attended_students) + '/' + str(rec.batch_strength)
            else:
                rec.attended_students = 0
                rec.attend_out_of_strength = 0

    def _compute_display_name(self):
        for rec in self:
            if rec.batch_id:
                rec.display_name = 'Walkway Program ' + str(rec.batch_id.name)
            else:
                rec.display_name = 'Walkway Program'

    @api.onchange('class_teacher_id')
    def onchange_class_teacher(self):
        self.batch_id = False
        if self.class_teacher_id:
            batch = self.env['logic.base.batch'].sudo().search([])
            batches = []
            batches.clear()
            for i in batch:
                print(i.name, 'batch')
                batches.append(i.id)
            domain = [('id', 'in', batches)]
            print(domain, 'domain')
            print(batches, 'batches')

            return {'domain': {'batch_id': domain}}

    batch_id = fields.Many2one('logic.base.batch', string='Batch', domain=onchange_class_teacher)

    # @api.onchange('batch_id')
    # def onchange_batch_students(self):
    #     unlink_commands = [(3, child.id) for child in self.walk_ids]
    #     self.write({'walk_ids': unlink_commands})
    #     students = self.env['logic.students'].search([('batch_id', '=', self.batch_id.id)])
    #
    #     for i in students:
    #         if self.batch_id:
    #             print(i.name, 'std')
    #             self.walk_ids = [(0, 0, {'student_id': i.id})]
    #         else:
    #             self.walk_ids = []

    def activity_cron_for_coordinator(self):
        current_date = datetime.now().date()
        one_day_after = current_date + timedelta(days=1)
        print(one_day_after, 'one_day_after')
        rec = self.env['walkway.program'].sudo().search([])
        for i in rec:
            if i.scheduled_date == one_day_after:
                if i.state == 'draft':
                    i.activity_schedule('walkway_program.mail_walkway_coordinator_alert', user_id=i.class_teacher_id.id,
                                        note=f'{i.batch_id.name} This batch walkway program scheduled.')
                    print('ya')
                    print(i.scheduled_date)
            else:
                print('na')

    def action_cancel(self):
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('walkway_program.mail_walkway_coordinator_alert').id)])
        activity_id.action_feedback(feedback=f'batch walkway cancelled.')
        self.state = 'cancelled'

    def action_submit(self):
        activity_id = self.env['mail.activity'].search(
            [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('walkway_program.mail_walkway_coordinator_alert').id)])
        activity_id.action_feedback(feedback=f'batch walkway submitted.')
        self.state = 'done'
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Walkaway Program Submitted Successfully',
                'type': 'rainbow_man',
            }
        }

    @api.model
    def create(self, vals):
        record = super(WalkwayProgramForm, self).create(vals)
        # Set the sequence number for each child record
        for index, child in enumerate(record.walk_ids, start=1):
            child.write({'sequence': index})
        return record

    def write(self, vals):
        result = super(WalkwayProgramForm, self).write(vals)
        # Update the sequence number for each child record
        for index, child in enumerate(self.walk_ids, start=1):
            child.write({'sequence': index})
        return result


class WalkwayStudentsList(models.Model):
    _name = 'walkway.students.list'
    _description = 'Walkway Students List'

    student_id = fields.Many2one('logic.students', string='Student')
    program = fields.Char(string='Program')
    walk_id = fields.Many2one('walkway.program', string='Walkway', ondelete='cascade')
    sequence = fields.Integer(string="SI Number", default=1)


