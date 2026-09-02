import os
import subprocess
import tempfile
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtCore import QThread, pyqtSignal

class ConverterThread(QThread):
    """Поток для конвертации, чтобы не блокировать интерфейс."""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, docx_path):
        super().__init__()
        self.docx_path = docx_path

    def run(self):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                subprocess.run(
                    [
                        "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
                        "--headless",
                        "--convert-to", "pdf",
                        "--outdir", tmpdir,
                        self.docx_path
                    ],
                    check=True,
                    capture_output=True,
                    text=True
                )
                base = os.path.splitext(os.path.basename(self.docx_path))[0]
                pdf_path = os.path.join(tmpdir, base + ".pdf")
                if not os.path.exists(pdf_path):
                    raise RuntimeError("PDF не был создан.")
                dest_dir = os.path.dirname(self.docx_path)
                dest_pdf = os.path.join(dest_dir, base + ".pdf")
                import shutil
                shutil.copy2(pdf_path, dest_pdf)
                self.finished.emit(dest_pdf)
        except subprocess.CalledProcessError as e:
            self.error.emit(f"Ошибка конвертации: {e.stderr}")
        except FileNotFoundError:
            self.error.emit("LibreOffice не найден. Установите его или проверьте PATH.")
        except Exception as e:
            self.error.emit(str(e))

class DocxToPdfConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Конвертер DOCX в PDF")
        self.setGeometry(100, 100, 400, 200)
        layout = QVBoxLayout()
        self.label = QLabel("Выберите файл .docx для конвертации")
        layout.addWidget(self.label)
        self.selectBtn = QPushButton("Выбрать файл")
        self.selectBtn.clicked.connect(self.select_file)
        layout.addWidget(self.selectBtn)
        self.convertBtn = QPushButton("Конвертировать")
        self.convertBtn.clicked.connect(self.convert)
        self.convertBtn.setEnabled(False)
        layout.addWidget(self.convertBtn)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        self.setLayout(layout)
        self.selected_file = None

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите DOCX файл", "", "DOCX files (*.docx)")
        if file_path:
            self.selected_file = file_path
            self.label.setText(f"Выбран: {os.path.basename(file_path)}")
            self.convertBtn.setEnabled(True)

    def convert(self):
        if not self.selected_file:
            return
        self.convertBtn.setEnabled(False)
        self.selectBtn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.thread = ConverterThread(self.selected_file)
        self.thread.finished.connect(self.on_conversion_success)
        self.thread.error.connect(self.on_conversion_error)
        self.thread.start()

    def on_conversion_success(self, pdf_path):
        self.progress.setVisible(False)
        self.convertBtn.setEnabled(True)
        self.selectBtn.setEnabled(True)
        reply = QMessageBox.information(
            self, "Успех", f"PDF создан:\n{pdf_path}\n\nОткрыть папку с файлом?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if sys.platform == "win32":
                os.startfile(os.path.dirname(pdf_path))
            elif sys.platform == "darwin":
                subprocess.run(["open", os.path.dirname(pdf_path)])
            else:
                subprocess.run(["xdg-open", os.path.dirname(pdf_path)])

    def on_conversion_error(self, error_msg):
        self.progress.setVisible(False)
        self.convertBtn.setEnabled(True)
        self.selectBtn.setEnabled(True)
        QMessageBox.critical(self, "Ошибка", error_msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DocxToPdfConverter()
    window.show()
    sys.exit(app.exec_())
