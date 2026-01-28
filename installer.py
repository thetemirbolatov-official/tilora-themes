import sys
import os
import shutil
import json
import time
import winreg
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        self.setStyleSheet("""
            QSplashScreen {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000000,
                    stop:0.3 #0a0a0a,
                    stop:0.7 #1a1a1a,
                    stop:1 #000000
                );
            }
        """)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # ИСПРАВЛЕНИЕ: Правильная загрузка иконки без размытия
        self.logo_label = QLabel()
        
        # Способ 1: Загрузка напрямую как QIcon
        if os.path.exists("datas/logo.ico"):
            try:
                # Пробуем загрузить как QIcon (лучше для .ico)
                icon = QIcon("datas/logo.ico")
                if not icon.isNull():
                    # Получаем пиксмап нужного размера
                    pixmap = icon.pixmap(200, 200)
                    self.logo_label.setPixmap(pixmap)
                    self.logo_label.setAlignment(Qt.AlignCenter)
                else:
                    # Альтернатива: загрузка напрямую
                    pixmap = QPixmap("datas/logo.ico")
                    if not pixmap.isNull():
                        # Убираем сглаживание для резкости
                        pixmap = pixmap.scaled(200, 200, 
                            Qt.KeepAspectRatio, 
                            Qt.FastTransformation)  # FastTransformation вместо SmoothTransformation
                        self.logo_label.setPixmap(pixmap)
            except:
                # Создаем простую заглушку если иконка не загрузилась
                self.logo_label.setText("TILORA")
                self.logo_label.setStyleSheet("""
                    font-size: 48px;
                    font-weight: bold;
                    color: #3A86FF;
                """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(58, 134, 255, 150))
        shadow.setOffset(0, 0)
        self.logo_label.setGraphicsEffect(shadow)
        
        layout.addWidget(self.logo_label, 0, Qt.AlignCenter)
        
        self.title_label = QLabel("TILORA THEMES")
        self.title_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: #ffffff;
            margin: 30px 0;
            letter-spacing: 4px;
        """)
        
        layout.addWidget(self.title_label, 0, Qt.AlignCenter)
        
        self.loading_label = QLabel("Загрузка установщика...")
        self.loading_label.setStyleSheet("""
            font-size: 14px;
            color: #cccccc;
            margin: 20px;
        """)
        layout.addWidget(self.loading_label, 0, Qt.AlignCenter)
        
        self.splash_progress = QProgressBar()
        self.splash_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3A86FF;
                border-radius: 10px;
                text-align: center;
                height: 20px;
                width: 300px;
                background: #111111;
                margin: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3A86FF,
                    stop:0.5 #764BA2,
                    stop:1 #667EEA
                );
                border-radius: 8px;
            }
        """)
        self.splash_progress.setTextVisible(False)
        layout.addWidget(self.splash_progress, 0, Qt.AlignCenter)
        
        dev_label = QLabel("Разработчик: thetemirbolatov")
        dev_label.setStyleSheet("""
            font-size: 12px;
            color: #666666;
            margin-top: 30px;
        """)
        layout.addWidget(dev_label, 0, Qt.AlignCenter)
        
        self.setFixedSize(600, 500)
        self.center_on_screen()
        
    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.geometry()
        self.move(
            (screen.width() - window_geometry.width()) // 2,
            (screen.height() - window_geometry.height()) // 2
        )
    
    def update_progress(self, value, text):
        self.splash_progress.setValue(value)
        self.loading_label.setText(text)
        QApplication.processEvents()

class DraggableWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() < 50:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

