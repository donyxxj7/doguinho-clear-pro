def analisar_espaco_disco(self):
    """Analisa o espaço em disco e mostra detalhes"""
    try:
        dialog = QDialog(self)
        dialog.setWindowTitle("Análise de Disco")
        dialog.setModal(True)
        dialog.setFixedSize(800, 600)  # Set fixed size
        layout = QVBoxLayout(dialog)
        
        # Informações gerais
        info_label = QLabel(
            f"Espaço Total: {self.stats['disk_info']['total']}GB\n"
            f"Espaço Usado: {self.stats['disk_info']['used']}GB\n"
            f"Espaço Livre: {self.stats['disk_info']['free']}GB\n"
            f"Uso: {self.stats['disk_usage']}%"
        )
        info_label.setStyleSheet("font-size: 12px; margin: 10px;")
        layout.addWidget(info_label)
        
        # Create text area for results
        results = QPlainTextEdit(dialog)
        results.setReadOnly(True)
        results.setMinimumHeight(400)
        results.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333333;
                padding: 5px;
                font-family: Consolas, monospace;
            }
        """)
        results.hide()  # Initially hidden
        layout.addWidget(results)
        
        # Botão para análise detalhada
        btn_analise = QPushButton("Analisar Diretórios")
        btn_analise.setStyleSheet(self.get_button_style())
        btn_analise.clicked.connect(lambda: self.analisar_diretorios(dialog, results))
        layout.addWidget(btn_analise)
        
        dialog.exec_()
        
    except Exception as e:
        logger.log_error("DISCO", "Análise", f"Erro ao analisar disco: {str(e)}")
        QMessageBox.warning(self, "Erro", "Não foi possível analisar o disco.")

def analisar_diretorios(self, parent_dialog, results_widget):
    """Analisa o tamanho dos diretórios"""
    try:
        logger.log_success("DISCO", "Análise", "Iniciando análise de diretórios")
        
        # Show and clear the results widget
        results_widget.show()
        results_widget.clear()
        results_widget.setPlainText("🔍 Iniciando análise dos diretórios...\n")
        QApplication.processEvents()

        # Rest of the analysis code remains the same...
        # [Previous implementation of directory analysis]

    except Exception as e:
        logger.log_error("DISCO", "Análise", f"Erro ao analisar diretórios: {str(e)}")
        if results_widget:
            results_widget.setPlainText(f"Erro ao analisar diretórios: {str(e)}")
        logger.log_error("DISCO", "Análise", f"Erro detalhado: {str(e)}")
