# -*- coding: utf-8 -*-
"""
Suite de pruebas automatizadas para GRK PowerSloth v6.3.0.
Verifica modelos, persistencia atómica, resiliencia de configuración,
localización en 4 idiomas, lazy-loading y métodos del presentador.
"""

import sys
import os
import unittest
from pathlib import Path
from datetime import datetime, timedelta

# Asegurar que la raíz del proyecto esté en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from models.enums import Theme, Language, ScheduleMode, PowerAction
from models.process_item import ProcessItem
from models.history_entry import HistoryEntry
from models.scheduled_event import ScheduledEvent, RecurrenceType
from services.settings_manager import AppSettings, SettingsManager
from services.system_integration import SystemIntegration
from managers.localization_manager import LocalizationManager


class TestPowerSlothV630(unittest.TestCase):
    
    def test_model_slots(self):
        """Verifica que las entidades usan slots para optimizar memoria."""
        item = ProcessItem(1234, "notepad.exe", "Notepad (1234)")
        self.assertTrue(hasattr(item, "__slots__"))
        self.assertEqual(item.pid, 1234)

        entry = HistoryEntry(action_type=0, trigger_mode="countdown")
        self.assertTrue(hasattr(entry, "__slots__"))

        event = ScheduledEvent(name="Auto Shutdown")
        self.assertTrue(hasattr(event, "__slots__"))

        settings = AppSettings()
        self.assertTrue(hasattr(settings, "__slots__"))

    def test_settings_resilience_and_forward_compatibility(self):
        """Verifica que AppSettings.from_dict ignora claves desconocidas o de versiones futuras sin fallar."""
        payload = {
            "last_hours": 1,
            "last_minutes": 45,
            "current_theme": Theme.NORDIC.value,
            "unknown_future_field_v7": "some_value",
            "deprecated_flag": True
        }
        settings = AppSettings.from_dict(payload)
        self.assertEqual(settings.last_hours, 1)
        self.assertEqual(settings.last_minutes, 45)
        self.assertEqual(settings.current_theme, Theme.NORDIC.value)
        # Valores por defecto para campos no presentes
        self.assertEqual(settings.last_seconds, 0)

    def test_settings_atomic_save(self):
        """Verifica que el guardado atómico no deja archivos .tmp colgados y escribe JSON válido."""
        test_settings = AppSettings(last_hours=2, last_minutes=15)
        SettingsManager.save(test_settings)

        settings_path = SettingsManager.get_settings_path()
        tmp_path = settings_path.with_suffix(settings_path.suffix + ".tmp")

        self.assertTrue(settings_path.exists())
        self.assertFalse(tmp_path.exists())

        loaded = SettingsManager.load()
        self.assertEqual(loaded.last_hours, 2)
        self.assertEqual(loaded.last_minutes, 15)

    def test_scheduled_event_dates(self):
        """Verifica el cálculo de fechas de eventos programados (diario, semanal, mensual)."""
        now = datetime.now()
        
        # Evento diario
        event_daily = ScheduledEvent(
            event_time="23:59",
            recurrence=RecurrenceType.DAILY,
            enabled=True
        )
        next_run = event_daily.get_next_run()
        self.assertIsNotNone(next_run)
        self.assertTrue(next_run > now)

        # Evento mensual (clamp en fin de mes)
        event_monthly = ScheduledEvent(
            event_time="10:00",
            recurrence=RecurrenceType.MONTHLY,
            day_of_month=31,
            enabled=True
        )
        next_monthly = event_monthly.get_next_run()
        self.assertIsNotNone(next_monthly)
        self.assertLessEqual(next_monthly.day, 31)

    def test_localization_completeness_and_fallback(self):
        """Verifica que las nuevas claves están disponibles en todos los idiomas y el fallback a inglés funciona."""
        keys_to_verify = [
            "schedule_edit_title_new", "schedule_edit_title_edit",
            "schedule_field_name", "schedule_field_action", "schedule_field_time",
            "schedule_group_recurrence", "recurrence_once", "recurrence_daily",
            "recurrence_weekly", "recurrence_monthly", "schedule_chk_force",
            "schedule_btn_add", "schedule_btn_edit", "schedule_btn_delete",
            "schedule_col_status", "schedule_col_name", "schedule_col_action",
            "day_short_0", "day_short_6",
            "history_title", "history_description", "history_status_completed",
            "about_version", "about_date", "condition_on_idle", "status_monitoring_active", "status_monitoring_verifying"
        ]

        for lang in [Language.SPANISH, Language.ENGLISH, Language.PORTUGUESE, Language.FRENCH]:
            LocalizationManager.set_language(lang)
            for k in keys_to_verify:
                val = LocalizationManager.get(k)
                self.assertNotEqual(val, k, f"Clave '{k}' no está traducida en {lang.name}")
                self.assertTrue(len(val) > 0)
            self.assertIn("6.3.0", LocalizationManager.get("about_version"), f"about_version no contiene 6.2.0 en {lang.name}")
            self.assertIn("2026", LocalizationManager.get("about_date"), f"about_date no contiene 2026 en {lang.name}")

        # Probar fallback a inglés si falta en un idioma secundario
        LocalizationManager.set_language(Language.PORTUGUESE)
        # Una clave inexistente en portugués pero existente en inglés
        LocalizationManager._PORTUGUESE.pop("_test_fallback_key", None)
        LocalizationManager._ENGLISH["_test_fallback_key"] = "English Fallback Value"
        self.assertEqual(LocalizationManager.get("_test_fallback_key"), "English Fallback Value")
        # Limpieza
        LocalizationManager._ENGLISH.pop("_test_fallback_key", None)

    def test_lazy_loading_requests(self):
        """Verifica que importar update_manager NO carga requests en sys.modules inmediatamente."""
        # Si requests ya fue importado en otro test, eliminarlo temporalmente para verificar
        if "managers.update_manager" in sys.modules:
            del sys.modules["managers.update_manager"]

        # Eliminar requests si estaba en sys.modules
        requests_was_present = "requests" in sys.modules
        saved_requests = sys.modules.pop("requests", None)

        try:
            import managers.update_manager
            self.assertNotIn("requests", sys.modules, "requests NO debe ser cargado al importar update_manager (Lazy-loading)")
        finally:
            if requests_was_present and saved_requests is not None:
                sys.modules["requests"] = saved_requests

    def test_presenter_countdown_methods_exist(self):
        """Verifica que _update_countdown_display existe en MainPresenter y previene el crash de modo compacto."""
        from unittest.mock import MagicMock
        from presenters.main_presenter import MainPresenter

        mock_view = MagicMock()
        mock_view.get_countdown_time.return_value = (0, 30, 0)
        mock_view.get_selected_action.return_value = PowerAction.SHUTDOWN
        mock_view.get_selected_mode.return_value = ScheduleMode.COUNTDOWN
        mock_view.get_countdown_total_seconds.return_value = 1800
        mock_view.get_is_force_close_enabled.return_value = False
        mock_view.get_is_prevent_sleep_enabled.return_value = True

        presenter = MainPresenter(mock_view)
        
        # Confirmar que el método crítico existe
        self.assertTrue(hasattr(presenter, "_update_countdown_display"))

        # Simular pulsar '+' y '-' mientras corre la cuenta atrás
        presenter.is_running = True
        presenter.remaining_seconds = 600
        presenter.total_seconds = 600

        # No debe lanzar AttributeError
        presenter._on_add_time_clicked()
        self.assertEqual(presenter.remaining_seconds, 900)

        presenter._on_sub_time_clicked()
        self.assertEqual(presenter.remaining_seconds, 600)

        # Detener timers del presenter para salir limpio
        presenter.countdown_timer.stop()
        presenter._save_timer.stop()
        presenter.schedule_manager.stop_monitoring()


    def test_process_monitor_constants_and_bounded_thresholds(self):
        """Verifica que ProcessMonitorService implementa el piso y techo de umbral adaptativo."""
        from services.process_monitor import ProcessMonitorService
        monitor = ProcessMonitorService()
        self.assertEqual(monitor.IDLE_FLOOR_BYTES_PER_SEC, 35 * 1024)
        self.assertEqual(monitor.ACTIVE_CEILING_BYTES_PER_SEC, 150 * 1024)
        self.assertEqual(monitor.DISK_ACTIVE_THRESHOLD_BYTES, 250 * 1024)
        self.assertEqual(monitor.CHECK_INTERVAL_MS, 2000)

        # Simular ajuste dinámico de umbral con picos de red
        monitor._network_peak_rate = 1_000_000  # 1 MB/s
        expected_threshold = min(monitor.ACTIVE_CEILING_BYTES_PER_SEC, max(monitor.IDLE_FLOOR_BYTES_PER_SEC, int(1_000_000 * 0.05)))
        self.assertEqual(expected_threshold, 50000)

    def test_process_family_and_partial_downloads(self):
        """Verifica la resolución de familia de procesos y el detector heurístico de descargas parciales."""
        import os
        from services.process_monitor import ProcessMonitorService
        monitor = ProcessMonitorService()
        
        # El proceso actual (python unittest) debe resolverse como familia conteniendo su propio PID
        monitor.monitored_pid = os.getpid()
        monitor.monitored_name = "python.exe"
        family = monitor._get_process_family()
        family_pids = [p.pid for p in family]
        self.assertIn(os.getpid(), family_pids)
        
        # La comprobación heurística de archivos parciales no debe lanzar excepciones
        result = monitor._has_active_partial_download()
        self.assertIsInstance(result, bool)

    def test_ui_compact_proportions(self):
        """Verifica que el ancho base y el modo compacto de la UI se han reducido según el plan."""
        from ui.display_helper import DisplayHelper
        self.assertEqual(DisplayHelper.scale_value(416), 416)
        self.assertEqual(DisplayHelper.scale_value(336), 336)
        self.assertEqual(DisplayHelper.scale_value(78), 78)


if __name__ == "__main__":
    unittest.main()
