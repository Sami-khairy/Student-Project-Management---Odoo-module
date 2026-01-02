from odoo import models, fields, api

class StudentProject(models.Model):
    _name = "student.project"
    _description = "Student Project Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Titre du projet", required=True, tracking=True)
    description = fields.Html(string="Description du sujet")
    
    project_type = fields.Selection([
        ('pfe', 'PFE'),
        ('pfa', 'PFA'),
        ('mini_projet', 'Mini-projet'),
        ('stage', 'Stage')
    ], string="Type de Projet", default='mini_projet', tracking=True)

    # Relation avec les étudiants (res.partner)
    student_ids = fields.Many2many(
        'res.partner', 
        string="Étudiant(s)",
        help="Sélectionnez les étudiants assignés à ce projet."
    )

    # Relation avec le tuteur (Supervisor)
    supervisor_id = fields.Many2one(
        'res.partner', 
        string="Tuteur (Professeur)", 
        tracking=True
    )

    date_deadline = fields.Date(string="Date limite", tracking=True)
    repository_url = fields.Char(string="Lien Repository (Git)")
    
    grade = fields.Float(string="Note Finale (/20)", tracking=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('validation', 'Validation'),
        ('in_progress', 'En cours'),
        ('submitted', 'Rendu'),
        ('done', 'Noté')
    ], string="État", default='draft', tracking=True, group_expand='_expand_states')

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    # Workflow Actions
    def action_draft(self):
        self.state = 'draft'

    def action_validate(self):
        self.state = 'validation'

    def action_in_progress(self):
        self.state = 'in_progress'

    def action_submit(self):
        self.state = 'submitted'

    def action_done(self):
        self.state = 'done'

    @api.constrains('grade')
    def _check_grade(self):
        for record in self:
            if record.grade < 0 or record.grade > 20:
                raise models.ValidationError("La note doit être comprise entre 0 et 20 !")