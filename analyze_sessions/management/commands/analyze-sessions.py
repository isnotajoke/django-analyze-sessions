# Hook AnalyzeSessionsCommand up to django-admin
# See https://docs.djangoproject.com/en/1.3/howto/custom-management-commands/

from analyze_sessions.commands import AnalyzeSessionsCommand as Command
