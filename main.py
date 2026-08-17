import sys
import os
import pyautogui
from PyQt6.QtWidgets import QApplication, QMessageBox, QWidget, QLabel, QFileDialog
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize
from PyQt6.QtGui import QFont, QPixmap, QCursor

class RealDesktopTerminator(QWidget):
    def __init__(self):
        super().__init__()
        self.target_path = None
        self.target_file_pos = QPoint(100, 100) # 預設位置，稍後會讓使用者選擇
        self.init_app()

    def init_app(self):
        # 1. 跳出詢問對話框
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
        # 2. 選擇要銷毀的桌面檔案
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        file_path, _ = QFileDialog.getOpenFileName(
            None, 
            "請選擇要銷毀的桌面檔案（選擇後將在點擊位置執行特效）", 
            desktop_path, 
            "所有檔案 (*.*)"
        )

        if not file_path:
            sys.exit()

        self.target_path = file_path
        file_name = os.path.basename(file_path)

        # 3. 點擊確定後，讓使用者點擊螢幕選擇特效發生的位置
        confirm = QMessageBox.question(
            None,
            "⚠️ 最後確認",
            f"確認要銷毀「{file_name}」嗎？\n\n按下「是」後，請用「瞄準」游標點擊檔案所在的螢幕位置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.start_aiming_mode()
        else:
            sys.exit()

    def start_aiming_mode(self):
        # 開啟全螢幕透明透明層，改變游標為瞄準
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # 透明背景
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setCursor(Qt.CursorShape.CrossCursor) # 瞄準游標
        
        # 建立一個佔滿全螢幕的黑色透明層（可選，增加實體感）
        self.overlay = QLabel(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 100);")
        self.overlay.setGeometry(0, 0, QApplication.primaryScreen().size().width(), QApplication.primaryScreen().size().height())
        self.overlay.show()

        self.show()

    def mousePressEvent(self, event):
        # 4. 當使用者用瞄準游標點擊螢幕時，記錄位置並執行特效
        if event.button() == Qt.MouseButton.LeftButton:
            self.target_file_pos = event.globalPosition().toPoint()
            self.setCursor(Qt.CursorShape.ArrowCursor) # 恢復正常游標
            self.start_destruction_animation()

    def start_destruction_animation(self):
        # 移除透明覆蓋層
        self.overlay.close()

        # 建立醜怪物 (👹) - 初始位置在檔案點擊處左側
        self.monster = QLabel("👹", self)
        self.monster.setFont(QFont("Segoe UI Emoji", 80)) # 放大怪物
        self.monster.setFixedSize(QSize(120, 120))
        # 初始位置：檔案點擊位置左側 200 像素
        monster_start_x = self.target_file_pos.x() - 250
        monster_start_y = self.target_file_pos.y() - 60
        self.monster.move(monster_start_x, monster_start_y)
        self.monster.show()

        # 開始怪物走路動畫
        self.anim_current_x = monster_start_x
        # 目標位置：檔案點擊位置旁邊
        self.anim_target_x = self.target_file_pos.x() - 100

        self.timer = QTimer()
        self.timer.timeout.connect(self.move_monster)
        self.timer.start(25) # 調整動畫速度

    def move_monster(self):
        self.anim_current_x += 18 # 調整怪物移動距離
        # 怪物移動，並加上一點上下抖動感
        wobble = (self.anim_current_x // 10 % 2) * 8
        self.monster.move(self.anim_current_x, self.target_file_pos.y() - 60 + wobble)

        # 怪物抵達檔案位置旁邊
        if self.anim_current_x >= self.anim_target_x:
            self.timer.stop()
            self.trigger_explosion()

    def trigger_explosion(self):
        # 5. 怪物變成爆炸特效 (💥) - 精確覆蓋點擊位置
        self.monster.setText("💥")
        self.monster.setFont(QFont("Segoe UI Emoji", 150)) # 大爆炸特效
        self.monster.setFixedSize(QSize(200, 200))
        # 將爆炸中心移到點擊位置
        self.monster.move(self.target_file_pos.x() - 100, self.target_file_pos.y() - 100)
        
        # 刪除真實檔案 (這一步在特效期間同步執行)
        try:
            if self.target_path and os.path.exists(self.target_path):
                os.remove(self.target_path)
                print(f"成功刪除檔案: {self.target_path}")
        except Exception as e:
            print(f"刪除失敗 (可能是因為檔案正在使用): {e}")

        # 爆炸持續一段時間後關閉特效
        QTimer.singleShot(1000, self.finish)

    def finish(self):
        self.hide()
        # 6. 跳出銷毀成功對話框
        QMessageBox.information(None, "💥 完成", "檔案已銷毀！")
        sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 使用 Windows 高 DPI 設定，確保全螢幕定位準確
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ex = RealDesktopTerminator()
    sys.exit(app.exec())
