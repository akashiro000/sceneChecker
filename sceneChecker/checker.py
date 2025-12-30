# -*- coding: utf-8 -*-
"""
Maya Scene Checker - Checker Logic
チェックロジックの実装
"""

import maya.cmds as cmds


# ========================================
# Adjust関数（修正関数）
# ========================================

def adjust_lamina_faces(items):
    """ラミナフェースを削除"""
    if items:
        cmds.select(items)
        cmds.delete()
        return True
    return False


def adjust_zero_edge_length(items):
    """長さゼロのエッジをマージ"""
    if items:
        for edge in items:
            try:
                # エッジを構成する頂点を取得してマージ
                vertices = cmds.polyListComponentConversion(edge, toVertex=True)
                if vertices:
                    cmds.polyMergeVertex(vertices, distance=0.001)
            except:
                pass
        return True
    return False


def adjust_ngons(items):
    """N-gonを三角形/四角形に分割"""
    if items:
        cmds.select(items)
        cmds.polyTriangulate()
        return True
    return False


def adjust_zero_area_faces(items):
    """面積ゼロのフェースを削除"""
    if items:
        cmds.select(items)
        cmds.delete()
        return True
    return False


def adjust_non_frozen_transforms(items):
    """トランスフォームをフリーズ"""
    if items:
        cmds.select(items)
        cmds.makeIdentity(apply=True, translate=True, rotate=True, scale=True)
        return True
    return False


def adjust_negative_scale(items):
    """負のスケールを修正（ジオメトリを反転してスケールを正に）"""
    if items:
        for obj in items:
            try:
                # 負のスケール軸を検出
                scale = cmds.getAttr(f"{obj}.scale")[0]
                for i, s in enumerate(scale):
                    if s < 0:
                        # スケールを正にしてジオメトリを反転
                        axis = ['X', 'Y', 'Z'][i]
                        cmds.setAttr(f"{obj}.scale{axis}", abs(s))
                        # メッシュのノーマルを反転
                        shapes = cmds.listRelatives(obj, shapes=True, type="mesh")
                        if shapes:
                            cmds.polyNormal(shapes[0], normalMode=0, userNormalMode=0)
            except:
                pass
        return True
    return False


def adjust_unused_influences(items):
    """未使用のインフルエンスを削除"""
    if items:
        for item in items:
            try:
                # "skinCluster -> influence" の形式から分離
                parts = item.split(" -> ")
                if len(parts) == 2:
                    skin, influence = parts
                    cmds.skinCluster(skin, edit=True, removeInfluence=influence)
            except:
                pass
        return True
    return False


# ========================================
# ジオメトリチェック
# ========================================

def check_geometry_issues(check_info):
    """ジオメトリの問題をまとめてチェック"""
    results = []
    meshes = cmds.ls(type="mesh", long=True)

    # Non-Manifold頂点
    non_manifold = []
    for mesh in meshes:
        cmds.select(mesh)
        cmds.polySelectConstraint(mode=3, type=0x0001, nonmanifold=1)
        vertices = cmds.ls(sl=True, flatten=True)
        cmds.polySelectConstraint(disable=True)
        if vertices:
            non_manifold.extend(vertices)

    if non_manifold:
        results.append({
            "name": "Non-Manifold Vertices",
            "count": len(non_manifold),
            "severity": "error",
            "description": "非多様体頂点が検出されました",
            "items": non_manifold,
            "adjust_function": None
        })

    # Lamina Faces
    lamina = []
    for mesh in meshes:
        cmds.select(mesh)
        cmds.polySelectConstraint(mode=3, type=0x0008, topology=2)
        faces = cmds.ls(sl=True, flatten=True)
        cmds.polySelectConstraint(disable=True)
        if faces:
            lamina.extend(faces)

    if lamina:
        results.append({
            "name": "Lamina Faces",
            "count": len(lamina),
            "severity": "error",
            "description": "ラミナフェースが検出されました",
            "items": lamina,
            "adjust_function": adjust_lamina_faces
        })

    # Zero Edge Length
    zero_edges = []
    for mesh in meshes:
        try:
            edges = cmds.polyListComponentConversion(mesh, toEdge=True)
            if edges:
                cmds.select(edges)
                cmds.polySelectConstraint(mode=3, type=0x8000, length=1, lengthbound=(0, 0.0001))
                edge_list = cmds.ls(sl=True, flatten=True)
                cmds.polySelectConstraint(disable=True)
                if edge_list:
                    zero_edges.extend(edge_list)
        except:
            pass

    if zero_edges:
        results.append({
            "name": "Zero Edge Length",
            "count": len(zero_edges),
            "severity": "warning",
            "description": "長さゼロのエッジが検出されました",
            "items": zero_edges,
            "adjust_function": adjust_zero_edge_length
        })

    return results


