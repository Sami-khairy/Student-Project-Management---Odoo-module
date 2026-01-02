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
    
    # Champs pour la Soutenance
    defense_date = fields.Datetime(string="Date de Soutenance", tracking=True)
    defense_location = fields.Char(string="Salle / Lieu")
    jury_ids = fields.Many2many(
        'res.partner', 
        'student_project_jury_rel',
        'project_id',
        'partner_id',
        string="Membres du Jury",
        help="Sélectionnez les membres du jury (en plus du tuteur)."
    )

    # Jalons & Livrables
    milestone_ids = fields.One2many(
        'student.project.milestone', 
        'project_id', 
        string="Livrables & Jalons"
    )
    progress = fields.Float(string="Progression", compute="_compute_progress", store=True)

    # Évaluation Détaillée
    grade_report = fields.Float(string="Note Rapport (/10)", default=0.0, tracking=True)
    grade_oral = fields.Float(string="Note Présentation (/5)", default=0.0, tracking=True)
    grade_technical = fields.Float(string="Qualité Technique (/5)", default=0.0, tracking=True)
    
    grade = fields.Float(string="Note Finale (/20)", compute="_compute_total_grade", store=True, tracking=True)

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

    def action_send_defense_invitation(self):
        """ Envoie une convocation via le Chatter à tous les participants """
        for record in self:
            if not record.defense_date:
                raise models.ValidationError("Veuillez définir une date de soutenance avant d'envoyer les convocations.")
            
            partners = record.student_ids | record.jury_ids | record.supervisor_id
            if not partners:
                raise models.ValidationError("Aucun participant (étudiant, tuteur ou jury) n'est assigné.")

            subject = f"Convocation Soutenance : {record.name}"
            body = f"Vous êtes invité à la soutenance du projet du {record.defense_date}. Lieu : {record.defense_location or 'Non spécifié'}."
            
            record.message_post(body=body, subject=subject, partner_ids=partners.ids)

    @api.depends('milestone_ids', 'milestone_ids.is_done')
    def _compute_progress(self):
        for record in self:
            if not record.milestone_ids:
                record.progress = 0.0
            else:
                total = len(record.milestone_ids)
                done = len(record.milestone_ids.filtered(lambda m: m.is_done))
                record.progress = (done / total) * 100

    @api.depends('grade_report', 'grade_oral', 'grade_technical')
    def _compute_total_grade(self):
        for record in self:
            record.grade = record.grade_report + record.grade_oral + record.grade_technical

    @api.constrains('grade_report', 'grade_oral', 'grade_technical')
    def _check_sub_grades(self):
        for record in self:
            if not (0 <= record.grade_report <= 10):
                raise models.ValidationError("La note du rapport doit être entre 0 et 10.")
            if not (0 <= record.grade_oral <= 5):
                raise models.ValidationError("La note orale doit être entre 0 et 5.")
            if not (0 <= record.grade_technical <= 5):
                raise models.ValidationError("La note technique doit être entre 0 et 5.")
