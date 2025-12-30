# -*- coding: utf-8 -*-
"""
Maya Scene Checker - Progress Dialog
プログレスバーダイアログ
"""

try:
    from PySide6 import QtWidgets, QtCore
except ImportError:
    from PySide2 import QtWidgets, QtCore


class ProgressDialog(QtWidgets.QDialog):
    """プログレスバーダイアログ"""

    def __init__(self, title="処理中", parent=None):
        super(ProgressDialog, self).__init__(parent)

        self.setWindowTitle(title)
        self.setMinimumSize(500, 150)
        self.setModal(True)
        self.cancelled = False

        self.setup_ui()
        self.apply_stylesheet()

    def setup_ui(self):
        """UIのセットアップ"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # メッセージラベル
        self.message_label = QtWidgets.QLabel("処理を開始しています...")
        self.message_label.setStyleSheet("color: #FFFFFF; font-size: 13px;")
        layout.addWidget(self.message_label)

        # プログレスバー
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(28)
        layout.addWidget(self.progress_bar)

        # キャンセルボタン
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QtWidgets.QPushButton("キャンセル (ESC)")
        self.cancel_btn.setFixedSize(150, 32)
        self.cancel_btn.clicked.connect(self.on_cancel)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def apply_stylesheet(self):
        """スタイルシートを適用"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E2E;
            }
            QProgressBar {
                background-color: #2A2A3E;
                border: 2px solid #3A3A4E;
                border-radius: 6px;
                text-align: center;
                color: #FFFFFF;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4A90E2,
                    stop:1 #357ABD
                );
                border-radius: 4px;
            }
            QPushButton {
                background-color: #4A4A5E;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5A5A6E;
            }
        """)

    def update_progress(self, current, total, message=""):
        """プログレスを更新

        Args:
            current: 現在の進捗
            total: 全体数
            message: 表示メッセージ

        Returns:
            bool: キャンセルされていない場合True
        """
        if self.cancelled:
            return False

        percentage = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percentage)

        if message:
            self.message_label.setText(message)

        # UIを更新
        QtWidgets.QApplication.processEvents()

        return not self.cancelled

    def on_cancel(self):
        """キャンセルボタンが押された時"""
        self.cancelled = True
        self.message_label.setText("キャンセル中...")
        self.cancel_btn.setEnabled(False)

    def keyPressEvent(self, event):
        """キーイベントハンドラ"""
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.on_cancel()
        else:
            super(ProgressDialog, self).keyPressEvent(event)
