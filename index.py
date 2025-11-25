import streamlit as st

# ページ設定
st.set_page_config(page_title="Manga Prompt Generator", layout="wide")

st.title("漫画プロンプト作成補助ツールVer.1")
st.markdown("nanobananaの漫画プロンプトをYamlで作るとき、コードが長くて一つ一つ目で見ていくのが大変だったからフォーム化してみたよ。")
st.markdown("Pythonの勉強はじめたばかりだから細かい部分はこれから直していくかも。")
st.markdown("使い方/n画面左の★基礎設定で希望のものを選択→①キャラクター登録→② パネル(コマ)作成→③ プロンプト生成　の順で入力")

# --- セッション状態の初期化 ---
if "character_infos" not in st.session_state:
    st.session_state.character_infos = []
if "panels" not in st.session_state:
    st.session_state.panels = []

# --- サイドバー：基礎設定 ---
st.sidebar.header("★基礎設定")

# 言語設定
lang_input = st.sidebar.radio(
    "Language (言語)",
    options=["日本語", "英語"],
    horizontal=True
)
language_val = "Japanese" if lang_input == "日本語" else "English"

# カラーモード設定
color_mode_val = st.sidebar.radio(
    "Color Mode",
    options=["白黒", "グレー", "カラー"],
    horizontal=True
)

# 固定設定（表示のみ）
st.sidebar.markdown("---")
st.sidebar.markdown("**固定設定**")
st.sidebar.info("""
- Style: japanese syonen manga
- Writing-mode: vertical-rl
- Aspect Ratio: 1:1.41
""")

# 固定テキストブロック
INSTRUCTIONS_BLOCK = """このYAMLは漫画ページの仕様です。添付の画像データ（キャラクター等、コマ割り画像）がある場合は、
それらを外見の基準として忠実に反映し、このプロンプトの指示に従ってページを生成してください。"""

LAYOUT_CONSTRAINTS_BLOCK = """指示: 以下のレイアウト制約を厳守して画像を生成してください。
- ページ全体のアスペクト比は 1:1.4（幅:高さ）を絶対に厳守する。
- パネルの追加・削除・結合・回転・順序入替えは禁止。
- 各パネルの内容は必ず枠内に収める。
- 読み順は panel.number の昇順。
- writing-mode が vertical-rl の場合、同一パネル内で会話があるときは「先に読ませたいセリフのキャラクターほど右側に配置する」こと。"""

# --- ヘルパー関数: 手動YAML生成 ---
def make_yaml_text(data_dict):
    """
    辞書データをYAML形式の文字列に変換する簡易関数
    """
    lines = []
    
    def add_line(text, indent=0):
        lines.append("  " * indent + text)

    # comic_page
    add_line("comic_page :", 0)
    cp = data_dict["comic_page"]
    
    # 基本プロパティ
    add_line(f'language : "{cp["language"]}"', 1)
    add_line(f'style : "{cp["style"]}"', 1)
    add_line(f'writing-mode : "{cp["writing-mode"]}"', 1)
    add_line(f'color_mode : "{cp["color_mode"]}"', 1)
    add_line(f'aspect_ratio : "{cp["aspect_ratio"]}"', 1)
    
    # 長文ブロック
    add_line("instructions : |-", 1)
    for l in cp["instructions"].split("\n"):
        add_line(l, 2)
        
    add_line("layout_constraints : |-", 1)
    for l in cp["layout_constraints"].split("\n"):
        add_line(l, 2)

    # Character Infos
    if cp["character_infos"]:
        add_line("character_infos :", 1)
        for char in cp["character_infos"]:
            add_line(f'- name : "{char["name"]}"', 2)
            add_line(f'  base_prompt : "{char["base_prompt"]}"', 2)
            add_line("", 0)

    # Panels
    if cp["panels"]:
        add_line("panels :", 1)
        for panel in cp["panels"]:
            add_line(f'- number : {panel["number"]}', 2)
            add_line(f'  page_position : "{panel["page_position"]}"', 2)
            add_line(f'  background : "{panel["background"]}"', 2)
            add_line(f'  description : "{panel["description"]}"', 2)
            
            # Objects
            if panel["objects"]:
                add_line("  objects :", 2)
                for obj in panel["objects"]:
                    add_line(f'- name : "{obj["name"]}"', 3)
            else:
                add_line("  objects : []", 2)

            # Characters in panel
            if panel["characters"]:
                add_line("  characters :", 2)
                for p_char in panel["characters"]:
                    # nameが空文字の場合でも出力する
                    add_line(f'- name : "{p_char["name"]}"', 3)
                    add_line(f'  panel_position : "{p_char["panel_position"]}"', 3)
                    add_line(f'  emotion : "{p_char.get("emotion", "")}"', 3)
                    add_line(f'  facing : "{p_char["facing"]}"', 3)
                    add_line(f'  shot : "{p_char["shot"]}"', 3)
                    add_line(f'  pose : "{p_char.get("pose", "")}"', 3)
                    
                    # Lines
                    if p_char["lines"]:
                        add_line("  lines :", 3)
                        for line in p_char["lines"]:
                            add_line(f'- text : "{line["text"]}"', 4)
                            add_line(f'  char_text_position : "{line["char_text_position"]}"', 4)
                            add_line(f'  type : "{line["type"]}"', 4)
                    else:
                        add_line("  lines : []", 3)
            else:
                add_line("  characters : []", 2)
            
            # Effects
            add_line("  effects : []", 2)

            # Monologues
            if panel["monologues"]:
                add_line("  monologues :", 2)
                for mono in panel["monologues"]:
                    add_line(f'- text : "{mono["text"]}"', 3)
                    add_line(f'  text_position : "{mono["text_position"]}"', 3)
                    add_line(f'  balloon_shape : "{mono["balloon_shape"]}"', 3)
            else:
                add_line("  monologues : []", 2)
            
            add_line(f'  camera_angle : "{panel["camera_angle"]}"', 2)
            add_line("", 0)

    return "\n".join(lines)

