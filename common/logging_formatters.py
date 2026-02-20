import json
import logging
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    Formatador de logs em JSON para facilitar a agregação em ferramentas de monitoramento.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "logger": record.name,
        }
        
        # Inclui informações de exceção se existirem
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        # Inclui dados extras passados via 'extra'
        if hasattr(record, 'extra'):
            log_record.update(record.extra)
            
        return json.dumps(log_record)
