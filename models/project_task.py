# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Renombrado para evitar conflicto con sale_project
    estate_milestone_id = fields.Many2one(
        'estate.milestone',
        string='Hito Estate (Custom)', # Cambiado string para claridad
        domain="[ ('project_id', '=', project_id) ]",
        index=True,
        tracking=True,
        copy=False
    )

    # Actualizado onchange para el nuevo nombre
    @api.onchange('project_id')
    def _onchange_project_id_clear_estate_milestone(self):
        if self.project_id and self.estate_milestone_id and self.estate_milestone_id.project_id != self.project_id:
            self.estate_milestone_id = False

    # --- Bloque de herencia de _compute_sale_line eliminado ---

    # --- Herencia para solucionar conflicto con sale_project (@depends) ---

    # Heredamos _compute_sale_line para redefinir su lógica de cálculo,
    # evitando el acceso a task.estate_milestone_id.sale_line_id.
    # Usamos el @api.depends limpio que no causaba el error de validación inicial.
    @api.depends('sale_line_id.order_partner_id', 'parent_id.sale_line_id', 'project_id.sale_line_id', 'allow_billable')
    def _compute_sale_line(self):
        """
        Compute method override for sale_line_id.
        This replicates the logic from sale_project but avoids accessing
        self.estate_milestone_id.sale_line_id, which causes errors because
        our estate.milestone model doesn't have that field.
        We DO NOT call super() here because we are replacing the logic.
        """
        for task in self:
            # Reset first in case dependencies change
            task.sale_line_id = False

            if not (task.allow_billable or task.parent_id.allow_billable):
                # If task is not billable, ensure sale_line_id is False
                continue # Skip to next task

            # Replicate original logic to find sale_line from parent or project
            sale_line = False
            # Check parent task first
            if task.parent_id.sale_line_id and task.parent_id.partner_id.commercial_partner_id == task.partner_id.commercial_partner_id:
                sale_line = task.parent_id.sale_line_id
            # If not found in parent, check project
            elif task.project_id.sale_line_id and task.project_id.partner_id.commercial_partner_id == task.partner_id.commercial_partner_id:
                sale_line = task.project_id.sale_line_id

            # Assign the found sale_line (or False if none found).
            # CRUCIALLY, DO NOT add 'or task.estate_milestone_id.sale_line_id' here.
            task.sale_line_id = sale_line

    # -----------------------------------------------------------------

    # Optional: Si quieres limpiar el hito si cambia el proyecto de la tarea
    # @api.onchange('project_id')
    # def _onchange_project_id_clear_estate_milestone(self):
    #     if self.project_id and self.estate_milestone_id and self.estate_milestone_id.project_id != self.project_id:
    #         # Si el hito asignado no pertenece al nuevo proyecto, lo limpiamos
    #         self.estate_milestone_id = False
        # Devuelve un dominio actualizado (útil si no se usa @api.depends en el campo)
        # return {'domain': {'estate_milestone_id': [('project_id', '=', self.project_id)]}} 