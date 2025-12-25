import sys
import psutil
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QProgressBar, QFrame, QFileDialog
)
from PyQt6.QtGui import QFont, QAction, QColor
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

# ================= 🎨 THEME & STYLING (J.A.R.V.I.S LOOK) =================
STYLE_SHEET = """
QMainWindow { background-color: #050505; }
QWidget { color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }

/* CHAT BOX */
QTextEdit {
    background-color: #0f0f12; border: 1px solid #333;
    border-radius: 10px; padding: 10px; font-size: 13px; color: #00ffcc;
}

/* INPUT FIELD */
QLineEdit {
    background-color: #1a1a20; border: 1px solid #00ffcc;
    border-radius: 20px; padding: 10px; font-size: 13px; color: white;
}

/* BUTTONS */
QPushButton { font-weight: bold; border-radius: 15px; padding: 8px; }
QPushButton#SendBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00ffcc, stop:1 #0099ff);
    color: black; border: none;
}
QPushButton#SendBtn:hover { background: #00ffff; }

QPushButton#AttachBtn { background-color: #222; border: 1px solid #555; color: white; }
QPushButton#AttachBtn:hover { border-color: #00ffcc; color: #00ffcc; }

QPushButton#LiveBtn {
    background-color: transparent; border: 2px solid #ff3333; color: #ff3333;
    border-radius: 10px; padding: 10px; font-size: 12px;
}
QPushButton#LiveBtn:hover { background-color: #ff3333; color: white; }

/* SYSTEM MONITOR */
QProgressBar {
    border: 1px solid #333; border-radius: 5px; text-align: center; color: white;
}
QProgressBar::chunk { background-color: #00ffcc; }

/* MENUBAR */
QMenuBar { background-color: #111; color: white; }
QMenuBar::item:selected { background-color: #00ffcc; color: black; }
"""

# ================= 🧵 WORKER THREAD (NO FREEZING) =================
class ChatThread(QThread):
    finished_signal = pyqtSignal(dict)
    def __init__(self, url, data, files):
        super().__init__()
        self.url = url
        self.data = data
        self.files = files

    def run(self):
        try:
            # 120s Timeout taaki 502 error na aaye
            response = requests.post(self.url, data=self.data, files=self.files, timeout=120)
            if response.status_code == 200:
                self.finished_signal.emit({"status": "success", "reply": response.json().get("response", "No Reply")})
            else:
                self.finished_signal.emit({"status": "error", "reply": f"Server Error: {response.status_code}"})
        except Exception as e:
            self.finished_signal.emit({"status": "error", "reply": f"Connection Error: {str(e)}"})

