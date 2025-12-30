# -*- coding: utf-8 -*-
"""
Maya Scene Checker - Check Selector UI
チェック項目選択ダイアログ
"""

import json
import os

try:
    from PySide6 import QtWidgets, QtCore
except ImportError:
    from PySide2 import QtWidgets, QtCore


def load_check_config(config_name="bg_checks"):
    """チェック設定をJSONファイルから読み込む"""
    config_dir = os.path.join(os.path.dirname(__file__), "configs")
    config_path = os.path.join(config_dir, f"{config_name}.json")

    if not os.path.exists(config_path):
        # デフォルト設定
        return {
            "name": "Default Checks",
            "description": "デフォルトのチェック項目",
            "categories": {}
        }

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"設定ファイルの読み込みに失敗: {e}")
        return {
            "name": "Default Checks",
            "description": "デフォルトのチェック項目",
            "categories": {}
        }


def get_available_configs():
    """利用可能な設定ファイルのリストを取得"""
    config_dir = os.path.join(os.path.dirname(__file__), "configs")
    if not os.path.exists(config_dir):
        return []

    configs = []
    for filename in os.listdir(config_dir):
        if filename.endswith(".json"):
            config_name = filename[:-5]  # .jsonを除去
            try:
                with open(os.path.join(config_dir, filename), "r", encoding="utf-8") as f:
                    config = json.load(f)
                    configs.append({
                        "id": config_name,
                        "name": config.get("name", config_name),
                        "description": config.get("description", "")
                    })
            except:
                pass

    return configs


# 後方互換性のため、デフォルト定義を保持（使用されない）
CHECK_CATEGORIES = {
    "頂点": [
        {"name": "Non-Manifold Geometry", "description": "非多様体ジオメトリを検出", "severity": "error"},
        {"name": "Lamina Faces", "description": "ラミナフェースを検出", "severity": "error"},
        {"name": "Zero Edge Length", "description": "長さゼロのエッジを検出", "severity": "warning"},
        {"name": "Isolated Vertices", "description": "孤立した頂点を検出", "severity": "warning"},
    ],
    "メッシュ": [
        {"name": "N-gons", "description": "四角形以外のポリゴンを検出", "severity": "warning"},
        {"name": "Non-Triangulated Faces", "description": "三角形化されていないフェースを検出", "severity": "warning"},
        {"name": "Concave Faces", "description": "凹面を検出", "severity": "warning"},
        {"name": "Duplicate Faces", "description": "重複したフェースを検出", "severity": "error"},
    ],
    "テクスチャ": [
        {"name": "Missing UVs", "description": "UVが設定されていないオブジェクトを検出", "severity": "error"},
        {"name": "Overlapping UVs", "description": "重なったUVを検出", "severity": "warning"},
        {"name": "UV Range", "description": "0-1範囲外のUVを検出", "severity": "warning"},
        {"name": "Missing Textures", "description": "テクスチャファイルが見つからないマテリアルを検出", "severity": "error"},
    ],
    "ネーミング": [
        {"name": "Default Names", "description": "デフォルト名を持つオブジェクトを検出", "severity": "warning"},
        {"name": "Duplicate Names", "description": "重複した名前を検出", "severity": "error"},
        {"name": "Invalid Characters", "description": "無効な文字を含む名前を検出", "severity": "warning"},
        {"name": "Namespace Issues", "description": "名前空間の問題を検出", "severity": "warning"},
    ],
    "トランスフォーム": [
        {"name": "Frozen Transforms", "description": "フリーズされていないトランスフォームを検出", "severity": "warning"},
        {"name": "Non-Zero Pivots", "description": "ゼロでないピボットポイントを検出", "severity": "warning"},
        {"name": "Negative Scale", "description": "負のスケール値を検出", "severity": "error"},
    ],
}