def check_ngons(check_info):
    """N-gonをチェック"""
    meshes = cmds.ls(type="mesh", long=True)
    ngons = []

    for mesh in meshes:
        try:
            cmds.select(mesh)
            cmds.polySelectConstraint(mode=3, type=0x0008, size=3)
            faces = cmds.ls(sl=True, flatten=True)
            cmds.polySelectConstraint(disable=True)
            if faces:
                ngons.extend(faces)
        except:
            pass

    if ngons:
        return {
            "name": check_info["name"],
            "count": len(ngons),
            "severity": check_info["severity"],
            "description": check_info["description"],
            "items": ngons,
            "adjust_function": adjust_ngons
        }
    return None


def check_zero_area_faces(check_info):
    """面積ゼロのフェースをチェック"""
    meshes = cmds.ls(type="mesh", long=True)
    zero_faces = []

    for mesh in meshes:
        try:
            num_faces = cmds.polyEvaluate(mesh, face=True)
            for i in range(num_faces):
                face = f"{mesh}.f[{i}]"
                area = cmds.polyEvaluate(face, faceArea=True)
                if area < 0.0001:
                    zero_faces.append(face)
        except:
            pass

    if zero_faces:
        return {
            "name": check_info["name"],
            "count": len(zero_faces),
            "severity": check_info["severity"],
            "description": check_info["description"],
            "items": zero_faces,
            "adjust_function": adjust_zero_area_faces
        }
    return None


# ========================================
# テクスチャ・UVチェック
# ========================================

def check_uv_issues(check_info):
    """UVの問題をまとめてチェック"""
    results = []
    meshes = cmds.ls(type="mesh", long=True)

    # Missing UVs
    missing_uvs = []
    for mesh in meshes:
        try:
            uv_sets = cmds.polyUVSet(mesh, query=True, allUVSets=True)
            if not uv_sets or len(uv_sets) == 0:
                transform = cmds.listRelatives(mesh, parent=True, fullPath=True)
                if transform:
                    missing_uvs.append(transform[0])
        except:
            pass

    if missing_uvs:
        results.append({
            "name": "Missing UVs",
            "count": len(missing_uvs),
            "severity": "error",
            "description": "UVが設定されていないメッシュが検出されました",
            "items": missing_uvs
        })

    # UV Range (0-1範囲外)
    out_of_range = []
    for mesh in meshes:
        try:
            uvs = cmds.polyListComponentConversion(mesh, toUV=True)
            if uvs:
                uvs_flat = cmds.ls(uvs, flatten=True)
                for uv in uvs_flat:
                    pos = cmds.polyEditUV(uv, query=True)
                    if pos and (pos[0] < 0 or pos[0] > 1 or pos[1] < 0 or pos[1] > 1):
                        out_of_range.append(uv)
                        if len(out_of_range) >= 50:  # 最大50個まで
                            break
        except:
            pass

    if out_of_range:
        results.append({
            "name": "UV Out of Range",
            "count": len(out_of_range),
            "severity": "warning",
            "description": "0-1範囲外のUVが検出されました",
            "items": out_of_range
        })

    return results


