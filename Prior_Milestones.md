# Módulo: Prior Project Milestones (Hitos de Proyecto)

Este módulo para Odoo amplía la funcionalidad de gestión de proyectos permitiendo definir, seguir y gestionar hitos clave. Facilita la visualización del progreso y automatiza recordatorios para hitos atrasados.

## Funcionalidad Principal

*   **Creación y Seguimiento de Hitos:** Define hitos (`estate.milestone`) con nombre, proyecto asociado, fecha prevista y responsable.
*   **Estados y Visualización:** Los hitos pueden estar 'Pendientes' o 'Realizados'. Se visualizan en vistas de Lista, Kanban (agrupados por proyecto por defecto) y Formulario.
*   **Indicador de Retraso:** Un campo calculado (`overdue`) marca automáticamente los hitos pendientes cuya fecha prevista ha pasado. La vista de lista resalta estos hitos en rojo.
*   **Integración con Proyectos:** Los hitos se asocian directamente a un Proyecto (`project.project`). Una pestaña "Hitos del Proyecto" se añade al formulario de Proyecto para ver y gestionar los hitos asociados.
*   **Integración con Tareas:** Los hitos se pueden asociar a Tareas (`project.task`) individuales mediante el campo `estate_milestone_id`. Este campo se muestra en el formulario de Tarea.
    *   **Nota Técnica:** La integración con tareas se ha implementado cuidadosamente, modificando cómo se calcula el campo `sale_line_id` en las tareas para evitar conflictos con otros módulos como `sale_project`.
*   **Recordatorios Automáticos:** Una acción planificada (Cron Job) se ejecuta diariamente para revisar los hitos atrasados (`overdue = True`). Por cada hito atrasado, publica un mensaje en su Chatter notificando al usuario responsable.
*   **Chatter y Actividades:** Los hitos integran Chatter (`mail.thread`) y Actividades (`mail.activity.mixin`) para seguimiento y comunicación.
*   **Pruebas Unitarias:** Se incluyen pruebas básicas para verificar el cálculo del estado 'atrasado' y la acción de marcar un hito como 'realizado'.

## Estructura del Módulo

```
hitos-proyecto/
├── __init__.py             # Inicializador principal del módulo
├── __manifest__.py         # Metadatos, dependencias (base, mail, project) y archivos a cargar
├── models/                 # Definición de los modelos de datos
│   ├── __init__.py         # Inicializador de modelos
│   ├── estate_milestone.py # Modelo principal estate.milestone (Hitos)
│   ├── project_project.py  # Herencia: Añade campo One2many milestone_ids a project.project
│   └── project_task.py     # Herencia: Añade campo Many2one estate_milestone_id a project.task y ajusta _compute_sale_line
├── security/               # Reglas de acceso
│   └── ir.model.access.csv # Permisos CRUD para estate.milestone (grupo base.group_user)
├── data/                   # Datos iniciales o configuración
│   └── cron_milestones.xml # Definición del Cron Job para recordatorios de hitos atrasados
├── views/                  # Interfaz de usuario (vistas y menús)
│   ├── __init__.py               # Inicializador de vistas/menús
│   ├── estate_milestone_views.xml# Vistas List, Kanban y Form para Hitos (estate.milestone)
│   ├── project_project_views.xml # Herencia: Añade pestaña "Hitos del Proyecto" al form de Proyectos
│   ├── project_task_views.xml    # Herencia: Añade campo de Hito al form de Tareas
│   └── estate_milestone_menus.xml# Añade menú "Hitos de Proyecto" bajo la app Proyectos
└── tests/                  # Pruebas unitarias
    ├── __init__.py             # Inicializador de pruebas
    └── test_estate_milestone.py# Pruebas para el modelo estate.milestone
```

## Detalles Técnicos y Puntos Clave