class CheckCategoryWidget(QtWidgets.QWidget):
    """カテゴリごとのチェック項目を表示するウィジェット"""

    def __init__(self, category_name, check_items, parent=None):
        super(CheckCategoryWidget, self).__init__(parent)

        self.category_name = category_name
        self.check_items = check_items
        self.is_expanded = True
        self.checkboxes = []

        self.setup_ui()

    def setup_ui(self):
        """UIのセットアップ"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ヘッダー
        self.header = QtWidgets.QWidget()
        self.header.setFixedHeight(36)
        self.header.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        header_layout = QtWidgets.QHBoxLayout(self.header)
        header_layout.setContentsMargins(12, 6, 12, 6)

        # 展開アイコン
        self.expand_icon = QtWidgets.QLabel("▼")
        self.expand_icon.setFixedWidth(16)
        header_layout.addWidget(self.expand_icon)

        # カテゴリ名
        category_label = QtWidgets.QLabel(self.category_name)
        category_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFFFFF;")
        header_layout.addWidget(category_label)

        header_layout.addStretch()

        # すべて選択/解除ボタン
        self.select_all_btn = QtWidgets.QPushButton("すべて選択")
        self.select_all_btn.setFixedSize(90, 24)
        self.select_all_btn.clicked.connect(self.toggle_select_all)
        header_layout.addWidget(self.select_all_btn)

        self.header.setStyleSheet("""
            QWidget {
                background-color: #2A2A3E;
                border-radius: 4px;
            }
        """)

        layout.addWidget(self.header)

        # コンテンツ
        self.content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(self.content)
        content_layout.setContentsMargins(32, 8, 12, 8)
        content_layout.setSpacing(6)

        # チェック項目
        for item in self.check_items:
            check_widget = QtWidgets.QWidget()
            check_layout = QtWidgets.QHBoxLayout(check_widget)
            check_layout.setContentsMargins(0, 0, 0, 0)

            # チェックボックス
            checkbox = QtWidgets.QCheckBox(item["name"])
            checkbox.setChecked(True)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #FFFFFF;
                    font-size: 12px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border-radius: 3px;
                    border: 2px solid #4A4A5E;
                }
                QCheckBox::indicator:unchecked {
                    background-color: #1E1E2E;
                }
                QCheckBox::indicator:checked {
                    background-color: #4A90E2;
                    border-color: #4A90E2;
                }
            """)
            self.checkboxes.append(checkbox)
            check_layout.addWidget(checkbox, stretch=1)

            # 重要度インジケーター（オプショナル）
            severity_colors = {
                "error": "#FF6B6B",
                "warning": "#FFD93D",
            }
            severity = item.get("severity", "warning")  # デフォルトはwarning
            severity_color = severity_colors.get(severity, "#6BCF7F")
            severity_label = QtWidgets.QLabel("●")
            severity_label.setStyleSheet(f"color: {severity_color}; font-size: 10px;")
            severity_label.setFixedWidth(20)
            check_layout.addWidget(severity_label)

            # 説明
            desc_label = QtWidgets.QLabel(item["description"])
            desc_label.setStyleSheet("color: #B0B0B0; font-size: 11px;")
            desc_label.setFixedWidth(280)
            check_layout.addWidget(desc_label)

            content_layout.addWidget(check_widget)

        self.content.setStyleSheet("""
            QWidget {
                background-color: #1E1E2E;
            }
        """)

        layout.addWidget(self.content)

        # クリックイベント
        self.header.mousePressEvent = self.toggle_expand

    def toggle_expand(self, event):
        """展開/折りたたみの切り替え"""
        self.is_expanded = not self.is_expanded
        self.content.setVisible(self.is_expanded)
        self.expand_icon.setText("▼" if self.is_expanded else "▶")

    def toggle_select_all(self):
        """すべて選択/解除の切り替え"""
        any_checked = any(cb.isChecked() for cb in self.checkboxes)
        for cb in self.checkboxes:
            cb.setChecked(not any_checked)

        # ボタンのテキストを更新
        self.select_all_btn.setText("すべて解除" if not any_checked else "すべて選択")

    def get_selected_checks(self):
        """選択されたチェック項目を取得"""
        selected = []
        for checkbox, item in zip(self.checkboxes, self.check_items):
            if checkbox.isChecked():
                selected.append({
                    "category": self.category_name,
                    "name": item["name"],
                    "description": item["description"],
                    "severity": item.get("severity", "warning"),  # デフォルトはwarning
                    "function": item.get("function", "")
                })
        return selected


