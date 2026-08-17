import sys
import os
import pyautogui
from PyQt6.QtWidgets import QApplication, QMessageBox, QWidget, QLabel, QFileDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap

class RealDesktopTerminator(QWidget):
    def __init__(self):
        super().__init__()
        self.target_path = None
        self.init_ui()

    def init_ui(self):
        reply = QMessageBox.question(
            None,
            "🚨 檔案終結計畫",
            "要執行檔案終結計畫嗎？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.select_file()
        else:
            sys.exit()

    def select_file(self):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        file_path, _ = QFileDialog.getOpenFileName(
            None, 
            "請選擇要銷毀的桌面檔案", 
            desktop_path, 
            "所有檔案 (*.*)"
        )

        if not file_path:
            sys.exit()

        self.target_path = file_path
        file_name = os.path.basename(file_path)

        confirm = QMessageBox.question(
            None,
            "⚠️ 警告",
            f"確認要銷毀「{file_name}」嗎？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.start_full_screen_animation()
        else:
            sys.exit()

    def start_full_screen_animation(self):
        screenshot = pyautogui.screenshot()
        screenshot.save("temp_bg.png")

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        bg_label = QLabel(self)
        bg_label.setPixmap(QPixmap("temp_bg.png"))
        bg_label.setGeometry(0, 0, self.width(), self.height())

        self.monster = QLabel("👹", self)
        self.monster.setFont(QFont("Segoe UI Emoji", 64))
        self.monster.resize(100, 100)
        self.monster.move(-150, self.height() // 2)
        self.monster.show()

        self.show()

        self.anim_x = -150
        self.target_x = self.width() // 2 - 50

        self.timer = QTimer()
        self.timer.timeout.connect(self.move_monster)
        self.timer.start(20)

    def move_monster(self):
        self.anim_x += 15
        self.monster.move(self.anim_x, self.height() // 2 - 50)

        if self.anim_x >= self.target_x:
            self.timer.stop()
            self.trigger_explosion()

    def trigger_explosion(self):
        self.monster.setText("💥")
        self.monster.setFont(QFont("Segoe UI Emoji", 96))
        
        try:
            if os.path.exists(self.target_path):
                os.remove(self.target_path)
        except Exception as e:
            print(f"刪除失敗: {e}")

        QTimer.singleShot(800, self.finish)

    def finish(self):
        self.hide()
        if os.path.exists("temp_bg.png"):
            os.remove("temp_bg.png")

        QMessageBox.information(None, "💥 完成", "檔案已銷毀！")
        sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = RealDesktopTerminator()
    sys.exit(app.exec())
