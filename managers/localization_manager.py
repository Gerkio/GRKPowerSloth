"""
Gestor de internacionalización (i18n).
Equivalente a LocalizationManager.cs
"""

import json
from pathlib import Path
from typing import Dict
from models.enums import Language


class LocalizationManager:
    """
    Gestor estático para el manejo de traducciones.
    Soporta inglés y español.
    """
    
    # Diccionarios de traducciones
    _ENGLISH: Dict[str, str] = {
        "main_title": "GRK PowerSloth - Shutdown Scheduler",
        "trigger_condition_label": "Trigger condition:",
        "mode_countdown": "Countdown Timer",
        "mode_specific_time": "At a Specific Time",
        "mode_monitor_activity": "Monitor Activity",
        "hours": "Hours",
        "minutes": "Minutes",
        "seconds": "Seconds",
        "action": "Action",
        "start": "Start",
        "stop": "Stop",
        "status_default": "Waiting for configuration...",
        "status_countdown": "Action '{0}' in: {1}",
        "status_stopped": "Timer stopped by user.",
        "status_will_run_at": "Will run at approx. {0}",
        "menu_file": "&File",
        "menu_start": "&Start Timer",
        "menu_stop": "&Stop Timer",
        "menu_exit": "&Exit",
        "menu_settings": "&Settings",
        "menu_start_with_windows": "Start with Windows",
        "menu_always_on_top": "Always on Top",
        "menu_theme": "&Theme",
        "menu_light": "&Light",
        "menu_dark": "&Dark",
        "menu_language": "&Language",
        "menu_english": "&English",
        "menu_spanish": "&Spanish",
        "menu_help": "&Help",
        "menu_about": "&About...",
        "action_shutdown": "Shutdown",
        "action_restart": "Restart",
        "action_sleep": "Sleep",
        "action_restart_uefi": "Restart to BIOS/UEFI",
        "action_hibernate": "Hibernate",
        "about_title": "About GRK PowerSloth",
        "about_version": "Version 6.0 (Python)",
        "about_dev": "Developed by: Gerkio",
        "about_tech": "Technology: Python & PyQt6",
        "about_date": "December 5, 2025",
        "warning_title": "Final Warning",
        "warning_text": "The action '{0}' will be executed in {1} seconds.\nSave your work!",
        "warning_cancel": "Cancel Action",
        "force_close_apps": "Force close",
        "prevent_sleep_screen_off": "Keep awake",
        "tooltip_mode_countdown": "Schedule the action after a specific amount of time passes.",
        "tooltip_mode_specific_time": "Schedule the action to run at a specific time of day.",
        "tooltip_action": "Select the action to perform: Shutdown, Restart, or Sleep.",
        "tooltip_force_close": "Forcibly closes any applications that are unresponsive.\nWarning: This may cause data loss in unsaved work.",
        "tooltip_prevent_sleep": "Prevents the system and display from going to sleep while the timer is active.",
        "tray_show": "Show",
        "tray_exit": "Exit",
        "status_minimized": "GRK PowerSloth is running in the background.",
        "process": "Process",
        "filter_label": "Filter processes:",
        "process_label": "Process to monitor:",
        "process_filter_label": "Filter processes...",
        "monitoring_condition": "Trigger condition:",
        "condition_on_exit": "When process closes",
        "condition_on_idle": "When network activity stops",
        "refresh": "Refresh",
        "status_monitoring": "Monitoring '{0}' ...",
        "error_process_not_found": "The selected process no longer exists. Please refresh the list.",
        "error_admin_required_for_monitor": "Administrator rights are required to monitor this process's network activity.",
        "tooltip_process": "Select the application that is rendering, exporting or downloading.",
        "tooltip_condition_exit": "Ideal for tasks like rendering or exporting. The action will be triggered as soon as the application closes.",
        "tooltip_condition_idle": "Ideal for downloads. The action will be triggered when the network usage of the application is almost zero for a while.\nNOTE: This will detect both a finished download and a lost connection.",
        "tooltip_refresh": "Refresh the list of running processes.",
        "notification_timer_started": "Timer Started",
        "notification_timer_started_body": "GRK PowerSloth has started the countdown.",
        "notification_minute_warning": "Action in 1 Minute",
        "notification_minute_warning_body": "The scheduled action will execute in 60 seconds."
    }
    
    _SPANISH: Dict[str, str] = {
        "main_title": "GRK PowerSloth - Programador de Apagado",
        "trigger_condition_label": "Modo de disparo:",
        "mode_countdown": "Cuenta Regresiva",
        "mode_specific_time": "Hora Fija",
        "mode_monitor_activity": "Monitor de Actividad",
        "hours": "Horas",
        "minutes": "Minutos",
        "seconds": "Segundos",
        "action": "Acción",
        "start": "Iniciar",
        "stop": "Detener",
        "status_default": "Esperando configuración...",
        "status_countdown": "Acción '{0}' en: {1}",
        "status_stopped": "Temporizador detenido por el usuario.",
        "status_will_run_at": "Se ejecutará aprox. a las {0}",
        "menu_file": "&Archivo",
        "menu_start": "&Iniciar Temporizador",
        "menu_stop": "&Detener Temporizador",
        "menu_exit": "&Salir",
        "menu_settings": "&Configuración",
        "menu_start_with_windows": "Iniciar con el Sistema",
        "menu_always_on_top": "Siempre Visible",
        "menu_theme": "&Tema",
        "menu_light": "&Claro",
        "menu_dark": "&Oscuro",
        "menu_language": "&Idioma",
        "menu_english": "&Inglés",
        "menu_spanish": "&Español",
        "menu_help": "&Ayuda",
        "menu_about": "&Acerca de...",
        "action_shutdown": "Apagar",
        "action_restart": "Reiniciar",
        "action_sleep": "Suspender",
        "action_restart_uefi": "Reiniciar en BIOS/UEFI",
        "action_hibernate": "Hibernar",
        "about_title": "Acerca de GRK PowerSloth",
        "about_version": "Versión 6.0 (Python)",
        "about_dev": "Desarrollado por: Gerkio",
        "about_tech": "Tecnología: Python & PyQt6",
        "about_date": "5 de diciembre de 2025",
        "warning_title": "Advertencia Final",
        "warning_text": "La acción '{0}' se ejecutará en {1} segundos.\n¡Guarde su trabajo!",
        "warning_cancel": "Cancelar Acción",
        "force_close_apps": "Forzar cierre",
        "prevent_sleep_screen_off": "Mantener despierto",
        "tooltip_mode_countdown": "Programa la acción para que se ejecute después de un tiempo determinado.",
        "tooltip_mode_specific_time": "Programa la acción para que se ejecute a una hora específica del día.",
        "tooltip_action": "Selecciona la acción a realizar: Apagar, Reiniciar o Suspender.",
        "tooltip_force_close": "Fuerza el cierre de aplicaciones que no respondan.\nAviso: Puede causar pérdida de datos en trabajos no guardados.",
        "tooltip_prevent_sleep": "Evita que el sistema y la pantalla entren en modo de suspensión mientras el temporizador está activo.",
        "tray_show": "Mostrar",
        "tray_exit": "Salir",
        "status_minimized": "GRK PowerSloth se está ejecutando en segundo plano.",
        "process": "Proceso",
        "filter_label": "Filtrar procesos:",
        "process_label": "Proceso a monitorear:",
        "process_filter_label": "Filtrar procesos...",
        "monitoring_condition": "Disparar:",
        "condition_on_exit": "Al cerrar app",
        "condition_on_idle": "Al finalizar red",
        "refresh": "Refrescar",
        "status_monitoring": "Monitorizando '{0}' ...",
        "error_process_not_found": "El proceso seleccionado ya no existe. Por favor, refresca la lista.",
        "error_admin_required_for_monitor": "Se requieren derechos de administrador para monitorizar la actividad de red de este proceso.",
        "tooltip_process": "Selecciona el programa que está renderizando, exportando o descargando.",
        "tooltip_condition_exit": "Ideal para tareas como renderizados o exportaciones. La acción se ejecutará en cuanto el programa finalice y se cierre.",
        "tooltip_condition_idle": "Ideal para descargas. La acción se ejecutará cuando el uso de red del programa sea casi nulo durante un tiempo.\nNOTA: Esto detectará tanto una descarga finalizada como una conexión perdida.",
        "tooltip_refresh": "Refrescar la lista de procesos en ejecución.",
        "notification_timer_started": "Temporizador Iniciado",
        "notification_timer_started_body": "GRK PowerSloth ha iniciado la cuenta regresiva.",
        "notification_minute_warning": "Acción en 1 Minuto",
        "notification_minute_warning_body": "La acción programada se ejecutará en 60 segundos."
    }

    _PORTUGUESE: Dict[str, str] = {
        "main_title": "GRK PowerSloth - Agendador de Desligamento",
        "trigger_condition_label": "Modo de disparo:",
        "mode_countdown": "Contagem Regressiva",
        "mode_specific_time": "Hora Fixa",
        "mode_monitor_activity": "Monitor de Atividade",
        "hours": "Horas",
        "minutes": "Minutos",
        "seconds": "Segundos",
        "action": "Ação",
        "start": "Iniciar",
        "stop": "Parar",
        "status_default": "Aguardando configuração...",
        "status_countdown": "Ação '{0}' em: {1}",
        "status_stopped": "Cronômetro parado pelo usuário.",
        "status_will_run_at": "Executará aprox. às {0}",
        "menu_file": "&Arquivo",
        "menu_start": "&Iniciar Cronômetro",
        "menu_stop": "&Parar Cronômetro",
        "menu_exit": "&Sair",
        "menu_settings": "&Configurações",
        "menu_start_with_windows": "Iniciar com o Windows",
        "menu_always_on_top": "Sempre no Topo",
        "menu_theme": "&Tema",
        "menu_light": "&Claro",
        "menu_dark": "&Escuro",
        "menu_language": "&Idioma",
        "menu_english": "&Inglês",
        "menu_spanish": "&Espanhol",
        "menu_help": "&Ajuda",
        "menu_about": "&Sobre...",
        "action_shutdown": "Desligar",
        "action_restart": "Reiniciar",
        "action_sleep": "Suspender",
        "action_restart_uefi": "Reiniciar na BIOS/UEFI",
        "action_hibernate": "Hibernar",
        "about_title": "Sobre o GRK PowerSloth",
        "about_version": "Versão 6.0 (Python)",
        "about_dev": "Desenvolvido por: Gerkio",
        "about_tech": "Tecnologia: Python & PyQt6",
        "about_date": "5 de Dezembro de 2025",
        "warning_title": "Aviso Final",
        "warning_text": "A ação '{0}' será executada em {1} segundos.\nSalve seu trabalho!",
        "warning_cancel": "Cancelar Ação",
        "force_close_apps": "Forçar fechamento",
        "prevent_sleep_screen_off": "Não dormir",
        "tooltip_mode_countdown": "Agenda a ação para ser executada após um determinado tempo.",
        "tooltip_mode_specific_time": "Agenda a ação para ser executada em um horário específico do dia.",
        "tooltip_action": "Selecione a ação a ser realizada: Desligar, Reiniciar ou Suspender.",
        "tooltip_force_close": "Força o fechamento de aplicativos que não respondem.\nAviso: Isso pode causar perda de dados em trabalhos não salvos.",
        "tooltip_prevent_sleep": "Impede que o sistema e a tela entrem em modo de suspensão enquanto o cronômetro estiver ativo.",
        "tray_show": "Mostrar",
        "tray_exit": "Sair",
        "status_minimized": "GRK PowerSloth está rodando em segundo plano.",
        "process": "Processo",
        "filter_label": "Filtrar processos:",
        "process_label": "Processo para monitorar:",
        "process_filter_label": "Filtrar processos...",
        "monitoring_condition": "Disparar:",
        "condition_on_exit": "Ao fechar app",
        "condition_on_idle": "Ao finalizar rede",
        "refresh": "Atualizar",
        "status_monitoring": "Monitorando '{0}' ...",
        "error_process_not_found": "O processo selecionado não existe mais. Por favor, atualize a lista.",
        "error_admin_required_for_monitor": "Direitos de administrador são necessários para monitorar a atividade de rede deste processo.",
        "tooltip_process": "Selecione o aplicativo que está renderizando, exportando ou baixando.",
        "tooltip_condition_exit": "Ideal para tarefas como renderizações ou exportações. A ação será disparada assim que o aplicativo fechar.",
        "tooltip_condition_idle": "Ideal para downloads. A ação será disparada quando o uso de rede do aplicativo for quase zero por um tempo.\nNOTA: Isso detectará tanto um download finalizado quanto uma conexão perdida.",
        "tooltip_refresh": "Atualiza a lista de processos em execução.",
        "notification_timer_started": "Cronômetro Iniciado",
        "notification_timer_started_body": "GRK PowerSloth iniciou a contagem regressiva.",
        "notification_minute_warning": "Ação em 1 Minuto",
        "notification_minute_warning_body": "A ação agendada será executada em 60 segundos."
    }

    _FRENCH: Dict[str, str] = {
        "main_title": "GRK PowerSloth - Planificateur d'Arrêt",
        "trigger_condition_label": "Mode de déclenchement:",
        "mode_countdown": "Compte à rebours",
        "mode_specific_time": "Heure Fixe",
        "mode_monitor_activity": "Moniteur d'Activité",
        "hours": "Heures",
        "minutes": "Minutes",
        "seconds": "Secondes",
        "action": "Action",
        "start": "Démarrer",
        "stop": "Arrêter",
        "status_default": "En attente de configuration...",
        "status_countdown": "Action '{0}' dans: {1}",
        "status_stopped": "Minuterie arrêtée par l'utilisateur.",
        "status_will_run_at": "S'exécutera env. à {0}",
        "menu_file": "&Fichier",
        "menu_start": "&Démarrer Minuterie",
        "menu_stop": "&Arrêter Minuterie",
        "menu_exit": "&Quitter",
        "menu_settings": "&Paramètres",
        "menu_start_with_windows": "Démarrer avec Windows",
        "menu_always_on_top": "Toujours au Top",
        "menu_theme": "&Thème",
        "menu_light": "&Clair",
        "menu_dark": "&Sombre",
        "menu_language": "&Langue",
        "menu_english": "&Anglais",
        "menu_spanish": "&Espagnol",
        "menu_help": "&Aide",
        "menu_about": "&À propos...",
        "action_shutdown": "Éteindre",
        "action_restart": "Redémarrer",
        "action_sleep": "Veille",
        "action_restart_uefi": "Redémarrer en BIOS/UEFI",
        "action_hibernate": "Hiberner",
        "about_title": "À propos de GRK PowerSloth",
        "about_version": "Version 6.0 (Python)",
        "about_dev": "Développé par: Gerkio",
        "about_tech": "Technologie: Python & PyQt6",
        "about_date": "5 décembre 2025",
        "warning_title": "Dernier Avertissement",
        "warning_text": "L'action '{0}' sera exécutée dans {1} secondes.\nSauvegardez votre travail!",
        "warning_cancel": "Annuler Action",
        "force_close_apps": "Forcer fermeture",
        "prevent_sleep_screen_off": "Rester éveillé",
        "tooltip_mode_countdown": "Planifie l'action après un certain temps.",
        "tooltip_mode_specific_time": "Planifie l'action à une heure précise de la journée.",
        "tooltip_action": "Sélectionnez l'action à effectuer: Éteindre, Redémarrer ou Veille.",
        "tooltip_force_close": "Ferme de force les applications ne répondant pas.\nAvertissement: Cela peut causer une perte de données pour les travaux non sauvegardés.",
        "tooltip_prevent_sleep": "Empêche le système et l'écran de se mettre en veille pendant que la minuterie est active.",
        "tray_show": "Montrer",
        "tray_exit": "Quitter",
        "status_minimized": "GRK PowerSloth s'exécute en arrière-plan.",
        "process": "Processus",
        "filter_label": "Filtrer processus:",
        "process_label": "Processus à surveiller:",
        "process_filter_label": "Filtrer processus...",
        "monitoring_condition": "Déclencheur:",
        "condition_on_exit": "À la fermeture",
        "condition_on_idle": "Fin réseau",
        "refresh": "Actualiser",
        "status_monitoring": "Surveillance de '{0}' ...",
        "error_process_not_found": "Le processus sélectionné n'existe plus. Veuillez actualiser la liste.",
        "error_admin_required_for_monitor": "Les droits d'administrateur sont requis pour surveiller l'activité réseau de ce processus.",
        "tooltip_process": "Sélectionnez l'application qui effectue le rendu, l'exportation ou le téléchargement.",
        "tooltip_condition_exit": "Idéal pour les rendus ou exportations. L'action sera déclenchée dès que l'application se fermera.",
        "tooltip_condition_idle": "Idéal pour les téléchargements. L'action sera déclenchée lorsque l'utilisation réseau sera presque nulle pendant un certain temps.\nNOTE: Cela détectera aussi bien un téléchargement terminé qu'une connexion perdue.",
        "tooltip_refresh": "Actualiser la liste des processus en cours d'exécution.",
        "notification_timer_started": "Minuterie Démarrée",
        "notification_timer_started_body": "GRK PowerSloth a commencé le compte à rebours.",
        "notification_minute_warning": "Action dans 1 Minute",
        "notification_minute_warning_body": "L'action planifiée s'exécutera dans 60 secondes."
    }
    
    # Estado actual
    _current_language: Language = Language.SPANISH
    _current_dict: Dict[str, str] = _SPANISH
    
    @classmethod
    def set_language(cls, language: Language) -> None:
        """
        Establece el idioma actual.
        
        Args:
            language: Idioma a establecer
        """
        cls._current_language = language
        if language == Language.SPANISH:
            cls._current_dict = cls._SPANISH
        elif language == Language.PORTUGUESE:
            cls._current_dict = cls._PORTUGUESE
        elif language == Language.FRENCH:
            cls._current_dict = cls._FRENCH
        else:
            cls._current_dict = cls._ENGLISH
    
    @classmethod
    def get(cls, key: str) -> str:
        """
        Obtiene la traducción de una clave.
        
        Args:
            key: Clave de la traducción
            
        Returns:
            String traducido, o la clave si no se encuentra
        """
        return cls._current_dict.get(key, key)
    
    @classmethod
    def get_current_language(cls) -> Language:
        """Obtiene el idioma actual"""
        return cls._current_language