# --- メインエリア ---

tab1, tab2, tab3 = st.tabs(["① キャラクター登録", "② パネル(コマ)作成", "③ プロンプト生成"])

# === タブ1: キャラクター登録 ===
with tab1:
    st.header("登場キャラクターの登録")
    with st.form("add_char_form", clear_on_submit=True):
        c_name = st.text_input("キャラクター名 (name)", placeholder="例: aichan")
        st.markdown("※登場させるキャラクターの画像を参照させる場合、画像の名前とこのキャラ名を一致させるとよきです。")
        c_prompt = st.text_area("外見プロンプト (base_prompt)", placeholder="例: 1girl, solo, she has gold long hair, ...")
        submitted = st.form_submit_button("キャラクターを追加")
        if submitted and c_name:
            st.session_state.character_infos.append({
                "name": c_name,
                "base_prompt": c_prompt
            })
            st.success(f"{c_name} を追加しました")

    if st.session_state.character_infos:
        st.markdown("### 登録済みキャラクター")
        for i, char in enumerate(st.session_state.character_infos):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"{char['name']} : {char['base_prompt']}")
            with col2:
                if st.button("削除", key=f"del_char_{i}"):
                    st.session_state.character_infos.pop(i)
                    st.rerun()

# === タブ2: パネル作成 ===
with tab2:
    st.header("コマ(Panel)の構成")
    
    with st.expander("新しいコマを作成する", expanded=True):
        p_num = len(st.session_state.panels) + 1
        
        # --- コマの基本設定 ---
        st.subheader("1. コマの基本設定")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            p_pos = st.selectbox("ページ内でのコマの位置", ["top", "middle", "bottom", "top-right", "top-left", "bottom-right", "bottom-left"], key="new_p_pos")
            p_bg = st.text_area("背景", placeholder="例: 暗い部屋に煌々と光るPCの画面", key="new_p_bg")
        with col_p2:
            p_cam = st.text_input("カメラアングル", placeholder="例: from side, front", key="new_p_cam")
            p_desc = st.text_input("コマが表してる状況を書いておく", placeholder="例: ナノバナナProが世間を賑わしている", key="new_p_desc")
        
        p_obj_str = st.text_input("登場させたいモノ (カンマ区切り)", placeholder="例: モニター, スマホ, ベッド", key="new_p_obj")

        st.markdown("---")
        
        # --- キャラクター・セリフ設定 ---
        st.subheader("2. キャラクターとセリフの追加")
        
        if "temp_panel_chars" not in st.session_state:
            st.session_state.temp_panel_chars = []

        reg_char_names = [c["name"] for c in st.session_state.character_infos]
        
        # 入力フォーム
        with st.container():
            # 話者（キャラクター）選択
            tp_name = st.selectbox("話者選択（空白なら名前なし）", [""] + reg_char_names, key="tp_name")
            
            # --- セリフ設定エリア ---
            col_l1, col_l2 = st.columns([3, 1])
            with col_l1:
                tp_line = st.text_input("セリフ内容", placeholder="例：なのばなな…ぷろ？", key="tp_line")
            with col_l2:
                # 【改善点①】吹き出し位置の選択
                tp_text_pos = st.selectbox("吹き出し位置", ["right", "center", "left"], index=0, key="tp_text_pos")

            # --- 外見設定エリア（トグルで見やすく） ---
            st.caption("▼ 外見設定（「キャラ＋セリフを追加」ボタンを押したときのみ反映されます）")
            col_v1, col_v2, col_v3 = st.columns(3)
            with col_v1:
                tp_pos = st.selectbox("立ち位置", ["center", "left", "right"], key="tp_pos")
            with col_v2:
                tp_shot = st.selectbox("ショット", ["バストアップ", "顔のアップ", "全身", "ニーアップ"], key="tp_shot")
            with col_v3:
                tp_face = st.text_input("表情/向き", placeholder="PCを見ている", key="tp_face")

            # --- 追加ボタンエリア ---
            # 【改善点②】追加ボタンを2つに分離
            col_btn1, col_btn2 = st.columns(2)
            
            # ボタンA: キャラとセリフ両方追加
            if col_btn1.button("👤 キャラ＋セリフを追加"):
                st.session_state.temp_panel_chars.append({
                    "name": tp_name,
                    "panel_position": tp_pos,
                    "shot": tp_shot,
                    "facing": tp_face,
                    "pose": "",
                    "lines": [{"text": tp_line, "char_text_position": tp_text_pos, "type": "speech"}] if tp_line else []
                })

            # ボタンB: セリフのみ追加（吹き出しのみ）
            if col_btn2.button("💬 セリフ(吹き出し)のみ追加"):
                # 外見データを空文字にして追加
                st.session_state.temp_panel_chars.append({
                    "name": tp_name, # 名前は紐づける（誰のセリフか）
                    "panel_position": "",
                    "shot": "",
                    "facing": "",
                    "pose": "",
                    "lines": [{"text": tp_line, "char_text_position": tp_text_pos, "type": "speech"}]
                })

            # --- 追加済みリスト表示 ---
            if st.session_state.temp_panel_chars:
                st.info("このコマに追加される要素:")
                for idx, tc in enumerate(st.session_state.temp_panel_chars):
                    # 表示用にわかりやすく整形
                    disp_name = tc['name'] if tc['name'] else "（名前なし）"
                    if tc['panel_position']:
                        type_label = "【キャラ＋セリフ】"
                        detail = f"{tc['shot']} / {tc['facing']}"
                    else:
                        type_label = "【吹き出しのみ】"
                        detail = "外見指定なし"
                    
                    line_text = tc['lines'][0]['text'] if tc['lines'] else "（セリフなし）"
                    line_pos = tc['lines'][0]['char_text_position'] if tc['lines'] else "-"
                    
                    st.text(f"{idx+1}. {type_label} {disp_name}: 「{line_text}」 (位置:{line_pos})")
                
                if st.button("追加リストをクリア"):
                    st.session_state.temp_panel_chars = []

        st.markdown("---")
        
        # --- モノローグ ---
        st.subheader("3. その他 (モノローグ)")
        p_mono = st.text_input("モノローグ内容", placeholder="例: 早すぎて追いつかない", key="new_p_mono")
        
        # --- 決定ボタン ---
        if st.button("この内容でコマを確定・追加", type="primary"):
            objects_list = [{"name": x.strip()} for x in p_obj_str.split(",")] if p_obj_str else []
            monologues_list = []
            if p_mono:
                monologues_list.append({
                    "text": p_mono,
                    "text_position": "top-left",
                    "balloon_shape": "長方形"
                })

            new_panel = {
                "number": p_num,
                "page_position": p_pos,
                "background": p_bg,
                "description": p_desc,
                "objects": objects_list,
                "characters": st.session_state.temp_panel_chars, # リストをそのままコピー
                "effects": [],
                "monologues": monologues_list,
                "camera_angle": p_cam
            }
            
            st.session_state.panels.append(new_panel)
            st.session_state.temp_panel_chars = [] # リセット
            st.success(f"Panel {p_num} を追加しました！")
            st.rerun()

    # 登録済みパネル一覧
    st.markdown("### 作成済みパネル一覧")
    for i, p in enumerate(st.session_state.panels):
        with st.expander(f"Panel {p['number']}: {p['description']}"):
            st.text(f"位置: {p['page_position']}")
            st.text(f"背景: {p['background']}")
            # キャラ内容の簡易表示
            if p['characters']:
                st.caption("含まれるキャラ/セリフ:")
                for c in p['characters']:
                    l = c['lines'][0]['text'] if c['lines'] else ""
                    st.text(f"- {c['name']}: {l}")
            
            if st.button("このパネルを削除", key=f"del_panel_{i}"):
                st.session_state.panels.pop(i)
                for idx, panel in enumerate(st.session_state.panels):
                    panel['number'] = idx + 1
                st.rerun()

# === タブ3: 生成 ===
with tab3:
    st.header("プロンプト生成結果")
    
    if st.button("YAMLを生成する"):
        output_data = {
            "comic_page": {
                "language": language_val,
                "style": "japanese syonen manga",
                "writing-mode": "vertical-rl",
                "color_mode": color_mode_val,
                "aspect_ratio": "1:1.41",
                "instructions": INSTRUCTIONS_BLOCK,
                "layout_constraints": LAYOUT_CONSTRAINTS_BLOCK,
                "character_infos": st.session_state.character_infos,
                "panels": st.session_state.panels
            }
        }
        
        yaml_str = make_yaml_text(output_data)
        st.code(yaml_str, language="yaml")
        st.info("右上のコピーボタンからコピーして使用してください。")
