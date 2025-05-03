# -*- coding: utf-8 -*-

from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    milestone_ids = fields.One2many(
        'estate.milestone',
        'project_id',
        string='Hitos del Proyecto'
    ) 