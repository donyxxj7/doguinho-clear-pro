import logging
import os
from datetime import datetime

class LoggerConfig:
    def __init__(self):
        self.success_logger = self._setup_logger('success_logger', 'sucesso_log.txt')
        self.error_logger = self._setup_logger('error_logger', 'erro_log.txt')

    def _setup_logger(self, name, log_file):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Verifica se o logger já tem handlers para evitar duplicação
        if not logger.handlers:
            handler = logging.FileHandler(log_file, encoding='utf-8')
            handler.setLevel(logging.INFO)
            logger.addHandler(handler)
        
        return logger

    def _format_message(self, operation, path, message):
        timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        return f"[{timestamp}] {operation} - {path} - {message}"

    def log_success(self, operation, path, message):
        """Registra uma operação bem-sucedida"""
        formatted_message = self._format_message(operation, path, message)
        self.success_logger.info(f"✅ Sucesso: {formatted_message}")

    def log_error(self, operation, path, error):
        """Registra um erro na operação"""
        formatted_message = self._format_message(operation, path, error)
        self.error_logger.error(f"❌ Erro: {formatted_message}")

    def log_warning(self, operation, path, message):
        """Registra um aviso na operação"""
        formatted_message = self._format_message(operation, path, message)
        self.error_logger.warning(f"⚠️ Aviso: {formatted_message}")

    def get_logs(self, log_type='both'):
        """Retorna os logs do tipo especificado"""
        logs = []
        
        if log_type in ['success', 'both']:
            try:
                if os.path.exists('sucesso_log.txt'):
                    with open('sucesso_log.txt', 'r', encoding='utf-8') as f:
                        logs.extend(f.readlines())
            except Exception as e:
                self.log_error('LEITURA_LOG', 'sucesso_log.txt', f'Erro ao ler logs de sucesso: {str(e)}')

        if log_type in ['error', 'both']:
            try:
                if os.path.exists('erro_log.txt'):
                    with open('erro_log.txt', 'r', encoding='utf-8') as f:
                        logs.extend(f.readlines())
            except Exception as e:
                self.log_error('LEITURA_LOG', 'erro_log.txt', f'Erro ao ler logs de erro: {str(e)}')

        return logs

# Instância global do logger
logger = LoggerConfig()
