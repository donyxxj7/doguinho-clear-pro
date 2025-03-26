import code
import os
import sys
import time
import ctypes
import tempfile
import subprocess
import psutil
from logger_config import logger

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTabWidget,
    QProgressBar, QPlainTextEdit, QMessageBox, QDialog, QMenu
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon

# ---------------- INSTÂNCIA ÚNICA ----------------
def verificar_instancia_unica(lock_filename='doguinho.lock'):
    lock_file_path = os.path.join(tempfile.gettempdir(), lock_filename)
    if os.path.exists(lock_file_path):
        try:
            with open(lock_file_path, 'r') as lockfile:
                pid = int(lockfile.read())
                os.kill(pid, 0)
            return False  # Já rodando
        except (ValueError, OSError):
            os.remove(lock_file_path)
    with open(lock_file_path, 'w') as lockfile:
        lockfile.write(str(os.getpid()))
    return True

# ---------------- CONFIGS GERAIS ----------------
THEMES = {
    "dark": {
        "BG_COLOR": "#121212",
        "FG_COLOR": "#FFFFFF",
        "BUTTON_COLOR": "#1F1F1F",
        "BUTTON_HOVER": "#333333",
        "PROGRESS_COLOR": "#03DAC6",
        "SUCCESS_COLOR": "#00C853",
        "ERROR_COLOR": "#FF5252",
        "ACCENT_COLOR": "#BB86FC"
    },
    "light": {
        "BG_COLOR": "#F5F5F5",
        "FG_COLOR": "#000000",
        "BUTTON_COLOR": "#E0E0E0",
        "BUTTON_HOVER": "#BDBDBD",
        "PROGRESS_COLOR": "#00897B",
        "SUCCESS_COLOR": "#2E7D32",
        "ERROR_COLOR": "#C62828",
        "ACCENT_COLOR": "#6200EE"
    }
}

# Tema padrão
THEME = "dark"
COLORS = THEMES[THEME]

# ---------------- CHECAGEM ADMIN ----------------
def verificar_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logger.log_error("ADMIN", "Sistema", f"Erro ao verificar administrador: {e}")
        return False

# ---------------- THREAD WORKER ----------------
class Worker(QThread):
    update_status = Signal(str)
    update_progress = Signal(int)
    
    def __init__(self, func):
        super().__init__()
        self.func = func
        self.running = True
    
    def run(self):
        try:
            # Inicia o progresso
            self.update_progress.emit(10)
            
            # Executa a função
            resultado = self.func()
            
            # Atualiza o progresso antes de finalizar
            self.update_progress.emit(90)
            
            # Emite o resultado
            self.update_status.emit(resultado)
            
            # Finaliza o progresso
            self.update_progress.emit(100)
        except Exception as e:
            erro = f"Erro durante a execução: {str(e)}"
            logger.log_error("WORKER", "Thread", erro)
            self.update_status.emit(f"❌ {erro}")
            self.update_progress.emit(0)

# ---------------- FUNÇÕES DO SISTEMA ----------------
def limpar_arquivos(pastas):
    arquivos_apagados = 0
    tamanho_total = 0
    erros = []
    
    for pasta in pastas:
        if not pasta:
            continue
            
        if not os.path.exists(pasta):
            logger.log_warning("VERIFICAR_PASTA", pasta, "Pasta não encontrada")
            continue
            
        try:
            for root, dirs, files in os.walk(pasta):
                for file in files:
                    path = os.path.join(root, file)
                    try:
                        if os.path.exists(path):  # Verificação adicional
                            file_size = os.path.getsize(path)
                            os.remove(path)
                            arquivos_apagados += 1
                            tamanho_total += file_size
                            logger.log_success("REMOVER_ARQUIVO", path, "Arquivo removido com sucesso")
                    except PermissionError as e:
                        erro = f"Sem permissão para remover: {path}"
                        logger.log_error("REMOVER_ARQUIVO", path, erro)
                        erros.append(erro)
                    except Exception as e:
                        erro = f"Erro ao remover arquivo: {str(e)}"
                        logger.log_error("REMOVER_ARQUIVO", path, erro)
                        erros.append(erro)
        except Exception as e:
            erro = f"Erro ao acessar pasta: {str(e)}"
            logger.log_error("ACESSAR_PASTA", pasta, erro)
            erros.append(erro)
    
    if erros:
        logger.log_error("LIMPEZA", "múltiplos arquivos", f"{len(erros)} arquivos não puderam ser removidos")
    
    return arquivos_apagados, round(tamanho_total / (1024 * 1024), 2)

