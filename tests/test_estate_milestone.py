from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from datetime import date, timedelta

class TestEstateMilestone(TransactionCase):

    def setUp(self):
        super(TestEstateMilestone, self).setUp()
        self.Milestone = self.env['estate.milestone']
        self.ResUsers = self.env['res.users']
        self.Project = self.env['project.project']
        
        # Crear un usuario de prueba
        self.test_user = self.ResUsers.create({
            'name': 'Test User Milestone',
            'login': 'test_milestone_user',
        })

        # Crear un proyecto de prueba
        self.test_project = self.Project.create({
            'name': 'Proyecto de Prueba Hitos',
            'user_id': self.test_user.id,
        })

        # Crear un hito con fecha pasada para probar 'overdue'
        yesterday = date.today() - timedelta(days=1)
        self.milestone_overdue = self.Milestone.create({
            'name': 'Hito Atrasado Test',
            'project_id': self.test_project.id,
            'planned_date': yesterday,
            'responsible_id': self.test_user.id,
            'state': 'pending', 
        })

        # Crear un hito con fecha futura
        tomorrow = date.today() + timedelta(days=1)
        self.milestone_not_overdue = self.Milestone.create({
            'name': 'Hito Futuro Test',
            'project_id': self.test_project.id,
            'planned_date': tomorrow,
            'responsible_id': self.test_user.id,
            'state': 'pending',
        })
        
        # Crear un hito con fecha pasada pero ya realizado
        self.milestone_done = self.Milestone.create({
            'name': 'Hito Realizado Test',
            'project_id': self.test_project.id,
            'planned_date': yesterday,
            'responsible_id': self.test_user.id,
            'state': 'done',
        })


    def test_01_milestone_overdue_computation(self):
        """ Prueba que el campo 'overdue' se calcule correctamente. """
        
        # Forzar recálculo (aunque store=True debería manejarlo en creación)
        # En Odoo 15+ el cómputo store=True se dispara en create/write, pero 
        # recomputar aquí asegura que la prueba sea robusta en diferentes versiones/configuraciones.
        self.milestone_overdue.invalidate_cache(fnames=['overdue'])
        self.milestone_not_overdue.invalidate_cache(fnames=['overdue'])
        self.milestone_done.invalidate_cache(fnames=['overdue'])
        
        self.env.invalidate_all()
        self.env.flush_all()

        self.assertTrue(self.milestone_overdue.overdue, "El hito con fecha pasada y estado pendiente debería estar atrasado.")
        self.assertFalse(self.milestone_not_overdue.overdue, "El hito con fecha futura no debería estar atrasado.")
        self.assertFalse(self.milestone_done.overdue, "El hito realizado no debería estar marcado como atrasado, incluso si la fecha pasó.")

    def test_02_action_mark_done(self):
        """ Prueba la acción para marcar un hito como realizado. """
        self.assertEqual(self.milestone_not_overdue.state, 'pending', "El estado inicial debe ser pendiente.")
        self.milestone_not_overdue.action_mark_done()
        self.assertEqual(self.milestone_not_overdue.state, 'done', "El estado después de la acción debe ser realizado.")

        # Probar marcar como realizado un hito ya realizado (debería lanzar UserError)
        with self.assertRaises(UserError, msg="Intentar marcar como realizado un hito ya realizado debería fallar."):
            self.milestone_done.action_mark_done()

    # --- Pruebas para el Cron (requiere mocking) ---
    # def test_03_cron_sends_reminders(self):
    #     """ Prueba (mockeada) que el cron busca y procesa hitos atrasados. """
    #     # Esta prueba es más compleja y requiere mockear 'message_post' 
    #     # o el método de envío de emails si se implementa la opción 2.
    #     
    #     # Ejemplo conceptual con mock (necesitaría 'unittest.mock')
    #     # from unittest.mock import patch
    #     # with patch.object(type(self.Milestone), 'message_post') as mock_message_post:
    #     #     self.env['estate.milestone']._cron_send_overdue_milestone_reminders()
    #     #     # Verificar que message_post fue llamado para milestone_overdue
    #     #     mock_message_post.assert_called_once_with( ... argumentos esperados ... )
    #     #     # Verificar que no fue llamado para los otros
    #     #     # ...
    #     pass # Dejar pendiente o implementar con mock si es necesario 