class CheckSelectorUI(QtWidgets.QWidget):
    """チェック項目選択ウィンドウ"""

    def __init__(self, config_name="bg_checks", parent=None, callback=None):
        super(CheckSelectorUI, self).__init__(parent)

        self.setWindowTitle("Maya Scene Checker - チェック項目選択")
        self.setMinimumSize(720, 600)
        self.resize(720, 600)

        # ウィンドウフラグを設定（モードレスウィンドウとして動作）
        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowModality(QtCore.Qt.NonModal)

        self.category_widgets = []
        self.selected_checks = []
        self.config_name = config_name
        self.config = load_check_config(config_name)
        self.callback = callback  # チェック実行時のコールバック

        self.setup_ui()
        self.apply_stylesheet()

    def setup_ui(self):
        """UIのセットアップ"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # ヘッダー
        header_layout = QtWidgets.QHBoxLayout()

        title_label = QtWidgets.QLabel(self.config.get("name", "チェック項目を選択"))
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # すべて展開/折りたたみボタン
        self.expand_all_btn = QtWidgets.QPushButton("すべて折りたたむ")
        self.expand_all_btn.setFixedSize(120, 32)
        self.expand_all_btn.clicked.connect(self.toggle_expand_all)
        header_layout.addWidget(self.expand_all_btn)

        main_layout.addLayout(header_layout)

        # スクロールエリア
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # カテゴリコンテナ
        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(8)

        # カテゴリウィジェットを追加
        categories = self.config.get("categories", {})
        for category_name, check_items in categories.items():
            category_widget = CheckCategoryWidget(category_name, check_items)
            container_layout.addWidget(category_widget)
            self.category_widgets.append(category_widget)

        container_layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # ボタン
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QtWidgets.QPushButton("キャンセル")
        cancel_btn.setFixedSize(100, 36)
        cancel_btn.clicked.connect(self.on_cancel_clicked)
        button_layout.addWidget(cancel_btn)

        self.run_btn = QtWidgets.QPushButton("チェック実行")
        self.run_btn.setFixedSize(120, 36)
        self.run_btn.clicked.connect(self.on_run_clicked)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)
        button_layout.addWidget(self.run_btn)

        main_layout.addLayout(button_layout)


    def toggle_expand_all(self):
        """すべてのカテゴリを展開/折りたたみ"""
        expand = self.expand_all_btn.text() == "すべて展開"

        for widget in self.category_widgets:
            if expand and not widget.is_expanded:
                widget.toggle_expand(None)
            elif not expand and widget.is_expanded:
                widget.toggle_expand(None)

        self.expand_all_btn.setText("すべて折りたたむ" if expand else "すべて展開")

    def get_selected_checks(self):
        """選択されたすべてのチェック項目を取得"""
        all_selected = []
        for widget in self.category_widgets:
            all_selected.extend(widget.get_selected_checks())
        return all_selected

    def on_run_clicked(self):
        """チェック実行ボタンが押された時"""
        self.selected_checks = self.get_selected_checks()

        if not self.selected_checks:
            # チェック項目が選択されていない場合
            msg = QtWidgets.QMessageBox(self)
            msg.setWindowTitle("警告")
            msg.setText("チェック項目が選択されていません")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
            msg.exec()
            return

        # コールバックがあれば実行
        if self.callback:
            self.callback(self.selected_checks)

        # ウィンドウを閉じる
        self.close()

    def on_cancel_clicked(self):
        """キャンセルボタンが押された時"""
        self.close()

    def apply_stylesheet(self):
        """スタイルシートを適用"""
        self.setStyleSheet("""
            QWidget {
                background-color: #1A1A2E;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #2A2A3E;
                color: #FFFFFF;
                border: 1px solid #3A3A4E;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3A3A4E;
                border: 1px solid #4A4A5E;
            }
            QPushButton:pressed {
                background-color: #4A4A5E;
            }
            QScrollBar:vertical {
                background: #2A2A3E;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #4A4A5E;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5A5A6E;
            }
        """)
