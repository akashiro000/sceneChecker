# -*- coding: utf-8 -*-
"""
Maya Scene Checker UI
Maya2025向けシーンチェッカーのUIモジュール
"""

try:
    from PySide6 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui

from . import checker as checker_module


class CheckResultWidget(QtWidgets.QWidget):
    """個別のチェック結果を表示するウィジェット"""

    def __init__(self, check_name, count, severity, description="", items=None, adjust_function=None, parent=None):
        super(CheckResultWidget, self).__init__(parent)

        self.check_name = check_name
        self.count = count
        self.severity = severity  # "error", "warning", "success"
        self.description = description
        self.items = items or []
        self.adjust_function = adjust_function
        self.is_expanded = False

        self.setup_ui()

    def setup_ui(self):
        """UIのセットアップ"""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ヘッダー部分
        self.header = QtWidgets.QWidget()
        self.header.setFixedHeight(40)
        self.header.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        header_layout = QtWidgets.QHBoxLayout(self.header)
        header_layout.setContentsMargins(12, 8, 12, 8)

        # 展開アイコン
        self.expand_icon = QtWidgets.QLabel("▶")
        self.expand_icon.setFixedWidth(16)
        header_layout.addWidget(self.expand_icon)

        # ステータスアイコン
        severity_icon, icon_color = self.get_severity_icon()
        icon_label = QtWidgets.QLabel(severity_icon)
        icon_label.setFixedWidth(20)
        icon_label.setStyleSheet(f"color: {icon_color}; font-size: 16px;")
        header_layout.addWidget(icon_label)

        # チェック名
        name_label = QtWidgets.QLabel(self.check_name)
        name_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #FFFFFF;")
        header_layout.addWidget(name_label)

        # カウント（色付き）
        count_color = self.get_count_color()
        count_label = QtWidgets.QLabel(f"({self.count})")
        count_label.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {count_color};")
        header_layout.addWidget(count_label)

        header_layout.addStretch()

        # Adjustボタン（エラーと警告の場合のみ、adjust_functionが定義されている場合のみ有効）
        if self.severity in ["error", "warning"] and self.count > 0:
            self.adjust_btn = QtWidgets.QPushButton("Adjust")
            self.adjust_btn.setFixedSize(70, 28)

            # adjust_functionがNoneまたは未定義の場合は無効化
            if not self.adjust_function:
                self.adjust_btn.setEnabled(False)
                self.adjust_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3A3A4E;
                        color: #808080;
                        border: none;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                """)
            else:
                self.adjust_btn.clicked.connect(self.on_adjust_clicked)
                self.adjust_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4A90E2;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #357ABD;
                    }
                """)
            header_layout.addWidget(self.adjust_btn)

        # ヘッダーの背景色
        header_bg = self.get_header_background()
        self.header.setStyleSheet(f"""
            QWidget {{
                background-color: {header_bg};
                border-radius: 4px;
            }}
        """)

        layout.addWidget(self.header)

        # 詳細コンテンツ
        self.content = QtWidgets.QWidget()
        self.content.setVisible(False)
        content_layout = QtWidgets.QVBoxLayout(self.content)
        content_layout.setContentsMargins(40, 12, 12, 12)

        # 説明文
        if self.description:
            desc_label = QtWidgets.QLabel(self.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #B0B0B0; font-size: 12px; padding-bottom: 8px;")
            content_layout.addWidget(desc_label)

        # アイテムリスト（リストビュー）
        if self.items:
            items_label = QtWidgets.QLabel(f"エラー詳細 ({len(self.items)}件)")
            items_label.setStyleSheet("color: #FFFFFF; font-size: 11px; font-weight: bold; padding-top: 4px;")
            content_layout.addWidget(items_label)

            # リストビュー
            self.items_list = QtWidgets.QListWidget()
            self.items_list.setMaximumHeight(200)
            self.items_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
            self.items_list.addItems(self.items)
            self.items_list.setStyleSheet("""
                QListWidget {
                    background-color: #2A2A3E;
                    color: #D0D0D0;
                    border: none;
                    font-size: 11px;
                    font-family: 'Consolas', monospace;
                    padding: 4px;
                }
                QListWidget::item {
                    padding: 4px;
                    border-radius: 2px;
                }
                QListWidget::item:selected {
                    background-color: #4A90E2;
                    color: white;
                }
                QListWidget::item:hover {
                    background-color: #3A3A4E;
                }
                QScrollBar:vertical {
                    background: #2A2A3E;
                    width: 8px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background: #4A4A5E;
                    border-radius: 4px;
                }
            """)

            # 選択時のイベント接続
            self.items_list.itemSelectionChanged.connect(self.on_selection_changed)

            content_layout.addWidget(self.items_list)

        self.content.setStyleSheet("""
            QWidget {
                background-color: #1E1E2E;
            }
        """)

        layout.addWidget(self.content)

        # クリックイベント
        self.header.mousePressEvent = self.toggle_expand

    def get_severity_icon(self):
        """重要度に応じたアイコンと色を返す"""
        icons = {
            "error": ("⚠", "#FF6B6B"),
            "warning": ("⚠", "#FFD93D"),
            "success": ("✓", "#6BCF7F")
        }
        return icons.get(self.severity, ("●", "#FFFFFF"))

    def get_count_color(self):
        """件数の色を返す"""
        colors = {
            "error": "#FF6B6B",
            "warning": "#FFD93D",
            "success": "#6BCF7F"
        }
        return colors.get(self.severity, "#FFFFFF")

    def get_header_background(self):
        """ヘッダーの背景色を返す"""
        colors = {
            "error": "#2A1E2E",
            "warning": "#2A2A1E",
            "success": "#1E2A1E"
        }
        return colors.get(self.severity, "#2A2A3E")

    def toggle_expand(self, event):
        """展開/折りたたみの切り替え"""
        self.is_expanded = not self.is_expanded
        self.content.setVisible(self.is_expanded)
        self.expand_icon.setText("▼" if self.is_expanded else "▶")

    def on_adjust_clicked(self):
        """Adjustボタンがクリックされた時の処理"""
        if not self.adjust_function:
            return

        try:
            # adjust_function名からグローバル関数を取得
            adjust_func = getattr(checker_module, self.adjust_function, None)
            if adjust_func and callable(adjust_func):
                # Adjust処理を実行
                success = adjust_func(self.items)

                if success:
                    # 成功メッセージ
                    try:
                        from PySide6.QtWidgets import QMessageBox
                    except ImportError:
                        from PySide2.QtWidgets import QMessageBox

                    msg = QMessageBox(self)
                    msg.setWindowTitle("成功")
                    msg.setText(f"{self.check_name} の修正が完了しました")
                    msg.setIcon(QMessageBox.Icon.Information)
                    msg.exec()

                    # ウィンドウを閉じる（再チェックを促す）
                    parent_window = self.window()
                    if parent_window:
                        parent_window.close()
        except Exception as e:
            # エラーメッセージ
            try:
                from PySide6.QtWidgets import QMessageBox
            except ImportError:
                from PySide2.QtWidgets import QMessageBox

            msg = QMessageBox(self)
            msg.setWindowTitle("エラー")
            msg.setText(f"修正中にエラーが発生しました:\n{str(e)}")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()

    def on_selection_changed(self):
        """リストビューの選択が変更された時の処理"""
        try:
            import maya.cmds as cmds
            selected_items = self.items_list.selectedItems()
            if selected_items:
                # 選択されたアイテムからオブジェクト名を抽出
                selection = []
                for item in selected_items:
                    item_text = item.text()
                    # "pCube1.vtx[45]" のような形式からMayaで選択可能な形式に変換
                    selection.append(item_text)

                # Mayaで選択
                if selection:
                    cmds.select(selection, replace=True)
        except ImportError:
            # Maya環境外では何もしない
            pass
        except Exception as e:
            # エラーが発生しても無視（スタンドアロンモードなど）
            pass


class SceneCheckerUI(QtWidgets.QWidget):
    """Maya Scene Checkerのメインウィンドウ"""

    def __init__(self, parent=None):
        super(SceneCheckerUI, self).__init__(parent)

        self.setWindowTitle("Maya Scene Checker")
        self.setMinimumSize(720, 480)
        self.resize(720, 480)

        # ウィンドウフラグを設定（モードレスウィンドウとして動作）
        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        # モーダルではないことを明示的に設定
        self.setWindowModality(QtCore.Qt.NonModal)

        self.check_results = []

        self.setup_ui()
        self.apply_stylesheet()

    def setup_ui(self):
        """UIのセットアップ"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # ヘッダー
        header_layout = QtWidgets.QHBoxLayout()

        title_label = QtWidgets.QLabel("Maya Scene Checker")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # すべて展開ボタン
        self.expand_all_btn = QtWidgets.QPushButton("すべて展開")
        self.expand_all_btn.setFixedSize(100, 32)
        self.expand_all_btn.clicked.connect(self.expand_all)
        header_layout.addWidget(self.expand_all_btn)

        main_layout.addLayout(header_layout)

        # サマリー
        self.summary_layout = QtWidgets.QHBoxLayout()
        self.summary_layout.setSpacing(16)

        self.error_summary = self.create_summary_label("エラー: 0", "#FF6B6B")
        self.warning_summary = self.create_summary_label("警告: 0", "#FFD93D")
        self.success_summary = self.create_summary_label("成功: 0", "#6BCF7F")

        self.summary_layout.addWidget(self.error_summary)
        self.summary_layout.addWidget(self.warning_summary)
        self.summary_layout.addWidget(self.success_summary)
        self.summary_layout.addStretch()

        main_layout.addLayout(self.summary_layout)

        # チェック結果エリア
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.results_container = QtWidgets.QWidget()
        self.results_layout = QtWidgets.QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(8)
        self.results_layout.addStretch()

        scroll.setWidget(self.results_container)
        main_layout.addWidget(scroll)

    def create_summary_label(self, text, color):
        """サマリーラベルを作成"""
        label = QtWidgets.QLabel(text)
        label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 13px;
                font-weight: bold;
                padding: 4px 8px;
            }}
        """)
        return label

    def add_check_result(self, check_name, count, severity, description="", items=None, adjust_function=None):
        """チェック結果を追加"""
        result_widget = CheckResultWidget(check_name, count, severity, description, items, adjust_function)
        self.results_layout.insertWidget(self.results_layout.count() - 1, result_widget)
        self.check_results.append(result_widget)

        # サマリーを更新
        self.update_summary()

    def update_summary(self):
        """サマリーを更新"""
        errors = sum(1 for r in self.check_results if r.severity == "error")
        warnings = sum(1 for r in self.check_results if r.severity == "warning")
        successes = sum(1 for r in self.check_results if r.severity == "success")

        self.error_summary.setText(f"エラー: {errors}")
        self.warning_summary.setText(f"警告: {warnings}")
        self.success_summary.setText(f"成功: {successes}")

    def expand_all(self):
        """すべての結果を展開"""
        expand = self.expand_all_btn.text() == "すべて展開"

        for result in self.check_results:
            if expand and not result.is_expanded:
                result.toggle_expand(None)
            elif not expand and result.is_expanded:
                result.toggle_expand(None)

        self.expand_all_btn.setText("すべて折りたたむ" if expand else "すべて展開")

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