class ThemeInstaller(DraggableWindow):
    def __init__(self):
        super().__init__()
        self.vscode_paths = []
        self.install_in_progress = False
        self.drag_position = QPoint()
        self.initUI()
        self.center_on_screen()
        
    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.geometry()
        self.move(
            (screen.width() - window_geometry.width()) // 2,
            (screen.height() - window_geometry.height()) // 2
        )
    
    def findVSCodeInstallations(self):
        """Находит все установленные версии VS Code на компьютере"""
        installations = []
        
        # Ищем в реестре Windows
        try:
            reg_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for reg_path in reg_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                    for i in range(0, winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                if "Visual Studio Code" in display_name or "VSCode" in display_name:
                                    try:
                                        install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                        if install_location and os.path.exists(install_location):
                                            extensions_path = os.path.join(install_location, "resources", "app", "extensions")
                                            if os.path.exists(extensions_path):
                                                installations.append({
                                                    "name": display_name,
                                                    "path": extensions_path,
                                                    "install_location": install_location
                                                })
                                    except:
                                        pass
                            except:
                                pass
                            finally:
                                winreg.CloseKey(subkey)
                        except:
                            pass
                    winreg.CloseKey(key)
                except:
                    pass
        except:
            pass
        
        # Проверяем стандартные пути установки
        default_paths = [
            os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Microsoft VS Code'),
            os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'Microsoft VS Code'),
            os.path.expanduser('~\\AppData\\Local\\Programs\\Microsoft VS Code'),
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                extensions_path = os.path.join(path, "resources", "app", "extensions")
                if os.path.exists(extensions_path):
                    installations.append({
                        "name": "Microsoft VS Code",
                        "path": extensions_path,
                        "install_location": path
                    })
        
        # Проверяем путь к пользовательским расширениям
        user_extensions = os.path.expanduser('~/.vscode/extensions')
        if os.path.exists(user_extensions):
            installations.append({
                "name": "Пользовательские расширения VS Code",
                "path": user_extensions,
                "install_location": os.path.expanduser('~/.vscode')
            })
        
        return installations
    
    def initUI(self):
        self.setWindowTitle('TILORA THEMES Installer')
        self.setGeometry(300, 300, 750, 600)
        
        if os.path.exists("datas/logo.ico"):
            self.setWindowIcon(QIcon('datas/logo.ico'))
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a,
                    stop:0.5 #111111,
                    stop:1 #0a0a0a
                );
                border-radius: 20px;
                border: 1px solid #333333;
            }
        """)
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Заголовок с кнопкой закрытия
        header_layout = QHBoxLayout()
        
        icon_label = QLabel()
        if os.path.exists("datas/logo.ico"):
            pixmap = QPixmap("datas/logo.ico")
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
        
        header_layout.addWidget(icon_label)
        
        title_label = QLabel('Установщик TILORA THEMES')
        title_label.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #ffffff;
            padding-left: 15px;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #cccccc;
                font-size: 18px;
                border: none;
                padding: 5px 10px;
                border-radius: 10px;
                min-width: 30px;
                min-height: 30px;
            }
            QPushButton:hover {
                background: #ff4444;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("""
            QFrame {
                border: none;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 transparent,
                    stop:0.3 #3A86FF,
                    stop:0.7 #3A86FF,
                    stop:1 transparent
                );
                height: 2px;
                margin: 5px 0 15px 0;
            }
        """)
        layout.addWidget(line)
        
        # Основная область
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #1a1a1a;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #3A86FF;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #2A76EF;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 10, 0)
        scroll_layout.setSpacing(15)
        
        # Область выбора установки
        install_frame = QGroupBox("Выбор места установки")
        install_frame.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #333333;
                border-radius: 10px;
                padding-top: 15px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        install_layout = QVBoxLayout()
        
        # Радио кнопки для выбора типа установки
        self.install_type_group = QButtonGroup()
        
        self.auto_radio = QRadioButton("Автоматическая установка (рекомендуется)")
        self.auto_radio.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
                color: #cccccc;
                padding: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #3A86FF;
            }
            QRadioButton::indicator:checked {
                background-color: #3A86FF;
            }
        """)
        self.auto_radio.setChecked(True)
        self.auto_radio.toggled.connect(self.onInstallTypeChanged)
        
        self.manual_radio = QRadioButton("Ручной выбор пути")
        self.manual_radio.setStyleSheet("""
            QRadioButton {
                font-size: 14px;
                color: #cccccc;
                padding: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #3A86FF;
            }
            QRadioButton::indicator:checked {
                background-color: #3A86FF;
            }
        """)
        self.manual_radio.toggled.connect(self.onInstallTypeChanged)
        
        self.install_type_group.addButton(self.auto_radio)
        self.install_type_group.addButton(self.manual_radio)
        
        install_layout.addWidget(self.auto_radio)
        install_layout.addWidget(self.manual_radio)
        
        # Область для списка найденных VS Code
        self.vscode_list_frame = QFrame()
        self.vscode_list_frame.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 30, 0.6);
                border-radius: 8px;
                border: 1px solid #333333;
                padding: 10px;
            }
        """)
        vscode_list_layout = QVBoxLayout(self.vscode_list_frame)
        
        self.vscode_list = QListWidget()
        self.vscode_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: #88ccff;
                font-size: 12px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:selected {
                background: rgba(58, 134, 255, 0.3);
                border-radius: 5px;
            }
        """)
        self.vscode_list.setSelectionMode(QListWidget.SingleSelection)
        vscode_list_layout.addWidget(self.vscode_list)
        
        install_layout.addWidget(self.vscode_list_frame)
        
        # Область для ручного выбора пути
        self.manual_path_frame = QFrame()
        self.manual_path_frame.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 30, 0.6);
                border-radius: 8px;
                border: 1px solid #333333;
                padding: 10px;
            }
        """)
        manual_path_layout = QVBoxLayout(self.manual_path_frame)
        self.manual_path_frame.setVisible(False)
        
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Укажите путь к папке extensions VS Code...")
        self.path_edit.setStyleSheet("""
            QLineEdit {
                background: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 8px;
                color: #cccccc;
                font-size: 12px;
            }
        """)
        
        browse_btn = QPushButton("Обзор...")
        browse_btn.setStyleSheet("""
            QPushButton {
                background: #3A86FF;
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 12px;
                border-radius: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #2A76EF;
            }
        """)
        browse_btn.clicked.connect(self.browseForPath)
        
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        manual_path_layout.addLayout(path_layout)
        
        install_layout.addWidget(self.manual_path_frame)
        
        install_frame.setLayout(install_layout)
        scroll_layout.addWidget(install_frame)
        
        # Информация о выбранном пути
        self.selected_path_label = QLabel("")
        self.selected_path_label.setStyleSheet("""
            font-size: 12px;
            color: #88ccff;
            padding: 5px;
            background: rgba(30, 30, 30, 0.6);
            border-radius: 5px;
            border: 1px solid #333333;
        """)
        self.selected_path_label.setWordWrap(True)
        scroll_layout.addWidget(self.selected_path_label)
        
        # Статус установки
        self.install_status = QLabel("")
        self.install_status.setAlignment(Qt.AlignCenter)
        self.install_status.setStyleSheet("""
            font-size: 13px;
            padding: 10px;
            min-height: 40px;
            background: rgba(30, 30, 30, 0.6);
            border-radius: 10px;
            border: 1px solid #333333;
        """)
        scroll_layout.addWidget(self.install_status)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3A86FF;
                border-radius: 15px;
                text-align: center;
                height: 25px;
                background: rgba(30, 30, 30, 0.8);
                font-size: 11px;
                color: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3A86FF,
                    stop:0.5 #764BA2,
                    stop:1 #667EEA
                );
                border-radius: 13px;
            }
        """)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        scroll_layout.addWidget(self.progress_bar)
        
        main_scroll.setWidget(scroll_widget)
        layout.addWidget(main_scroll)
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.install_btn = QPushButton(' УСТАНОВИТЬ')
        self.install_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3A86FF,
                    stop:1 #764BA2
                );
                color: white;
                border: none;
                padding: 14px 35px;
                font-size: 15px;
                font-weight: bold;
                border-radius: 10px;
                min-width: 180px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2A76EF,
                    stop:1 #664B92
                );
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1A66DF,
                    stop:1 #564B82
                );
            }
            QPushButton:disabled {
                background: #333333;
                color: #666666;
            }
        """)
        self.install_btn.clicked.connect(self.installTheme)
        self.install_btn.setEnabled(False)
        
        self.cancel_btn = QPushButton(' ВЫХОД')
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: #333333;
                color: #cccccc;
                border: 1px solid #444444;
                padding: 14px 35px;
                font-size: 15px;
                border-radius: 10px;
                min-width: 150px;
            }
            QPushButton:hover {
                background: #444444;
                border: 1px solid #555555;
            }
        """)
        self.cancel_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(self.install_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Футер
        footer_label = QLabel('© 2026 TILORA THEMES • Разработчик: thetemirbolatov')
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("""
            font-size: 11px;
            color: #666666;
            padding-top: 15px;
            margin-top: 15px;
            border-top: 1px solid #333333;
        """)
        layout.addWidget(footer_label)
        
        scroll_layout.addStretch()
    
    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(100, self.scanForVSCode)
    
    def scanForVSCode(self):
        """Сканирует систему на наличие VS Code"""
        self.install_status.setText("🔍 Сканирование системы на наличие VS Code...")
        QApplication.processEvents()
        
        installations = self.findVSCodeInstallations()
        
        if installations:
            for install in installations:
                item_text = f"{install['name']}\nПуть: {install['path']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, install['path'])
                self.vscode_list.addItem(item)
            
            self.vscode_list.setCurrentRow(0)
            self.onVSCodeSelected()
            self.install_btn.setEnabled(True)
            self.install_status.setText(f"✅ Найден VS Code")
        else:
            self.install_status.setText("❌ VS Code не найден. Выберите путь вручную.")
            self.auto_radio.setEnabled(False)
            self.manual_radio.setChecked(True)
            self.onInstallTypeChanged()
    
    def onInstallTypeChanged(self):
        """Обработка изменения типа установки"""
        if self.auto_radio.isChecked():
            self.vscode_list_frame.setVisible(True)
            self.manual_path_frame.setVisible(False)
            self.onVSCodeSelected()
        else:
            self.vscode_list_frame.setVisible(False)
            self.manual_path_frame.setVisible(True)
            self.onManualPathChanged()
    
    def onVSCodeSelected(self):
        """Обработка выбора VS Code из списка"""
        if self.vscode_list.currentItem():
            path = self.vscode_list.currentItem().data(Qt.UserRole)
            self.selected_path_label.setText(f"📍 Выбран путь: {path}")
            self.install_btn.setEnabled(True)
        else:
            self.selected_path_label.setText("⚠️ Выберите VS Code из списка")
            self.install_btn.setEnabled(False)
    
    def onManualPathChanged(self):
        """Обработка изменения ручного пути"""
        path = self.path_edit.text().strip()
        if path and os.path.exists(path):
            self.selected_path_label.setText(f"📍 Выбран путь: {path}")
            self.install_btn.setEnabled(True)
        else:
            self.selected_path_label.setText("⚠️ Укажите существующий путь")
            self.install_btn.setEnabled(False)
    
    def browseForPath(self):
        """Открывает диалог выбора папки"""
        path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку extensions VS Code",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if path:
            self.path_edit.setText(path)
            self.onManualPathChanged()
    
    def getSelectedPath(self):
        """Возвращает выбранный путь установки"""
        if self.auto_radio.isChecked():
            if self.vscode_list.currentItem():
                return self.vscode_list.currentItem().data(Qt.UserRole)
        else:
            path = self.path_edit.text().strip()
            if path and os.path.exists(path):
                return path
        
        return None
    
    def installTheme(self):
        if self.install_in_progress:
            return
            
        install_path = self.getSelectedPath()
        if not install_path:
            self.show_error("Не выбран путь для установки")
            return
        
        # Проверяем, что это действительно папка extensions
        if "extensions" not in install_path.lower():
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                "Выбранный путь не похож на папку extensions VS Code.\n"
                f"Вы уверены, что хотите установить тему в:\n{install_path}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
        
        self.install_in_progress = True
        self.install_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        QTimer.singleShot(100, lambda: self._installThread(install_path))
    
    def _installThread(self, install_path):
        try:
            extension_name = f"thetemirbolatov.tilora-themes-1.0.0"
            source_dir = "datas/TILORA-THEMES"
            
            if not os.path.exists(source_dir):
                self.show_error("Исходные файлы темы не найдены в папке datas/TILORA-THEMES")
                return
            
            self.install_status.setText("📦 Подготовка файлов...")
            self.progress_bar.setValue(10)
            QApplication.processEvents()
            
            with open(os.path.join(source_dir, 'package.json'), 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            self.progress_bar.setValue(20)
            
            target_dir = os.path.join(install_path, extension_name)
            
            self.install_status.setText(f"🔄 Установка в: {install_path}")
            self.progress_bar.setValue(40)
            QApplication.processEvents()
            
            # Удаляем старую версию если существует
            if os.path.exists(target_dir):
                try:
                    shutil.rmtree(target_dir)
                except Exception as e:
                    print(f"Не удалось удалить старую версию: {e}")
            
            # Создаем директорию
            os.makedirs(target_dir, exist_ok=True)
            
            self.progress_bar.setValue(60)
            
            # Копирование всех файлов
            for item in os.listdir(source_dir):
                s = os.path.join(source_dir, item)
                d = os.path.join(target_dir, item)
                
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
            
            self.progress_bar.setValue(80)
            
            # Обновляем package.json
            package_data['name'] = 'tilora-themes'
            package_data['displayName'] = 'TILORA THEMES'
            package_data['publisher'] = 'thetemirbolatov'
            
            with open(os.path.join(target_dir, 'package.json'), 'w', encoding='utf-8') as f:
                json.dump(package_data, f, indent=2, ensure_ascii=False)
            
            self.progress_bar.setValue(90)
            self.install_status.setText("✅ Установка завершена!")
            
            self.progress_bar.setValue(100)
            QApplication.processEvents()
            
            self.show_success(install_path)
            
            QTimer.singleShot(3000, self.close_installer)
            
        except Exception as e:
            self.show_error(f"Ошибка установки: {str(e)}")
            self.install_in_progress = False
            self.install_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
    
    def show_success(self, install_path):
        self.install_status.setText(f"""
            <div style='color: #4CAF50; font-size: 14px; font-weight: bold;'>
            ✅ ТЕМА УСПЕШНО УСТАНОВЛЕНА!
            </div>
            <div style='color: #cccccc; font-size: 12px; margin-top: 5px;'>
            Тема установлена в: {install_path}<br>
            Перезапустите VS Code и выберите тему "TILORA Dark"
            </div>
        """)
        
        self.install_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 14px 35px;
                font-size: 15px;
                font-weight: bold;
                border-radius: 10px;
                min-width: 180px;
            }
        """)
        self.install_btn.setText("✅ УСТАНОВЛЕНО")
    
    def show_error(self, message):
        self.install_status.setText(f"""
            <div style='color: #FF6B6B; font-size: 14px; font-weight: bold;'>
            ❌ ОШИБКА УСТАНОВКИ
            </div>
            <div style='color: #cccccc; font-size: 12px; margin-top: 5px;'>
            {message}
            </div>
        """)
        
        self.install_btn.setStyleSheet("""
            QPushButton {
                background: #FF6B6B;
                color: white;
                border: none;
                padding: 14px 35px;
                font-size: 15px;
                font-weight: bold;
                border-radius: 10px;
                min-width: 180px;
            }
        """)
        self.install_btn.setText("❌ ОШИБКА")
        self.install_in_progress = False
        self.cancel_btn.setEnabled(True)
    
    def close_installer(self):
        for i in range(10, 0, -1):
            self.setWindowOpacity(i / 10.0)
            QApplication.processEvents()
            time.sleep(0.03)
        self.close()

class TILORAInstaller:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')
        
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        self.app.setPalette(dark_palette)
    
    def run(self):
        splash = SplashScreen()
        splash.show()
        
        splash.update_progress(10, "Инициализация...")
        time.sleep(0.3)
        
        splash.update_progress(30, "Загрузка конфигурации...")
        time.sleep(0.3)
        
        splash.update_progress(60, "Подготовка интерфейса...")
        time.sleep(0.3)
        
        splash.update_progress(90, "Запуск установщика...")
        time.sleep(0.2)
        
        splash.update_progress(100, "Готово!")
        time.sleep(0.3)
        
        installer = ThemeInstaller()
        
        splash.finish(installer)
        installer.show()
        
        installer.setWindowOpacity(0)
        for i in range(0, 11):
            installer.setWindowOpacity(i / 10.0)
            QApplication.processEvents()
            time.sleep(0.02)
        
        return self.app.exec_()

def main():
    installer = TILORAInstaller()
    sys.exit(installer.run())

if __name__ == '__main__':
    main()