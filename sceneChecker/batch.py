# -*- coding: utf-8 -*-
"""
Maya Scene Checker - Batch Execution
バッチ実行とCSV出力
"""

import csv
import os
import maya.cmds as cmds
from .checker import SceneChecker
from .check_selector import load_check_config


def run_batch_check(config_name="bg_checks", output_csv=None, scene_file=None):
    """バッチモードでチェックを実行してCSVに出力

    Args:
        config_name: 使用する設定ファイル名（デフォルト: "bg_checks"）
        output_csv: 出力するCSVファイルのパス（Noneの場合は自動生成）
        scene_file: チェックするシーンファイル（Noneの場合は現在のシーン）

    Returns:
        str: 出力されたCSVファイルのパス
    """
    # シーンファイルを開く
    if scene_file:
        if not os.path.exists(scene_file):
            raise FileNotFoundError(f"シーンファイルが見つかりません: {scene_file}")
        cmds.file(scene_file, open=True, force=True)

    # 設定をロード
    config = load_check_config(config_name)

    # すべてのチェックを選択
    all_checks = []
    for category_name, check_items in config.get("categories", {}).items():
        for item in check_items:
            all_checks.append({
                "category": category_name,
                "name": item["name"],
                "description": item["description"],
                "function": item.get("function", "")
            })

    # チェックを実行
    checker = SceneChecker()
    results = checker.run_checks(all_checks)

    # CSV出力パスを決定
    if not output_csv:
        current_scene = cmds.file(query=True, sceneName=True)
        if current_scene:
            scene_name = os.path.splitext(os.path.basename(current_scene))[0]
        else:
            scene_name = "untitled"
        output_csv = f"{scene_name}_check_results.csv"

    # CSVに出力
    export_to_csv(results, output_csv)

    return output_csv


def export_to_csv(results, output_path):
    """チェック結果をCSVファイルに出力

    Args:
        results: チェック結果のリスト
        output_path: 出力先CSVファイルパス
    """
    with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)

        # ヘッダー
        writer.writerow(["チェック名", "重要度", "件数", "説明", "エラー項目"])

        # 結果を書き込み
        for result in results:
            name = result.get("name", "")
            severity = result.get("severity", "")
            count = result.get("count", 0)
            description = result.get("description", "")
            items = result.get("items", [])

            # エラー項目を改行区切りで結合
            items_str = "\n".join(items) if items else ""

            writer.writerow([name, severity, count, description, items_str])

    print(f"チェック結果をCSVに出力しました: {output_path}")


def batch_check_multiple_files(scene_files, config_name="bg_checks", output_dir=None):
    """複数のシーンファイルをバッチチェック

    Args:
        scene_files: チェックするシーンファイルのリスト
        config_name: 使用する設定ファイル名
        output_dir: CSV出力先ディレクトリ（Noneの場合は各シーンと同じ場所）

    Returns:
        list: 出力されたCSVファイルパスのリスト
    """
    output_files = []

    for scene_file in scene_files:
        try:
            # 出力パスを決定
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                scene_name = os.path.splitext(os.path.basename(scene_file))[0]
                output_csv = os.path.join(output_dir, f"{scene_name}_check_results.csv")
            else:
                scene_dir = os.path.dirname(scene_file)
                scene_name = os.path.splitext(os.path.basename(scene_file))[0]
                output_csv = os.path.join(scene_dir, f"{scene_name}_check_results.csv")

            # バッチチェック実行
            result_path = run_batch_check(config_name, output_csv, scene_file)
            output_files.append(result_path)

            print(f"✓ チェック完了: {scene_file}")

        except Exception as e:
            print(f"✗ エラー: {scene_file} - {str(e)}")

    return output_files
