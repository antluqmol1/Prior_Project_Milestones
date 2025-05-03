{
    'name': "Prior Project Milestones",
    'summary': """
        Gestión de Hitos de Obra y Recordatorios Automáticos
    """,
    'description': """
        Módulo para descomponer proyectos en hitos, asignar responsables y fechas, 
        y enviar recordatorios automáticos para hitos pendientes o atrasados.
    """,
    'author': "Antonio Luque",
    'website': "https://nuevoprior.es/",
    'category': 'Project',
    'version': '1.0',
    'depends': ['base', 'mail', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_milestone_views.xml',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/estate_milestone_menus.xml',
        'data/cron_milestones.xml', #  Debemos asegurarnos que se cargue después de las vistas si es necesario
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
} 