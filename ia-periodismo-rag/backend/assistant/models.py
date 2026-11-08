from django.db import models
import uuid

class ConversationLog(models.Model):
    """
    Registro histórico de interacciones para trazabilidad,
    auditoría ética y evaluación del modelo según la rúbrica.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=120, db_index=True)
    user_query = models.TextField()
    bot_response = models.TextField()
    sources_cited = models.JSONField(default=list, blank=True)
    is_out_of_domain = models.BooleanField(default=False)
    has_evidence = models.BooleanField(default=True)
    feedback_score = models.IntegerField(default=0, help_text="1: Positivo, -1: Negativo, 0: Sin calificar")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Registro de Conversación"
        verbose_name_plural = "Registros de Conversaciones"

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.user_query[:50]}"