def check_missing_textures(check_info):
    """テクスチャファイルが見つからないマテリアルをチェック"""
    import os
    missing = []

    file_nodes = cmds.ls(type="file")
    for node in file_nodes:
        try:
            texture_path = cmds.getAttr(f"{node}.fileTextureName")
            if texture_path and not os.path.exists(texture_path):
                missing.append(f"{node} -> {texture_path}")
        except:
            pass

    if missing:
        return {
            "name": check_info["name"],
            "count": len(missing),
            "severity": check_info["severity"],
            "description": check_info["description"],
            "items": missing
        }
    return None


def check_texture_sequences(check_info):
    """テクスチャシーケンスの問題をチェック"""
    import os
    import re

    sequence_issues = []
    file_nodes = cmds.ls(type="file")

    for node in file_nodes:
        try:
            texture_path = cmds.getAttr(f"{node}.fileTextureName")
            if texture_path and "<" in texture_path:  # シーケンス記法
                # フレーム番号のパターンを検出
                pattern = re.sub(r'<.*?>', '*', texture_path)
                directory = os.path.dirname(pattern)
                if not os.path.exists(directory):
                    sequence_issues.append(f"{node} -> {texture_path} (ディレクトリが見つかりません)")
        except:
            pass

    if sequence_issues:
        return {
            "name": check_info["name"],
            "count": len(sequence_issues),
            "severity": check_info["severity"],
            "description": check_info["description"],
            "items": sequence_issues
        }
    return None


# ========================================
# ネーミングチェック
# ========================================

def check_naming_issues(check_info):
    """ネーミングの問題をまとめてチェック（汎用）"""
    results = []
    all_objects = cmds.ls(transforms=True, long=True)

    # カメラを除外
    all_objects = [obj for obj in all_objects if cmds.nodeType(obj) != "camera" and not cmds.listRelatives(obj, shapes=True, type="camera")]

    # Default Names
    default_names = []
    default_patterns = ["pCube", "pSphere", "pCylinder", "pPlane", "pTorus", "polySurface", "group"]
    for obj in all_objects:
        short_name = obj.split("|")[-1]
        for pattern in default_patterns:
            if short_name.startswith(pattern):
                default_names.append(obj)
                break

    if default_names:
        results.append({
            "name": "Default Names",
            "count": len(default_names),
            "severity": "warning",
            "description": "デフォルト名のオブジェクトが検出されました",
            "items": default_names,
            "adjust_function": None
        })

    # Duplicate Names
    all_short_names = [obj.split("|")[-1] for obj in all_objects]
    name_count = {}
    for name in all_short_names:
        name_count[name] = name_count.get(name, 0) + 1

    duplicate_names = []
    for name, count in name_count.items():
        if count > 1:
            duplicates = cmds.ls(name, long=True)
            duplicate_names.extend(duplicates)

    if duplicate_names:
        results.append({
            "name": "Duplicate Names",
            "count": len(duplicate_names),
            "severity": "error",
            "description": "重複した名前のオブジェクトが検出されました",
            "items": duplicate_names,
            "adjust_function": None
        })

    # Invalid Characters
    invalid_chars = []
    for obj in all_objects:
        short_name = obj.split("|")[-1]
        if any(c in short_name for c in [" ", ".", "-", ":", ";"]):
            invalid_chars.append(obj)

    if invalid_chars:
        results.append({
            "name": "Invalid Characters",
            "count": len(invalid_chars),
            "severity": "warning",
            "description": "無効な文字を含む名前が検出されました",
            "items": invalid_chars,
            "adjust_function": None
        })

    return results


