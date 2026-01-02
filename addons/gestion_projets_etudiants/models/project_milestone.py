from odoo import models, fields, api

class ProjectMilestone(models.Model):
    _name = "student.project.milestone"
    _description = "Jalon / Livrable du Projet"
    _order = "deadline, id"

    project_id = fields.Many2one('student.project', string="Projet", required=True, ondelete='cascade')
    name = fields.Char(string="Titre du Livrable", required=True)
    description = fields.Text(string="Description")
    deadline = fields.Date(string="Date Limite")
    is_done = fields.Boolean(string="Terminé")
    file_attachment = fields.Binary(string="Fichier Joint")
    file_name = fields.Char(string="Nom du Fichier")