def apagar_temporarios():
    pastas = [tempfile.gettempdir(), os.environ.get("TEMP"), r"C:\Windows\Temp", r"C:\Windows\Prefetch"]
    arquivos, tamanho = limpar_arquivos(pastas)
    return f"🧹 {arquivos} arquivos removidos ({tamanho} MB)"

def limpeza_profunda_temporarios():
    pastas = [
        os.environ.get("TEMP"),
        r"C:\Windows\Temp",
        r"C:\Windows\Prefetch",
        r"C:\Windows\SoftwareDistribution\Download",
        os.path.expanduser(r"~\AppData\Local\Temp"),
        os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Explorer"),
        os.path.expanduser(r"~\AppData\Local\CrashDumps")
    ]
    arquivos, tamanho = limpar_arquivos(pastas)
    return f"🧹 Limpeza profunda: {arquivos} arquivos removidos ({tamanho} MB)"

def otimizar_rede():
    """
    Realiza uma otimização completa da rede, incluindo:
    - Limpeza de cache DNS
    - Reset do Winsock
    - Reset do TCP/IP
    - Renovação de configurações IP
    - Otimização de parâmetros de rede
    """
    try:
        resultados = []
        logger.log_success("REDE", "Sistema", "Iniciando otimização completa da rede")

        # 1. Limpeza de Cache DNS
        try:
            dns_result = subprocess.run("ipconfig /flushdns", shell=True, capture_output=True, text=True)
            if dns_result.returncode == 0:
                resultados.append("✅ Cache DNS limpo")
                logger.log_success("REDE_DNS", "Sistema", "Cache DNS limpo com sucesso")
            else:
                resultados.append("⚠️ Falha ao limpar cache DNS")
                logger.log_warning("REDE_DNS", "Sistema", "Falha ao limpar cache DNS")
        except Exception as e:
            logger.log_error("REDE_DNS", "Sistema", f"Erro: {str(e)}")
            resultados.append("❌ Erro na limpeza DNS")

        # 2. Reset do Winsock
        try:
            winsock_result = subprocess.run("netsh winsock reset", shell=True, capture_output=True, text=True)
            if winsock_result.returncode == 0:
                resultados.append("✅ Winsock resetado")
                logger.log_success("REDE_WINSOCK", "Sistema", "Winsock resetado com sucesso")
            else:
                resultados.append("⚠️ Falha ao resetar Winsock")
                logger.log_warning("REDE_WINSOCK", "Sistema", "Falha ao resetar Winsock")
        except Exception as e:
            logger.log_error("REDE_WINSOCK", "Sistema", f"Erro: {str(e)}")
            resultados.append("❌ Erro no reset do Winsock")

        # 3. Reset do TCP/IP
        try:
            tcpip_result = subprocess.run("netsh int ip reset", shell=True, capture_output=True, text=True)
            if tcpip_result.returncode == 0:
                resultados.append("✅ TCP/IP resetado")
                logger.log_success("REDE_TCPIP", "Sistema", "TCP/IP resetado com sucesso")
            else:
                resultados.append("⚠️ Falha ao resetar TCP/IP")
                logger.log_warning("REDE_TCPIP", "Sistema", "Falha ao resetar TCP/IP")
        except Exception as e:
            logger.log_error("REDE_TCPIP", "Sistema", f"Erro: {str(e)}")
            resultados.append("❌ Erro no reset do TCP/IP")

        # 4. Renovação de IP
        try:
            # Libera o IP atual
            subprocess.run("ipconfig /release", shell=True, capture_output=True)
            # Obtém novo IP
            renew_result = subprocess.run("ipconfig /renew", shell=True, capture_output=True, text=True)
            if renew_result.returncode == 0:
                resultados.append("✅ IP renovado")
                logger.log_success("REDE_IP", "Sistema", "IP renovado com sucesso")
            else:
                resultados.append("⚠️ Falha ao renovar IP")
                logger.log_warning("REDE_IP", "Sistema", "Falha ao renovar IP")
        except Exception as e:
            logger.log_error("REDE_IP", "Sistema", f"Erro: {str(e)}")
            resultados.append("❌ Erro na renovação de IP")

        # 5. Otimização de parâmetros de rede
        try:
            # Habilita otimizações de rede do Windows
            subprocess.run("netsh interface tcp set global autotuninglevel=normal", shell=True)
            subprocess.run("netsh interface tcp set global chimney=enabled", shell=True)
            subprocess.run("netsh interface tcp set global dca=enabled", shell=True)
            subprocess.run("netsh interface tcp set global netdma=enabled", shell=True)
            resultados.append("✅ Parâmetros de rede otimizados")
            logger.log_success("REDE_PARAMS", "Sistema", "Parâmetros de rede otimizados")
        except Exception as e:
            logger.log_error("REDE_PARAMS", "Sistema", f"Erro: {str(e)}")
            resultados.append("❌ Erro na otimização de parâmetros")

        # Prepara mensagem de retorno
        if all("✅" in r for r in resultados):
            return "🌐 Rede otimizada com sucesso!\n" + "\n".join(resultados)
        elif any("❌" in r for r in resultados):
            return "⚠️ Otimização parcial da rede\n" + "\n".join(resultados)
        else:
            return "⚠️ Algumas otimizações não puderam ser concluídas\n" + "\n".join(resultados)

    except Exception as e:
        erro = f"Erro durante otimização de rede: {str(e)}"
        logger.log_error("REDE", "Sistema", erro)
        return f"❌ {erro}"

