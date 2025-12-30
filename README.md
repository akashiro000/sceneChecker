# Maya Scene Checker

Maya 2025向けのシーンチェッカーツール

## 概要

Maya Scene Checkerは、Mayaシーンの品質をチェックし、一般的な問題を検出するツールです。背景アセット、モーション、エフェクトなど、用途別の設定ファイルを使用してチェック項目をカスタマイズできます。

## 特徴

- **外部JSON設定**: チェック項目を外部JSONファイルで管理
- **モードレスUI**: Mayaのメインウィンドウと並行して操作可能
- **進捗表示**: ESCキーでキャンセル可能なプログレスダイアログ
- **自動修正機能**: 修正可能な問題に対してAdjustボタンを提供
- **バッチ処理**: 複数シーンファイルを一括チェックしてCSV出力

## インストール

1. このリポジトリをMayaのスクリプトディレクトリにクローン:
```bash
cd C:\Users\<username>\Documents\maya\scripts
git clone https://github.com/<username>/sceneChecker.git
```

2. または、ZIPファイルをダウンロードして解凍

## 使用方法

### 基本的な使い方

```python
# Mayaスクリプトエディタで実行
import launch_scene_checker
launch_scene_checker.main()

# または直接sceneCheckerモジュールを使用
from sceneChecker import run
run("bg_checks")  # 背景アセット用チェック
```

### 設定ファイルを指定して実行

```python
import launch_scene_checker

# 背景アセット用
launch_scene_checker.main("bg_checks")

# モーション用
launch_scene_checker.main("motion_checks")

# エフェクト用
launch_scene_checker.main("effect_checks")
```

### バッチモード（CSV出力）

```python
from sceneChecker import batch

# 現在のシーンをチェック
batch("bg_checks", output_csv="C:/temp/check_results.csv")

# 複数ファイルを一括チェック
from sceneChecker import batch_multiple
scene_files = [
    "C:/projects/scene1.ma",
    "C:/projects/scene2.ma"
]
batch_multiple(scene_files, "bg_checks", output_dir="C:/temp/results")
```

## チェック項目

### 背景アセット用 (bg_checks)

- **ジオメトリ**: Non-Manifold Geometry, N-gons, Zero Area Faces
- **テクスチャ**: UV Issues, Missing Textures
- **ネーミング**: BG Naming Convention (`{area}_{modelname}_{id}`)
- **トランスフォーム**: Transform Issues (非フリーズ、負のスケール)

### モーション用 (motion_checks)

- **リグ**: Rig Issues, Skinning Issues, Unused Influences
- **アニメーション**: Animation Keys
- **ネーミング**: Naming Convention

### エフェクト用 (effect_checks)

- **ジオメトリ**: Geometry Issues
- **シェーダー**: Shader Issues (lambert1以外を検出)
- **テクスチャ**: UV Issues, Texture Sequences
- **ネーミング**: Naming Convention

## カスタム設定の作成

`sceneChecker/configs/` ディレクトリに新しいJSONファイルを作成:

```json
{
  "name": "Custom Checks",
  "description": "カスタムチェック項目",
  "categories": {
    "カテゴリ名": [
      {
        "name": "チェック名",
        "description": "チェックの説明",
        "severity": "error",
        "function": "check_function_name"
      }
    ]
  }
}
```

## 修正機能 (Adjust)

以下のチェック項目は自動修正が可能です:

- Lamina Faces - 削除
- Zero Edge Length - 頂点マージ
- N-gons - 三角形化
- Zero Area Faces - 削除
- Non-Frozen Transforms - フリーズ
- Negative Scale - 修正（ジオメトリ反転）
- Unused Influences - 削除

## 技術仕様

- **対応バージョン**: Maya 2025
- **UIフレームワーク**: PySide6/PySide2
- **Python**: 3.x
- **アーキテクチャ**: モードレスQWidget

## ライセンス

MIT License

## 作者

- 開発: Claude Sonnet 4.5 with Claude Code
