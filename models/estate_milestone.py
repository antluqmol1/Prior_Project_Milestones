# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class EstateMilestone(models.Model):
    _name = 'estate.milestone'
    _description = 'Hito de Proyecto'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Para chatter y actividades
    _order = "planned_date" # Ordenación por defecto

    name = fields.Char(string='Nombre', required=True, tracking=True)
    project_id = fields.Many2one(
        'project.project', 
        string='Proyecto', 
        required=True, 
        ondelete='cascade', # Borrar hitos si se borra el proyecto
        index=True, # Buen índice para búsquedas
        tracking=True
    )
    planned_date = fields.Date(string='Fecha Prevista', required=True, tracking=True)
    responsible_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user, tracking=True)
    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('done', 'Realizado'),
    ], string='Estado', default='pending', required=True, tracking=True, copy=False)
    overdue = fields.Boolean(string='Atrasado', compute='_compute_overdue', store=True, tracking=True)
    is_reached = fields.Boolean(string="Alcanzado", compute='_compute_is_reached', store=True)
    deadline = fields.Date(related='planned_date', string="Fecha Límite (Relacionada)", store=True, readonly=True)
    task_ids = fields.One2many(
        'project.task',
        'estate_milestone_id', # Actualizado nombre del campo inverso
        string='Tareas Asociadas'
    )
    color = fields.Integer(string='Color Index') # Campo para color Kanban

    @api.depends('planned_date', 'state')
    def _compute_overdue(self):
        """Calcula si el hito está atrasado."""
        today = date.today()
        for record in self:
            record.overdue = bool(record.planned_date and record.planned_date < today and record.state == 'pending')

    @api.depends('state')
    def _compute_is_reached(self):
        """Calcula si el hito se considera alcanzado (estado = done)."""
        for record in self:
            record.is_reached = (record.state == 'done')

    def action_mark_done(self):
        """Marca el hito como realizado."""
        if any(record.state == 'done' for record in self):
             raise UserError(_("Algunos hitos seleccionados ya están marcados como 'Realizado'."))
        return self.write({'state': 'done'})

    # --- Métodos del Cron ---
    
    def _cron_send_overdue_milestone_reminders(self):
        """Busca hitos atrasados y envía recordatorios."""
        overdue_milestones = self.search([('overdue', '=', True)])
        for milestone in overdue_milestones:
            # Opción 1: Crear una actividad/mensaje en el chatter del hito
            # (Requiere 'mail' en depends y _inherit)
            milestone.message_post(
                body=_("Recordatorio: El hito '%s' está atrasado. Fecha prevista: %s") % (milestone.name, milestone.planned_date),
                subject=_("Hito Atrasado: %s") % milestone.name,
                partner_ids=[milestone.responsible_id.partner_id.id] if milestone.responsible_id else [], # Notificar al responsable si existe
                message_type='notification',
                subtype_xmlid='mail.mt_comment', # O un subtipo personalizado
            )
            
            # Opción 2: Enviar un correo electrónico (más complejo, requiere plantillas de email)
            # mail_template = self.env.ref('prior_milestones.email_template_overdue_milestone', raise_if_not_found=False)
            # if mail_template and milestone.responsible_id.email:
            #     mail_template.send_mail(milestone.id, force_send=True)

        return True 