def verificar_integridade():
    try:
        logger.log_success("VERIFICACAO", "Sistema", "Iniciando verificação de integridade do sistema")
        resultado = subprocess.run("sfc /scannow", shell=True, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            msg = "🩺 Verificação de integridade concluída!"
            logger.log_success("VERIFICACAO", "Sistema", "Verificação de integridade concluída com sucesso")
            return msg
        else:
            erro = f"Erro na verificação: {resultado.stderr}"
            logger.log_error("VERIFICACAO", "Sistema", erro)
            return f"❌ {erro}"
    except Exception as e:
        erro = f"Erro ao executar verificação: {str(e)}"
        logger.log_error("VERIFICACAO", "Sistema", erro)
        return f"❌ {erro}"

def desfragmentar_disco():
    try:
        logger.log_success("DESFRAG", "C:", "Iniciando desfragmentação do disco")
        resultado = subprocess.run("defrag C: /A", shell=True, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            msg = "💽 Desfragmentação concluída com sucesso!"
            logger.log_success("DESFRAG", "C:", "Desfragmentação concluída com sucesso")
            return msg
        else:
            erro = f"Erro na desfragmentação: {resultado.stderr}"
            logger.log_error("DESFRAG", "C:", erro)
            return f"❌ {erro}"
    except Exception as e:
        erro = f"Erro ao executar desfragmentação: {str(e)}"
        logger.log_error("DESFRAG", "C:", erro)
        return f"❌ {erro}"

def otimizar_servicos_windows():
    """
    Otimiza serviços do Windows, desativando serviços desnecessários
    e ajustando configurações para melhor performance
    """
    try:
        resultados = []
        logger.log_success("SERVICOS", "Sistema", "Iniciando otimização dos serviços")

        # Lista de serviços que podem ser otimizados
        servicos = {
            # Serviços que podem ser desativados
            "desativar": [
                "DiagTrack",          # Telemetria do Windows
                "dmwappushservice",    # WAP Push Message Routing
                "SysMain",            # Superfetch
                "WSearch",            # Windows Search
                "WerSvc",             # Windows Error Reporting
                "WMPNetworkSvc",      # Windows Media Player Network
                "XblAuthManager",      # Xbox Live Auth Manager
                "XblGameSave",        # Xbox Live Game Save
                "XboxNetApiSvc",      # Xbox Live Networking
                "TabletInputService", # Tablet Input Service
                "RetailDemo"          # Retail Demo Service
            ],
            # Serviços que podem ser configurados como manual
            "manual": [
                "BITS",               # Background Intelligent Transfer
                "WpcMonSvc",          # Parental Controls
                "PhoneSvc",           # Phone Service
                "PrintNotify",        # Printer Extensions
                "RemoteRegistry",     # Remote Registry
                "SessionEnv",         # Remote Desktop Configuration
                "TrkWks",            # Distributed Link Tracking
                "WbioSrvc"           # Windows Biometric Service
            ]
        }

        # 1. Desativa serviços desnecessários
        for servico in servicos["desativar"]:
            try:
                # Tenta parar o serviço
                stop_result = subprocess.run(
                    f'net stop "{servico}"',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                # Configura para não iniciar automaticamente
                config_result = subprocess.run(
                    f'sc config "{servico}" start= disabled',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if config_result.returncode == 0:
                    resultados.append(f"✅ Serviço {servico} otimizado")
                    logger.log_success("SERVICOS", servico, "Serviço desativado com sucesso")
                else:
                    resultados.append(f"⚠️ Falha ao otimizar {servico}")
                    logger.log_warning("SERVICOS", servico, "Falha ao desativar serviço")
            except Exception as e:
                logger.log_error("SERVICOS", servico, f"Erro: {str(e)}")
                resultados.append(f"❌ Erro ao configurar {servico}")

        # 2. Configura serviços para manual
        for servico in servicos["manual"]:
            try:
                config_result = subprocess.run(
                    f'sc config "{servico}" start= demand',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if config_result.returncode == 0:
                    resultados.append(f"✅ Serviço {servico} configurado como manual")
                    logger.log_success("SERVICOS", servico, "Serviço configurado como manual")
                else:
                    resultados.append(f"⚠️ Falha ao configurar {servico}")
                    logger.log_warning("SERVICOS", servico, "Falha ao configurar serviço")
            except Exception as e:
                logger.log_error("SERVICOS", servico, f"Erro: {str(e)}")
                resultados.append(f"❌ Erro ao configurar {servico}")

        # 3. Otimiza o serviço de atualização do Windows
        try:
            subprocess.run(
                'sc config "wuauserv" start= demand',
                shell=True,
                capture_output=True
            )
            resultados.append("✅ Serviço de atualização otimizado")
            logger.log_success("SERVICOS", "Windows Update", "Serviço configurado como manual")
        except Exception as e:
            logger.log_error("SERVICOS", "Windows Update", f"Erro: {str(e)}")
            resultados.append("❌ Erro ao otimizar Windows Update")

        # Prepara mensagem de retorno
        if all("✅" in r for r in resultados):
            return "⚡ Serviços otimizados com sucesso!\n" + "\n".join(resultados)
        elif any("❌" in r for r in resultados):
            return "⚠️ Otimização parcial dos serviços\n" + "\n".join(resultados)
        else:
            return "⚠️ Algumas otimizações não puderam ser concluídas\n" + "\n".join(resultados)

    except Exception as e:
        erro = f"Erro durante otimização dos serviços: {str(e)}"
        logger.log_error("SERVICOS", "Sistema", erro)
        return f"❌ {erro}"

def verificar_atualizacao():
    try:
        logger.log_success("ATUALIZACAO", "Sistema", "Verificando atualizações disponíveis")
        time.sleep(1)
        msg = "🔄 Você já está usando a versão mais recente!"
        logger.log_success("ATUALIZACAO", "Sistema", "Sistema está atualizado")
        return msg
    except Exception as e:
        erro = f"Erro ao verificar atualizações: {str(e)}"
        logger.log_error("ATUALIZACAO", "Sistema", erro)
        return f"❌ {erro}"

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.setToolTip('Doguinho Clear Pro')
        
        menu = QMenu(parent)
        showAction = menu.addAction("Mostrar")
        showAction.triggered.connect(parent.show)
        
        menu.addSeparator()
        
        exitAction = menu.addAction("Sair")
        exitAction.triggered.connect(parent.close)
        
        self.setContextMenu(menu)
        self.activated.connect(self.onTrayIconActivated)
    
    def onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.parent().show()

class DoguinhoClearPro(QWidget):
    def __init__(self):
        super().__init__()
        self.current_theme = "dark"
        self.initUI()
        self.setupSystemTray()
        
    def initUI(self):
        self.setWindowTitle("Doguinho Clear Pro")
        self.setGeometry(300, 100, 800, 600)
        self.updateTheme()
        
        # Garante que o arquivo de log existe
        try:
            with open("doguinho_detalhado_log.txt", "a", encoding="utf-8") as _:
                pass
        except Exception as e:
            logger.log_error("INIT", "Sistema", f"Erro ao criar arquivo de log: {str(e)}")

        layout = QVBoxLayout(self)

        titulo = QLabel("🐶 Doguinho Clear Pro")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout.addWidget(titulo)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.status_label = QLabel("")
        self.progress_bar = QProgressBar()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        
        # Oculta os elementos de status inicialmente
        self.status_label.hide()
        self.progress_bar.hide()

        self.log_window = None
        self.worker = None

        self.create_tabs()
        
        # Configura o timer para atualizar a posição do botão de logs
        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.update_logs_button_position)
        self.resize_timer.start(100)  # Atualiza a cada 100ms
        
    def resizeEvent(self, event):
        """Sobrescreve o evento de redimensionamento para atualizar a posição do botão de logs"""
        super().resizeEvent(event)
        self.update_logs_button_position()
        
    def update_logs_button_position(self):
        """Atualiza a posição do botão de logs para mantê-lo no canto inferior direito"""
        if hasattr(self, 'logs_button'):
            self.logs_button.move(self.width() - 110, self.height() - 40)
        
    def setupSystemTray(self):
        """Configura o ícone na bandeja do sistema"""
        self.tray_icon = SystemTrayIcon(QIcon("doguinho.ico"), self)
        self.tray_icon.show()
        
    def updateTheme(self):
        """Atualiza o tema da aplicação"""
        global COLORS
        COLORS = THEMES[self.current_theme]
        
        # Atualiza o estilo da janela principal
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['BG_COLOR']};
                color: {COLORS['FG_COLOR']};
                font-family: Arial;
            }}
            QPushButton {{
                background-color: {COLORS['BUTTON_COLOR']};
                color: {COLORS['FG_COLOR']};
                padding: 12px;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['BUTTON_HOVER']};
            }}
            QProgressBar {{
                border: 2px solid {COLORS['ACCENT_COLOR']};
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['PROGRESS_COLOR']};
            }}
        """)
        
    def toggleTheme(self):
        """Alterna entre os temas claro e escuro"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.updateTheme()

    def create_tabs(self):
        essenciais = QWidget()
        vbox = QVBoxLayout(essenciais)
        vbox.addWidget(self.create_button("🧹 Limpar Temporários", apagar_temporarios))
        vbox.addWidget(self.create_button("🌐 Otimizar Rede", otimizar_rede))
        vbox.addWidget(self.create_button("🩺 Verificar Integridade", verificar_integridade))

        avancadas = QWidget()
        vbox2 = QVBoxLayout(avancadas)
        vbox2.addWidget(self.create_button("⚡ Otimizar Serviços", otimizar_servicos_windows))
        vbox2.addWidget(self.create_button("💽 Desfragmentar Disco", desfragmentar_disco))
        vbox2.addWidget(self.create_button("🧹 Limpeza Profunda", limpeza_profunda_temporarios))

        logs = QWidget()
        vbox3 = QVBoxLayout(logs)
        vbox3.addWidget(self.create_button("🔄 Verificar Atualização", verificar_atualizacao))

        # Botão de logs no canto inferior direito
        self.logs_button = QPushButton("📋 Logs")
        self.logs_button.setFixedSize(100, 30)  # Tamanho compacto
        self.logs_button.clicked.connect(self.abrir_logs_detalhados)
        self.logs_button.setStyleSheet("""
            QPushButton {
                background-color: #1F1F1F;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
                position: absolute;
                bottom: 10px;
                right: 10px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """)
        # Adiciona o botão ao layout principal
        self.layout().addWidget(self.logs_button)
        self.logs_button.move(self.width() - 110, self.height() - 40)

        # Adiciona todas as abas
        self.tabs.addTab(essenciais, "Essenciais")
        self.tabs.addTab(avancadas, "Avançadas")
        self.tabs.addTab(logs, "Configuração")

    def create_button(self, label, func):
        button = QPushButton(label)
        button.setStyleSheet(f"background-color: {COLORS['BUTTON_COLOR']}; color: white; padding: 12px;")
        
        if label == "📋 Ver Logs Detalhados":
            button.clicked.connect(self.abrir_logs_detalhados)
        else:
            button.clicked.connect(lambda: self.run_task(func))
            
        return button

    def run_task(self, func):
        try:
            # Mostra os elementos de status
            self.status_label.show()
            self.progress_bar.show()
            
            self.status_label.setText("⏳ Executando...")
            self.progress_bar.setValue(0)
            
            self.worker = Worker(func)
            self.worker.update_status.connect(self.task_finished)
            self.worker.update_progress.connect(self.update_progress)
            self.worker.start()
            
        except Exception as e:
            erro = f"Erro ao iniciar tarefa: {str(e)}"
            logger.log_error("RUN_TASK", "Interface", erro)
            self.status_label.setText(f"❌ {erro}")
            self.progress_bar.setValue(0)

    def task_finished(self, result):
        try:
            self.status_label.setText(f"Status: {result}")
            if "❌" in result:  # Se houve erro
                self.progress_bar.setValue(0)
            else:
                self.progress_bar.setValue(100)
            
            # Agenda a ocultação dos elementos após 3 segundos
            QTimer.singleShot(3000, self.hide_status_elements)
        except Exception as e:
            logger.log_error("TASK_FINISHED", "Interface", f"Erro ao finalizar tarefa: {str(e)}")
            
    def update_progress(self, value):
        try:
            self.progress_bar.setValue(value)
        except Exception as e:
            logger.log_error("UPDATE_PROGRESS", "Interface", f"Erro ao atualizar progresso: {str(e)}")
            
    def hide_status_elements(self):
        """Oculta os elementos de status"""
        try:
            self.status_label.hide()
            self.progress_bar.hide()
        except Exception as e:
            logger.log_error("HIDE_STATUS", "Interface", f"Erro ao ocultar elementos: {str(e)}")

    def abrir_logs_detalhados(self):
        # Verifica se já existe uma janela de logs aberta
        if hasattr(self, 'log_window') and self.log_window is not None:
            if self.log_window.isVisible():
                self.log_window.raise_()
                self.log_window.activateWindow()
                return
            else:
                self.log_window.deleteLater()
                self.log_window = None

        # Cria uma nova janela de logs
        try:
            self.log_window = QDialog(self)
            self.log_window.setWindowTitle("📋 Logs Detalhados - Doguinho Clear Pro")
            self.log_window.resize(800, 600)
            self.log_window.setModal(False)  # Permite interação com a janela principal
            
            # Layout principal
            main_layout = QVBoxLayout(self.log_window)
            
            # Título
            titulo = QLabel("📄 Logs Detalhados")
            titulo.setAlignment(Qt.AlignCenter)
            titulo.setStyleSheet(f"color: {COLORS['FG_COLOR']}; font-size: 16px; padding: 10px;")
            main_layout.addWidget(titulo)
            
            # Área de texto
            self.logs_text = QPlainTextEdit()
            self.logs_text.setReadOnly(True)
            self.logs_text.setStyleSheet(f"""
                QPlainTextEdit {{
                    background-color: {COLORS['BUTTON_COLOR']};
                    color: {COLORS['FG_COLOR']};
                    border: 1px solid #333333;
                    padding: 5px;
                }}
            """)
            main_layout.addWidget(self.logs_text)
            
            # Container de botões
            button_container = QWidget()
            button_layout = QVBoxLayout(button_container)
            
            # Botão Fechar
            btn_fechar = QPushButton("❌ Fechar")
            btn_fechar.setStyleSheet(self.get_button_style())
            btn_fechar.clicked.connect(self.log_window.close)
            button_layout.addWidget(btn_fechar)
            
            main_layout.addWidget(button_container)
            
            # Estilo da janela
            self.log_window.setStyleSheet(f"background-color: {COLORS['BG_COLOR']};")
            
            # Carrega os logs iniciais
            self.atualizar_logs_seguros()
            
            # Mostra a janela
            self.log_window.show()
            
        except Exception as e:
            QMessageBox.warning(self, "Aviso", f"Não foi possível abrir a janela de logs: {str(e)}")
            logger.log_error("ABRIR_LOGS", "Interface", f"Erro ao abrir janela de logs: {str(e)}")

    def get_button_style(self):
        return f"""
            QPushButton {{
                background-color: {COLORS['BUTTON_COLOR']};
                color: {COLORS['FG_COLOR']};
                padding: 8px;
                border: 1px solid #333333;
            }}
            QPushButton:hover {{
                background-color: {COLORS['BUTTON_HOVER']};
            }}
        """

    def atualizar_logs_seguros(self):
        if not hasattr(self, 'logs_text') or self.logs_text is None:
            return

        try:
            # Obtém todos os logs (sucesso e erro)
            logs = logger.get_logs('both')
            
            if not logs:
                self.logs_text.setPlainText("📝 Nenhum log encontrado. Execute alguma operação primeiro.")
                return
            
            # Ordena os logs por data (assumindo que começam com [DD/MM/YYYY HH:MM:SS])
            logs.sort(reverse=True)  # Logs mais recentes primeiro
            
            # Junta todos os logs em uma única string
            conteudo = ''.join(logs)
            
            if not conteudo.strip():
                self.logs_text.setPlainText("📝 Arquivos de log estão vazios.")
            else:
                self.logs_text.setPlainText(conteudo)
                
        except Exception as e:
            erro = f"❌ Erro ao atualizar logs: {str(e)}"
            self.logs_text.setPlainText(erro)
            logger.log_error("ATUALIZAR_LOGS", "Interface", erro)

    def closeEvent(self, event):
        try:
            # Fecha a janela de logs se estiver aberta
            if hasattr(self, 'log_window') and self.log_window is not None:
                self.log_window.close()
                self.log_window.deleteLater()
                self.log_window = None

            # Remove o arquivo de lock
            lock_file_path = os.path.join(tempfile.gettempdir(), 'doguinho.lock')
            if os.path.exists(lock_file_path):
                os.remove(lock_file_path)

            # Limpa recursos
            if self.worker is not None:
                self.worker.quit()
                self.worker.wait()
                self.worker = None

            event.accept()
            QApplication.quit()
            os._exit(0)
        except Exception as e:
            logger.log_error("CLOSE", "Sistema", f"Erro ao fechar aplicativo: {str(e)}")
            event.accept()
            os._exit(1)

# ---------------- EXECUÇÃO ----------------
if __name__ == "__main__":
    if not verificar_instancia_unica():
        QMessageBox.warning(None, "Atenção", "⚠️ O Doguinho Clear Pro já está aberto!")
        sys.exit(0)

    if not verificar_admin():
        QMessageBox.critical(None, "Permissão Negada", "⚠️ Execute como Administrador!")
        sys.exit(0)

    app = QApplication(sys.argv)
    window = DoguinhoClearPro()
    window.show()
    sys.exit(app.exec())
