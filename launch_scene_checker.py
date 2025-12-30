# -*- coding: utf-8 -*-
"""
Maya Scene Checkerの起動スクリプト

Mayaのスクリプトエディタで以下を実行:
    import launch_scene_checker
    launch_scene_checker.main()

    # または設定を指定して実行:
    launch_scene_checker.main("motion_checks")
    launch_scene_checker.main("effect_checks")
"""

import sys
import os

# スクリプトのパスを追加
script_path = os.path.dirname(__file__)
if script_path not in sys.path:
    sys.path.insert(0, script_path)

from sceneChecker import run


def main(config_name="bg_checks"):
    """メイン関数 - チェック項目選択から実行

    Args:
        config_name: 使用する設定ファイル名
                    - "bg_checks": 背景アセット用
                    - "motion_checks": モーション用
                    - "effect_checks": エフェクト用
    """
    return run(config_name)


if __name__ == "__main__":
    main()
