{
    'name': 'Student Project Management',
    'version': '1.0',
    'summary': 'Academic Project Management System (PFE, PFA, etc.)',
    'category': 'Education',
    'author': 'KHAIRY Sami',
    'depends': ['base', 'mail', 'contacts'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/projet_etudiant_views.xml',
    ],
    'installable': True,
    'application': True,
}