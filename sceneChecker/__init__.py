# -*- coding: utf-8 -*-
"""
Maya Scene Checker
Maya2025向けシーンチェッカー

使用例:
    # チェック項目選択から実行
    from sceneChecker import run
    run()

    # バッチモードでCSV出力
    from sceneChecker import batch
    batch()
"""

from .ui import SceneCheckerUI
from .check_selector import CheckSelectorUI
from .main import run_scene_checker
from .batch import run_batch_check, batch_check_multiple_files, export_to_csv


def run(config_name="bg_checks"):
    """シーンチェッカーを実行（チェック項目選択→チェック実行→結果表示）

    Args:
        config_name: 使用する設定ファイル名（"bg_checks", "motion_checks", "effect_checks"）
    """
    return run_scene_checker(config_name)


def batch(config_name="bg_checks", output_csv=None, scene_file=None):
    """バッチモードでチェックを実行してCSVに出力

    Args:
        config_name: 使用する設定ファイル名（デフォルト: "bg_checks"）
        output_csv: 出力するCSVファイルのパス（Noneの場合は自動生成）
        scene_file: チェックするシーンファイル（Noneの場合は現在のシーン）

    Returns:
        str: 出力されたCSVファイルのパス
    """
    return run_batch_check(config_name, output_csv, scene_file)


def batch_multiple(scene_files, config_name="bg_checks", output_dir=None):
    """複数のシーンファイルをバッチチェック

    Args:
        scene_files: チェックするシーンファイルのリスト
        config_name: 使用する設定ファイル名
        output_dir: CSV出力先ディレクトリ（Noneの場合は各シーンと同じ場所）

    Returns:
        list: 出力されたCSVファイルパスのリスト
    """
    return batch_check_multiple_files(scene_files, config_name, output_dir)


__all__ = [
    'run', 'batch', 'batch_multiple',
    'SceneCheckerUI', 'CheckSelectorUI',
    'run_scene_checker',
    'run_batch_check', 'batch_check_multiple_files', 'export_to_csv'
]
