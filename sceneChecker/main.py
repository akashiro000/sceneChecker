# -*- coding: utf-8 -*-
"""
Maya Scene Checker - Main
チェック項目選択から結果表示までの統合
"""

try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets

from .check_selector import CheckSelectorUI
from .ui import SceneCheckerUI
from .checker import SceneChecker
from .progress_dialog import ProgressDialog


def get_maya_main_window():
    """Mayaのメインウィンドウを取得"""
    try:
        import maya.OpenMayaUI as omui
        from shiboken2 import wrapInstance
        main_window_ptr = omui.MQtUtil.mainWindow()
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    except:
        try:
            from shiboken6 import wrapInstance
            import maya.OpenMayaUI as omui
            main_window_ptr = omui.MQtUtil.mainWindow()
            return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
        except:
            return None


def run_scene_checker(config_name="bg_checks"):
    """シーンチェッカーを実行

    Args:
        config_name: 使用する設定ファイル名（デフォルト: "bg_checks"）
    """
    # Mayaのメインウィンドウを取得
    maya_main = get_maya_main_window()

    def on_checks_selected(selected_checks):
        """チェック項目が選択された時のコールバック"""
        # プログレスダイアログを表示
        progress = ProgressDialog("シーンチェック実行中", parent=maya_main)
        progress.show()

        # チェックを実行
        checker = SceneChecker()

        def progress_callback(current, total, message):
            return progress.update_progress(current, total, message)

        results = checker.run_checks(selected_checks, progress_callback)

        # プログレスダイアログを閉じる
        progress.close()

        # キャンセルされた場合
        if checker.cancelled:
            msg = QtWidgets.QMessageBox(maya_main)
            msg.setWindowTitle("情報")
            msg.setText("チェックがキャンセルされました")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.exec()
            return

        # 結果ウィンドウを表示（モードレス、parentなしで完全独立）
        result_ui = SceneCheckerUI(parent=None)

        # 結果を追加
        for result_data in results:
            result_ui.add_check_result(
                result_data["name"],
                result_data["count"],
                result_data["severity"],
                result_data["description"],
                result_data["items"],
                result_data.get("adjust_function")
            )

        result_ui.show()

        # グローバル変数として保持
        global _scene_checker_ui
        _scene_checker_ui = result_ui

    # チェック項目選択ウィンドウを表示（モードレス）
    selector = CheckSelectorUI(config_name=config_name, parent=maya_main, callback=on_checks_selected)
    selector.show()

    # グローバル変数として保持
    global _check_selector_ui
    _check_selector_ui = selector

    return selector
