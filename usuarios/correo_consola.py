"""
Backend de correo para desarrollo: igual al de consola de Django, pero
imprime el mensaje como texto legible (sin codificación quoted-printable),
para que el enlace de "recuperar contraseña" se pueda copiar directo.
No envía nada fuera del computador.
"""
from django.core.mail.backends.console import EmailBackend as ConsolaDjango


class EmailBackend(ConsolaDjango):
    def write_message(self, message):
        separador = '-' * 79
        self.stream.write(
            f"\n{separador}\n"
            f"CORREO (solo consola, no se envió)\n"
            f"De:      {message.from_email}\n"
            f"Para:    {', '.join(message.to)}\n"
            f"Asunto:  {message.subject}\n"
            f"{separador}\n"
            f"{message.body}\n"
            f"{separador}\n"
        )
