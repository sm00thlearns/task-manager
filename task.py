import sys
import json
import base64
import requests
from os import path
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QListWidget, QListWidgetItem




class NoteApp(QMainWindow):
    def __init__(self):
        icon_url = "https://media.discordapp.net/attachments/1105422496016125982/1169999814457577522/Icons.png?ex=6557723d&is=6544fd3d&hm=3a4446ad3d1d53dac14cd81808e7463563d7927a2f6e329615edcd72f19ab748&="
        response = requests.get(icon_url)
        with open(path.expandvars(r'%APPDATA%\Icon.png'), "wb") as icon_file:
            icon_file.write(response.content)
        icon = QIcon(path.expandvars(r'%APPDATA%\Icon.png'))

        super().__init__()
        self.setWindowTitle("<erenotes>")
        self.setWindowIcon(icon)
        self.setGeometry(100, 100, 800, 500)
        self.notes_data = {}
        self.initUI()
        self.load_notes_from_json()

    def initUI(self):
        # Ana pencere içeriği
        palette = QPalette()
        # Pencere arkaplan rengini ayarla (daha açık pembe)
        palette.setColor(QPalette.Window, QColor(255, 220, 224))

        # QListWidget arka plan rengini ayarla (daha açık pembe)
        palette.setColor(QPalette.Base, QColor(255, 192, 203))

        # QListWidget öğelerinin metin rengini ayarla (beyaz)
        palette.setColor(QPalette.Text, QColor(255, 255, 255))

        # Buton rengini ayarla (daha koyu pembe)
        palette.setColor(QPalette.Button, QColor(255, 192, 203))

        # Buton metin rengini beyaz yap
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))

        # Pencereye QPalette'i uygula
        self.setPalette(palette)


        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        left_layout = QVBoxLayout()


        note_label = QLabel("Note:")
        self.note_entry = QTextEdit()
        add_button = QPushButton("Send")
        add_button.clicked.connect(self.add_note)
        left_layout.addWidget(note_label)
        left_layout.addWidget(self.note_entry)
        left_layout.addWidget(add_button)

        create_section_label = QLabel("Bölüm Adı:")
        self.section_entry = QLineEdit()
        self.section_entry.setStyleSheet("background-color: pink; color: white")
        create_button = QPushButton("Bölüm Oluştur")
        create_button.clicked.connect(self.create_section)
        left_layout.addWidget(create_section_label)
        left_layout.addWidget(self.section_entry)
        left_layout.addWidget(create_button)

        # Sol tarafta bölümler ve not ekleme bölümü
        section_label = QLabel("Bölümler")
        self.section_list = QListWidget()
        self.section_list.itemSelectionChanged.connect(self.update_notes_list)
        section_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(section_label)
        left_layout.addWidget(self.section_list)
        secdelete_button = QPushButton("Bölümü Sil")
        secdelete_button.clicked.connect(self.delete_section)
        left_layout.addWidget(secdelete_button)


        # Sağ tarafta not okuma ve not listeleme bölümü
        right_layout = QVBoxLayout()
        self.notes_list = QListWidget()
        self.notes_list.itemDoubleClicked.connect(self.view_note)
        right_layout.addWidget(self.notes_list)

        self.note_display = QTextEdit()
        right_layout.addWidget(self.note_display)

        self.note_date = QLineEdit()
        self.note_date.setStyleSheet("background-color: pink; color: white")
        right_layout.addWidget(self.note_date)



        # Temizleme düğmesi
        update_button = QPushButton("Güncelle")
        update_button.clicked.connect(self.update_note)
        right_layout.addWidget(update_button)
        delete_button = QPushButton("Sil")
        delete_button.clicked.connect(self.delete_note)
        right_layout.addWidget(delete_button)
        clear_button = QPushButton("Temizle")
        clear_button.clicked.connect(self.clear_notes)
        right_layout.addWidget(clear_button)

        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 2)

        central_widget.setLayout(layout)

    def add_note(self):
        note_text = self.note_entry.toPlainText()
        selected_section = self.section_list.currentItem().text() if self.section_list.currentItem() else ""
        if selected_section not in self.notes_data:
            self.notes_data[selected_section] = []
        timestamp = datetime.now().strftime('%a %d %b %Y %I:%M:%S %p')
        note_data = {"not": base64.b64encode(note_text.encode()).decode(), "tarih": timestamp}
        self.notes_data[selected_section].append(note_data)
        self.update_sections_list()
        self.note_entry.clear()
        self.save_notes_to_json()


    def create_section(self):
        section_name = self.section_entry.text()
        self.notes_data[section_name] = []
        self.update_sections_list()
        self.section_entry.clear()
        self.save_notes_to_json()

    def update_sections_list(self):
        self.section_list.clear()
        self.section_list.addItems(self.notes_data.keys())
    
    def delete_section(self):
        selected_section = self.section_list.currentItem().text() if self.section_list.currentItem() else ""
        
        if selected_section in self.notes_data:
            del self.notes_data[selected_section]
            self.update_sections_list()  # Bölüm listesini güncelle
            self.notes_list.clear()  # Not listesini temizle
            self.note_display.clear()  # Not görüntülemeyi temizle
            self.note_date.clear()  # Not tarihini temizle
            self.save_notes_to_json()  # JSON dosyasını güncelle

    def update_notes_list(self):
        selected_section = self.section_list.currentItem().text() if self.section_list.currentItem() else ""
        self.notes_list.clear()
        if selected_section in self.notes_data:
            for note in self.notes_data[selected_section]:
                decoded_note = base64.b64decode(note["not"]).decode()
                if len(decoded_note) < 20:
                    truncated_note = decoded_note
                else:
                    truncated_note = decoded_note[:19] + "..."
                list_item = QListWidgetItem(truncated_note)
                list_item.full_note = decoded_note  # Tam notu saklamak için özel bir özellik ekleyin
                self.notes_list.addItem(list_item)

    def delete_note(self):
        selected_section = self.section_list.currentItem().text() if self.section_list.currentItem() else ""
        selected_note_item = self.notes_list.currentItem()
        
        if selected_section and selected_note_item:
            selected_note = selected_note_item.full_note  # Tam notu alın
            if selected_section in self.notes_data:
                for note in self.notes_data[selected_section]:
                    if selected_note == base64.b64decode(note["not"]).decode():
                        self.notes_data[selected_section].remove(note)
                        self.update_notes_list()
                        self.save_notes_to_json()
                        self.note_display.clear()
                        self.note_date.clear()
                        break


    def view_note(self):
        selected_section = self.section_list.currentItem().text() if self.section_list.currentItem() else ""
        selected_item = self.notes_list.currentItem()
        if selected_section and selected_item:
            note_text = selected_item.full_note
            self.note_display.setPlainText(note_text)
            note_data = next((note for note in self.notes_data[selected_section] if note["not"] == base64.b64encode(note_text.encode()).decode()), None)
            if note_data:
                self.note_date.setText(note_data["tarih"])


    def update_note(self):
        selected_section = self.section_list.currentItem().text() if self.section_list.currentItem() else ""
        selected_note = self.notes_list.currentItem().text() if self.notes_list.currentItem() else ""
    
        if selected_section and selected_note:
            new_note_text = self.note_display.toPlainText()
            if selected_section in self.notes_data:
                for note in self.notes_data[selected_section]:
                    if selected_note == base64.b64decode(note["not"]).decode():
                        note["not"] = base64.b64encode(new_note_text.encode()).decode()
                        self.update_notes_list()
                        self.save_notes_to_json()
                        break



    def clear_notes(self):
        self.note_display.clear()

    def save_notes_to_json(self):
        with open("notes.json", "w") as json_file:
            json.dump(self.notes_data, json_file)

    def load_notes_from_json(self):
        try:
            with open("notes.json", "r") as json_file:
                self.notes_data = json.load(json_file)
                self.update_sections_list()
        except FileNotFoundError:
            self.notes_data = {}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = NoteApp()
    ex.show()
    sys.exit(app.exec_())