# ================= 🖥️ MAIN INTERFACE =================
class AlyaUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # 👇 APNA MAIN SERVER URL YAHAN DALO
        self.render_url = "https://alya-1-7lll.onrender.com/chat" 
        
        self.selected_file = None
        self.initUI()
        self.startSystemMonitor()

    def initUI(self):
        self.setWindowTitle('A.L.Y.A - Neural Interface')
        self.setMinimumSize(1100, 750)
        self.setStyleSheet(STYLE_SHEET)

        # 1. MENU BAR (Prompts Folder)
        menubar = self.menuBar()
        prompt_menu = menubar.addMenu("📁 Prompts")
        
        sys_prompt_action = QAction("⚙️ System Personality", self)
        sys_prompt_action.triggered.connect(lambda: self.chat_box.append("<i>[SYSTEM: Personality settings coming soon...]</i>"))
        prompt_menu.addAction(sys_prompt_action)

        # 2. MAIN LAYOUT GRID
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.grid = QGridLayout()
        central_widget.setLayout(self.grid)
        self.grid.setContentsMargins(15, 15, 15, 15)
        self.grid.setSpacing(20)

        # ================= LEFT PANEL (Vision & System) =================
        left_panel = QFrame()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # [Top Left] Live Vision Button
        self.btn_live = QPushButton("🔴 LIVE VISION")
        self.btn_live.setObjectName("LiveBtn")
        self.btn_live.setCursor(Qt.CursorShape.PointingHandCursor)
        left_layout.addWidget(self.btn_live)

        left_layout.addStretch() # Gap

        # [Bottom Left] System Monitor
        lbl_sys = QLabel("SYSTEM VITALS")
        lbl_sys.setStyleSheet("color: #666; font-size: 10px; font-weight: bold; letter-spacing: 2px;")
        
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setFixedHeight(8)
        
        self.ram_label = QLabel("RAM: 0%")
        self.ram_bar = QProgressBar()
        self.ram_bar.setFixedHeight(8)

        left_layout.addWidget(lbl_sys)
        left_layout.addWidget(self.cpu_label)
        left_layout.addWidget(self.cpu_bar)
        left_layout.addSpacing(10)
        left_layout.addWidget(self.ram_label)
        left_layout.addWidget(self.ram_bar)

        # ================= CENTER PANEL (The Voice Globe) =================
        center_panel = QFrame()
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # The Orb (Stylized Label)
        self.orb = QLabel()
        self.orb.setFixedSize(220, 220)
        self.orb.setStyleSheet("""
            background: qradialgradient(cx:0.5, cy:0.5, radius: 0.5, fx:0.5, fy:0.5, 
                        stop:0 #222, stop:0.6 #111, stop:1 #00ffcc);
            border: 2px solid #00ffcc;
            border-radius: 110px;
        """)
        
        orb_label = QLabel("VOICE MODULE: STANDBY")
        orb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        orb_label.setStyleSheet("color: #00ffcc; font-size: 10px; margin-top: 15px; letter-spacing: 2px;")

        center_layout.addWidget(self.orb)
        center_layout.addWidget(orb_label)
        center_panel.setLayout(center_layout)

        # ================= RIGHT PANEL (Chat) =================
        right_panel = QFrame()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        # Chat History
        self.chat_box = QTextEdit()
        self.chat_box.setReadOnly(True)
        self.chat_box.setPlaceholderText("A.L.Y.A. Connected. Waiting for input...")
        
        # File Status
        self.file_lbl = QLabel("")
        self.file_lbl.setStyleSheet("color: #ff3333; font-size: 11px;")

        # Input Area
        input_layout = QHBoxLayout()
        
        self.btn_attach = QPushButton("📎")
        self.btn_attach.setObjectName("AttachBtn")
        self.btn_attach.setFixedWidth(40)
        self.btn_attach.clicked.connect(self.select_file)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.returnPressed.connect(self.send_msg)

        self.btn_send = QPushButton("SEND")
        self.btn_send.setObjectName("SendBtn")
        self.btn_send.setFixedWidth(80)
        self.btn_send.clicked.connect(self.send_msg)

        input_layout.addWidget(self.btn_attach)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.btn_send)

        right_layout.addWidget(self.chat_box)
        right_layout.addWidget(self.file_lbl)
        right_layout.addLayout(input_layout)

        # ================= ADD TO GRID =================
        # (Widget, Row, Col, RowSpan, ColSpan)
        self.grid.addWidget(left_panel, 0, 0, 1, 1)    # Col 1: System/Live
        self.grid.addWidget(center_panel, 0, 1, 1, 1)  # Col 2: Orb
        self.grid.addWidget(right_panel, 0, 2, 1, 2)   # Col 3-4: Chat (Wider)

        # Column Ratio
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 2)
        self.grid.setColumnStretch(2, 4)

    # --- SYSTEM MONITOR ---
    def startSystemMonitor(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateStats)
        self.timer.start(1000)

    def updateStats(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        self.cpu_label.setText(f"CPU: {cpu}%")
        self.cpu_bar.setValue(int(cpu))
        self.ram_label.setText(f"RAM: {ram}%")
        self.ram_bar.setValue(int(ram))

    # --- CHAT LOGIC ---
    def select_file(self):
        f, _ = QFileDialog.getOpenFileName(self, 'Attach File', '', "Images (*.png *.jpg *.jpeg)")
        if f:
            self.selected_file = f
            self.file_lbl.setText(f"📎 {f.split('/')[-1]} selected")

    def send_msg(self):
        msg = self.input_field.text().strip()
        if not msg and not self.selected_file: return

        # UI Update
        self.chat_box.append(f"<br><b style='color:#fff'>You:</b> {msg}")
        if self.selected_file: self.chat_box.append("<i>[Image Attached]</i>")
        
        self.input_field.clear()
        self.btn_send.setText("...")
        self.btn_send.setEnabled(False)

        # Data Prep
        data = {'message': msg}
        files = {'file': open(self.selected_file, 'rb')} if self.selected_file else None

        # Thread Start
        self.worker = ChatThread(self.render_url, data, files)
        self.worker.finished_signal.connect(self.handle_response)
        self.worker.start()

    def handle_response(self, res):
        self.btn_send.setText("SEND")
        self.btn_send.setEnabled(True)
        self.selected_file = None
        self.file_lbl.clear()

        if res['status'] == 'success':
            reply = res['reply'].replace('\n', '<br>')
            self.chat_box.append(f"<div style='margin-top:10px; color:#00ffcc;'><b>✨ Alya:</b><br>{reply}</div>")
            # Auto scroll to bottom
            sb = self.chat_box.verticalScrollBar()
            sb.setValue(sb.maximum())
        else:
            self.chat_box.append(f"<b style='color:red'>Error:</b> {res['reply']}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AlyaUI()
    window.show()
    sys.exit(app.exec())