def check_bg_naming_convention(check_info):
    """BG専用の厳格な命名規則チェック

    命名規則: {area}_{modelname}_{id}
    - area: アルファベット4文字（例: maps, city）
    - modelname: アルファベット1-10文字（例: building, tree）
    - id: 3桁の数字（例: 001, 099）
    """
    import re

    all_objects = cmds.ls(transforms=True, long=True)

    # カメラを除外
    all_objects = [obj for obj in all_objects if cmds.nodeType(obj) != "camera" and not cmds.listRelatives(obj, shapes=True, type="camera")]

    invalid_names = []

    # 正規表現パターン: {4文字アルファベット}_{1-10文字アルファベット}_{3桁数字}
    pattern = re.compile(r'^[a-zA-Z]{4}_[a-zA-Z]{1,10}_\d{3}$')

    for obj in all_objects:
        short_name = obj.split("|")[-1]
        if not pattern.match(short_name):
            invalid_names.append(f"{obj} (期待形式: area_modelname_id)")

    if invalid_names:
        return {
            "name": check_info["name"],
            "count": len(invalid_names),
            "severity": "error",
            "description": check_info["description"],
            "items": invalid_names,
            "adjust_function": None
        }
    return None


# ========================================
# トランスフォームチェック
# ========================================

def check_transform_issues(check_info):
    """トランスフォームの問題をまとめてチェック"""
    results = []
    transforms = cmds.ls(type="transform", long=True)

    # Non-Frozen Transforms
    non_frozen = []
    for transform in transforms:
        try:
            # メッシュを持つトランスフォームのみチェック
            shapes = cmds.listRelatives(transform, shapes=True, type="mesh")
            if shapes:
                translate = cmds.getAttr(f"{transform}.translate")[0]
                rotate = cmds.getAttr(f"{transform}.rotate")[0]
                scale = cmds.getAttr(f"{transform}.scale")[0]

                if (abs(translate[0]) > 0.0001 or abs(translate[1]) > 0.0001 or abs(translate[2]) > 0.0001 or
                    abs(rotate[0]) > 0.0001 or abs(rotate[1]) > 0.0001 or abs(rotate[2]) > 0.0001 or
                    abs(scale[0] - 1.0) > 0.0001 or abs(scale[1] - 1.0) > 0.0001 or abs(scale[2] - 1.0) > 0.0001):
                    non_frozen.append(transform)
        except:
            pass

    if non_frozen:
        results.append({
            "name": "Non-Frozen Transforms",
            "count": len(non_frozen),
            "severity": "warning",
            "description": "フリーズされていないトランスフォームが検出されました",
            "items": non_frozen,
            "adjust_function": adjust_non_frozen_transforms
        })

    # Negative Scale
    negative_scale = []
    for transform in transforms:
        try:
            scale = cmds.getAttr(f"{transform}.scale")[0]
            if scale[0] < 0 or scale[1] < 0 or scale[2] < 0:
                negative_scale.append(transform)
        except:
            pass

    if negative_scale:
        results.append({
            "name": "Negative Scale",
            "count": len(negative_scale),
            "severity": "error",
            "description": "負のスケール値が検出されました",
            "items": negative_scale,
            "adjust_function": adjust_negative_scale
        })

    return results


# ========================================
# リグチェック（Motion用）
# ========================================

def check_joint_orientation(check_info):
    """ジョイントの向きをチェック"""
    joints = cmds.ls(type="joint", long=True)
    bad_orientation = []

    for joint in joints:
        try:
            orient = cmds.getAttr(f"{joint}.jointOrient")[0]
            # ジョイントの向きが極端な値でないかチェック
            if abs(orient[0]) > 170 or abs(orient[1]) > 170 or abs(orient[2]) > 170:
                bad_orientation.append(joint)
        except:
            pass

    if bad_orientation:
        return {
            "name": check_info["name"],
            "count": len(bad_orientation),
            "severity": check_info["severity"],
            "description": check_info["description"],
            "items": bad_orientation
        }
    return None