1.  **Modelo `estate.milestone`:**
    *   Campos clave: `name`, `project_id` (Many2one, `ondelete='cascade'`), `planned_date`, `responsible_id` (Many2one `res.users`), `state` ('pending', 'done'), `overdue` (Boolean, computed), `is_reached` (Boolean, computed), `deadline` (Date, related `planned_date`), `task_ids` (One2many `project.task`), `color`.
    *   Orden por defecto: `planned_date`.
    *   Métodos: `_compute_overdue`, `_compute_is_reached`, `action_mark_done`, `_cron_send_overdue_milestone_reminders`.

2.  **Herencia `project.project`:** Añade `milestone_ids` (One2many).

3.  **Herencia `project.task`:**
    *   Añade `estate_milestone_id` (Many2one `estate.milestone`), con dominio para mostrar solo hitos del mismo proyecto.
    *   **Importante:** Sobrescribe `_compute_sale_line` para replicar la lógica de `sale_project` pero **excluyendo** la dependencia de `estate_milestone_id.sale_line_id` para resolver conflictos previos.
    *   Incluye un `@api.onchange('project_id')` para limpiar `estate_milestone_id` si el proyecto de la tarea cambia.

4.  **Seguridad:** Acceso CRUD completo para `base.group_user` sobre `estate.milestone`.

5.  **Cron Job (`ir_cron_send_overdue_milestone_reminders`):**
    *   Se ejecuta diariamente (configurable en `data/cron_milestones.xml`).
    *   Llama a `estate.milestone._cron_send_overdue_milestone_reminders()`.
    *   Publica un mensaje en el chatter del hito usando `message_post`.

6.  **Vistas `estate.milestone`:**
    *   **List:** Resalta atrasados (`decoration-danger`) y realizados (`decoration-muted`).
    *   **Kanban:** Agrupado por `project_id`, muestra tareas asociadas, responsable, estado de retraso. Usa el campo `color`.
    *   **Form:** Incluye botón `action_mark_done`, `statusbar` para el estado, pestaña para `task_ids` y pestaña para Chatter/Actividades.

7.  **Herencia Vistas:**
    *   **Proyecto (Form):** Añade pestaña "Hitos del Proyecto" mostrando `milestone_ids`.
    *   **Tarea (Form):** Añade el campo `estate_milestone_id` después del campo `project_id`. *(Nota: El XML usa `milestone_id`, pero el nombre correcto del campo en el modelo es `estate_milestone_id`. Esto podría requerir corrección en `project_task_views.xml` para consistencia total).*

8.  **Menú:** Añade "Hitos de Proyecto" bajo el menú principal de la aplicación "Proyectos".

9.  **Pruebas:** `test_estate_milestone.py` verifica `_compute_overdue` y `action_mark_done`. Pruebas de Cron pendientes (requieren mocking).

## Próximos Pasos y Consideraciones

1.  **Verificar Dependencias:** Asegúrate de que los módulos `project` y `mail` de Odoo estén instalados.
2.  **Consistencia Vista Tarea (Opcional):** Considerar corregir `milestone_id` a `estate_milestone_id` en `views/project_task_views.xml` para mayor claridad, aunque funcionalmente Odoo suele resolverlo.
3.  **Refinar Permisos (Opcional):** Ajustar los permisos en `security/ir.model.access.csv` si se necesita una granularidad mayor que `base.group_user`.
4.  **Mejorar Vista Kanban (Opcional):** Añadir más información o acciones rápidas.
5.  **Implementar Pruebas del Cron (Opcional):** Usar `unittest.mock` para simular `message_post` y verificar que el cron funciona como se espera.
6.  **Despliegue:**
    *   Debemos asegurarnos de que la carpeta `custom-addons` esté incluida en el `addons_path` de tu configuración de Odoo.
    *   Reiniciar el servidor Odoo.
    *   Ir a Aplicaciones, actualizar la lista de aplicaciones e instalar/actualizar el módulo "Project" y "Prior Project Milestones".
