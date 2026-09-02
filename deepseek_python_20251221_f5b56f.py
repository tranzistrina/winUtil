import sys
import math
from PyQt5.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QSlider,QSpinBox,QCheckBox,QComboBox,QFileDialog,QMessageBox,QTextEdit
from PyQt5.QtGui import QPixmap,QImage
from PyQt5.QtCore import Qt
from PIL import Image
import numpy as np

class ImageToBinaryConverter(QMainWindow):
    def __init__(self):
        super().__init__(); self.image_path=None; self.original_image=None; self.binary_image=None; self.initUI()
    def initUI(self):
        self.setWindowTitle('Image to Binary Converter with Square Output'); self.resize(1000,760)
        w=QWidget(); self.setCentralWidget(w); layout=QVBoxLayout(w)
        buttons=QHBoxLayout(); self.load_btn=QPushButton('Загрузить изображение'); self.convert_btn=QPushButton('Преобразовать в 0/1'); self.save_btn=QPushButton('Сохранить результат')
        self.convert_btn.setEnabled(False); self.save_btn.setEnabled(False)
        self.load_btn.clicked.connect(self.load_image); self.convert_btn.clicked.connect(self.convert_to_binary); self.save_btn.clicked.connect(self.save_result)
        for b in (self.load_btn,self.convert_btn,self.save_btn): buttons.addWidget(b)
        layout.addLayout(buttons)
        preview=QHBoxLayout(); self.original_label=QLabel('Оригинальное изображение'); self.binary_label=QLabel('Бинарное изображение');
        for lab in (self.original_label,self.binary_label): lab.setAlignment(Qt.AlignCenter); lab.setMinimumSize(400,300); preview.addWidget(lab)
        layout.addLayout(preview)
        settings=QHBoxLayout(); settings.addWidget(QLabel('Порог:')); self.threshold=QSlider(Qt.Horizontal); self.threshold.setRange(0,255); self.threshold.setValue(128); settings.addWidget(self.threshold); self.threshold_value=QLabel('128'); settings.addWidget(self.threshold_value); self.threshold.valueChanged.connect(lambda v:self.threshold_value.setText(str(v)))
        self.invert=QCheckBox('Инвертировать'); settings.addWidget(self.invert); settings.addWidget(QLabel('Ширина:')); self.width_box=QSpinBox(); self.width_box.setRange(1,500); self.width_box.setValue(100); settings.addWidget(self.width_box); settings.addWidget(QLabel('Высота:')); self.height_box=QSpinBox(); self.height_box.setRange(1,500); self.height_box.setValue(100); settings.addWidget(self.height_box); self.method=QComboBox(); self.method.addItems(['Ближайший сосед','Билинейная','Бикубическая','Lanczos']); settings.addWidget(self.method)
        layout.addLayout(settings); self.output=QTextEdit(); self.output.setReadOnly(True); layout.addWidget(self.output)
    def load_image(self):
        path,_=QFileDialog.getOpenFileName(self,'Выберите изображение','','Images (*.png *.jpg *.jpeg *.bmp *.webp)')
        if not path:return
        self.image_path=path; self.original_image=Image.open(path).convert('L'); self.show_pil(self.original_image,self.original_label); self.convert_btn.setEnabled(True)
    def show_pil(self,img,label):
        data=img.convert('RGB'); arr=np.asarray(data); h,w=arr.shape[:2]; q=QImage(arr.data,w,h,3*w,QImage.Format_RGB888); label.setPixmap(QPixmap.fromImage(q.copy()).scaled(label.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation))
    def convert_to_binary(self):
        if self.original_image is None:return
        method_map={'Ближайший сосед':Image.Resampling.NEAREST,'Билинейная':Image.Resampling.BILINEAR,'Бикубическая':Image.Resampling.BICUBIC,'Lanczos':Image.Resampling.LANCZOS}
        img=self.original_image.resize((self.width_box.value(),self.height_box.value()),method_map[self.method.currentText()]); a=np.array(img); b=(a>=self.threshold.value())
        if self.invert.isChecked():b=~b
        self.binary_image=b.astype(np.uint8); vis=Image.fromarray((self.binary_image*255).astype('uint8')); self.show_pil(vis,self.binary_label); self.output.setPlainText('\n'.join(''.join('1' if x else '0' for x in row) for row in self.binary_image)); self.save_btn.setEnabled(True)
    def save_result(self):
        if self.binary_image is None:return
        path,_=QFileDialog.getSaveFileName(self,'Сохранить результат','','Text (*.txt);;Binary (*.bin);;PNG (*.png)')
        if not path:return
        if path.lower().endswith('.bin'):
            bits=''.join('1' if x else '0' for row in self.binary_image for x in row); pad=(8-len(bits)%8)%8; bits+='0'*pad; data=bytes(int(bits[i:i+8],2) for i in range(0,len(bits),8)); open(path,'wb').write(data)
        elif path.lower().endswith('.png'): Image.fromarray((self.binary_image*255).astype('uint8')).save(path)
        else: open(path,'w',encoding='utf-8').write(self.output.toPlainText())
        QMessageBox.information(self,'Готово',f'Сохранено: {path}')

if __name__=='__main__':
    app=QApplication(sys.argv); win=ImageToBinaryConverter(); win.show(); sys.exit(app.exec_())