def check_skin_weights(check_info):
    """スキンウェイトの問題をチェック"""
    results = []
    skin_clusters = cmds.ls(type="skinCluster")

    for skin in skin_clusters:
        try:
            # ウェイトが0の頂点を検出
            geometry = cmds.skinCluster(skin, query=True, geometry=True)
            if geometry:
                vertices = cmds.ls(f"{geometry[0]}.vtx[*]", flatten=True)
                zero_weight_verts = []

                for vert in vertices:
                    weights = cmds.skinPercent(skin, vert, query=True, value=True)
                    total_weight = sum(weights)
                    if abs(total_weight) < 0.0001:
                        zero_weight_verts.append(vert)

                if zero_weight_verts:
                    results.append({
                        "name": f"Zero Weight Vertices ({skin})",
                        "count": len(zero_weight_verts),
                        "severity": "error",
                        "description": "ウェイトが0の頂点が検出されました",
                        "items": zero_weight_verts
                    })
        except:
            pass

    return results if results else None


def check_unused_influences(check_info):
    """未使用のインフルエンスをチェック"""
    skin_clusters = cmds.ls(type="skinCluster")
    unused = []

    for skin in skin_clusters:
        try:
            influences = cmds.skinCluster(skin, query=True, influence=True)
            for inf in influences:
                # インフルエンスのウェイト合計が0に近いかチェック
                weight_list = cmds.skinCluster(skin, query=True, weightedInfluence=inf)
                if not weight_list or sum(weight_list) < 0.0001:
                    unused.append(f"{skin} -> {inf}")
        except:
            pass

    if unused:
        return {
            "name": check_info["name"],
            "count": len(unused),
            "severity": check_info["severity"],
            "description": check_info["description"],
            "items": unused,
            "adjust_function": adjust_unused_influences
        }
    return None


def check_animation_keys(check_info):
    """アニメーションキーの問題をチェック"""
    anim_curves = cmds.ls(type="animCurve")
    issues = []

    for curve in anim_curves:
        try:
            # キーの数をチェック
            num_keys = cmds.keyframe(curve, query=True, keyframeCount=True)
            if num_keys == 1:
                issues.append(f"{curve} (キーが1つだけ)")
        except:
            pass

    if issues:
        return {
            "name": check_info["name"],
            "count": len(issues),
            "severity": check_info["severity"],
            "description": check_info["description"],
            "items": issues
        }
    return None


# ========================================
# エフェクトチェック
# ========================================

def check_shader_issues(check_info):
    """シェーダーの問題をチェック（lambert1以外の不要なマテリアルを検出）"""
    shaders = cmds.ls(materials=True)
    issues = []

    for shader in shaders:
        try:
            # lambert1以外のすべてのシェーダーを問題として検出
            if shader != "lambert1":
                issues.append(shader)
        except:
            pass

    if issues:
        return {
            "name": check_info["name"],
            "count": len(issues),
            "severity": check_info.get("severity", "error"),
            "description": "不要なマテリアルが見つかりました（シェーダーは実機側で付与するため）",
            "items": issues
        }
    return None


# ========================================
# SceneCheckerクラス
# ========================================

class SceneChecker:
    """シーンチェッカークラス"""

    def __init__(self):
        self.results = []
        self.cancelled = False

    def run_checks(self, selected_checks, progress_callback=None):
        """選択されたチェックを実行

        Args:
            selected_checks: 選択されたチェック項目のリスト
            progress_callback: プログレス更新用のコールバック関数 (current, total, message) -> bool
                             Falseを返すとキャンセル
        """
        self.results = []
        self.cancelled = False
        total = len(selected_checks)

        for i, check in enumerate(selected_checks):
            # キャンセルチェック
            if self.cancelled:
                break

            # プログレス更新
            if progress_callback:
                check_name = check.get("name", "Unknown")
                if not progress_callback(i + 1, total, f"チェック中: {check_name}"):
                    self.cancelled = True
                    break

            # グローバル関数から取得
            check_function = globals().get(check["function"])
            if check_function and callable(check_function):
                results = check_function(check)
                # 複数の結果を返す場合に対応
                if isinstance(results, list):
                    for result in results:
                        if result and result.get("count", 0) > 0:  # エラーがある場合のみ追加
                            self.results.append(result)
                elif results and results.get("count", 0) > 0:  # エラーがある場合のみ追加
                    self.results.append(results)

        return self.results

    def cancel(self):
        """チェックをキャンセル"""
        self.cancelled = True
