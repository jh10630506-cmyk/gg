import streamlit as st
import random
from typing import Dict, List, Tuple

# ==================== 遊戲配置 ====================
INITIAL_HP = 100
MAX_HP = 100
TREASURE_NEEDED = 3
MONSTER_DAMAGE_RANGE = (15, 25)
TRAP_DAMAGE_RANGE = (10, 20)
EVENT_TRIGGER_PROBABILITY = 0.3
TREASURE_FIND_PROBABILITY = 0.15

# ==================== 毒舌助手評論 ====================
TOXIC_COMMENTS = {
    "safe": [
        "又是膽小的選擇啊，真是太刺激了…不是。",
        "保險起見？我就喜歡看你這種「聰明」的表現。",
    ],
    "dangerous": [
        "好啊，自尋死路的勇氣我欣賞，去吧勇士。",
        "玩命啊？這才是我欣賞的蠢。",
    ],
    "treasure": [
        "運氣不錯呢，但別以為自己能逃脫。",
        "發現寶箱？哈，這也算幸運嗎？",
    ],
    "monster": [
        "怪物出現了，你跑不了的。",
        "看來今天是你的死期。",
    ],
    "trap": [
        "陷阱？你沒看到嗎？太慣用了。",
        "又中招了，真是一個接一個。",
    ],
    "safe_pass": [
        "居然活著走出來了，我有點失望。",
        "運氣不錯，下次沒那麼好運。",
    ],
}

# ==================== 場景定義 ====================
SCENES = {
    "entrance": {
        "title": "🏛️ 恐怖實驗室入口",
        "description": "你站在一個破舊的實驗室門前。冰冷的風吹過，傳來詭異的聲音。門內漆黑一片，但你可以看到一些詭異的光影。",
        "options": [
            {"text": "謹慎地進入實驗室 (安全)", "action": "enter_safe", "risk": "low"},
            {"text": "直直向前衝入黑暗 (危險)", "action": "enter_danger", "risk": "high"},
        ]
    },
    "corridor": {
        "title": "🚪 昏暗走廊",
        "description": "你走進了一條長長的走廊，兩側是生鏽的金屬牆。走廊深處隱約傳來奇怪的聲音。",
        "options": [
            {"text": "向前探索 (冒險)", "action": "explore", "risk": "high"},
            {"text": "返回入口 (安全)", "action": "return_entrance", "risk": "low"},
            {"text": "尋找側道 (探索)", "action": "find_side_path", "risk": "medium"},
        ]
    },
    "lab": {
        "title": "🔬 陰暗實驗室",
        "description": "實驗室裡到處是廢棄的儀器和生物罐。某些容器裡還閃爍著詭異的綠光。一股刺鼻的味道撲面而來。",
        "options": [
            {"text": "檢查容器 (危險)", "action": "check_containers", "risk": "high"},
            {"text": "前往深處 (很危險)", "action": "go_deeper", "risk": "very_high"},
            {"text": "後退到走廊 (安全)", "action": "retreat", "risk": "low"},
        ]
    },
    "treasure_room": {
        "title": "💎 寶藏室",
        "description": "你發現了一個隱藏的房間！牆上掛著發光的寶箱，散發著神秘的光芒。",
        "options": [
            {"text": "打開寶箱 (獲得寶藏)", "action": "open_treasure", "risk": "low"},
            {"text": "小心翼翼地檢查 (謹慎)", "action": "careful_treasure", "risk": "low"},
        ]
    },
    "exit": {
        "title": "🚪 逃生出口",
        "description": "你找到了出口！門的另一邊是自由。",
        "options": [
            {"text": "推開門逃脫！", "action": "escape", "risk": "none"},
        ]
    },
}

# ==================== 初始化 Session State ====================
def initialize_game():
    """初始化遊戲狀態"""
    st.session_state.initialized = True
    st.session_state.current_scene = "entrance"
    st.session_state.hp = INITIAL_HP
    st.session_state.max_hp = MAX_HP
    st.session_state.score = 0
    st.session_state.inventory = []
    st.session_state.encounters = 0
    st.session_state.visited_scenes = set()
    st.session_state.game_over = False
    st.session_state.game_won = False
    st.session_state.last_event = ""
    st.session_state.toxic_comment = ""

# ==================== 隨機事件系統 ====================
def trigger_random_event() -> str:
    """觸發隨機事件，返回事件描述"""
    if random.random() > EVENT_TRIGGER_PROBABILITY:
        return ""
    
    event_type = random.choice(["monster", "trap", "treasure", "safe"])
    
    if event_type == "monster":
        damage = random.randint(*MONSTER_DAMAGE_RANGE)
        st.session_state.hp -= damage
        st.session_state.toxic_comment = random.choice(TOXIC_COMMENTS["monster"])
        return f"💀 怪物出現！你受到 {damage} 傷害！"
    
    elif event_type == "trap":
        damage = random.randint(*TRAP_DAMAGE_RANGE)
        st.session_state.hp -= damage
        st.session_state.toxic_comment = random.choice(TOXIC_COMMENTS["trap"])
        return f"⚠️ 陷阱觸發！你受到 {damage} 傷害！"
    
    elif event_type == "treasure":
        if random.random() < TREASURE_FIND_PROBABILITY:
            st.session_state.inventory.append("寶箱")
            st.session_state.score += 20
            st.session_state.toxic_comment = random.choice(TOXIC_COMMENTS["treasure"])
            return f"✨ 你發現了寶箱！（已收集：{len(st.session_state.inventory)}/{TREASURE_NEEDED}）"
    
    else:  # safe
        st.session_state.score += 5
        st.session_state.toxic_comment = random.choice(TOXIC_COMMENTS["safe_pass"])
        return "✅ 你安全地通過了這一區域。+5 分！"
    
    return ""

# ==================== 動作處理系統 ====================
def handle_action(action: str) -> str:
    """處理玩家動作"""
    event_result = trigger_random_event()
    
    if action == "enter_safe":
        st.session_state.current_scene = "corridor"
        st.session_state.toxic_comment = random.choice(TOXIC_COMMENTS["safe"])
        return "你謹慎地進入了實驗室，踏入了一條昏暗的走廊。"
    
    elif action == "enter_danger":
        damage = random.randint(10, 15)
        st.session_state.hp -= damage
        st.session_state.toxic_comment = random.choice(TOXIC_COMMENTS["dangerous"])
        st.session_state.current_scene = "lab"
        return f"你衝進黑暗中，被什麼東西撞上了！受到 {damage} 傷害！"
    
    elif action == "explore":
        st.session_state.current_scene = "lab"
        return "你向前探索走廊，發現了一扇門。推開後，映入眼簾的是一個陰暗的實驗室。"
    
    elif action == "return_entrance":
        st.session_state.current_scene = "entrance"
        st.session_state.toxic_comment = "膽小如鼠啊。"
        return "你返回了入口。"
    
    elif action == "find_side_path":
        if random.random() < 0.5:
            st.session_state.current_scene = "treasure_room"
            st.session_state.toxic_comment = "運氣還不錯呢。"
            return "你發現了一條隱藏的側道，通往一個神秘的房間！"
        else:
            damage = random.randint(5, 10)
            st.session_state.hp -= damage
            st.session_state.toxic_comment = "這是什麼倒霉的日子。"
            st.session_state.current_scene = "corridor"
            return f"你走進側道，觸發了一個陷阱！受到 {damage} 傷害！"
    
    elif action == "check_containers":
        if random.random() < 0.6:
            damage = random.randint(20, 30)
            st.session_state.hp -= damage
            st.session_state.toxic_comment = random.choice(TOXIC_COMMENTS["monster"])
            return f"容器裡跳出了怪物！你受到 {damage} 傷害！"
        else:
            st.session_state.score += 10
            return "你發現了一些有用的物品。+10 分！"
    
    elif action == "go_deeper":
        if random.random() < 0.7:
            damage = random.randint(25, 35)
            st.session_state.hp -= damage
            st.session_state.toxic_comment = "看來你真的活膩了。"
            return f"深處傳來可怕的聲音，你被猛烈襲擊！受到 {damage} 傷害！"
        else:
            st.session_state.inventory.append("寶箱")
            st.session_state.score += 30
            st.session_state.toxic_comment = "運氣真不錯啊。"
            return f"你找到了一個寶箱！（已收集：{len(st.session_state.inventory)}/{TREASURE_NEEDED}）"
    
    elif action == "retreat":
        st.session_state.current_scene = "corridor"
        return "你決定暫時撤退到走廊。"
    
    elif action == "open_treasure":
        st.session_state.inventory.append("寶箱")
        st.session_state.score += 25
        st.session_state.toxic_comment = random.choice(TOXIC_COMMENTS["treasure"])
        return f"你打開了寶箱，獲得了寶藏！（已收集：{len(st.session_state.inventory)}/{TREASURE_NEEDED}）"
    
    elif action == "careful_treasure":
        if random.random() < 0.8:
            st.session_state.inventory.append("寶箱")
            st.session_state.score += 25
            st.session_state.toxic_comment = "謹慎還是有用的嘛。"
            return f"你小心地取出了寶箱。（已收集：{len(st.session_state.inventory)}/{TREASURE_NEEDED}）"
        else:
            damage = random.randint(10, 15)
            st.session_state.hp -= damage
            st.session_state.toxic_comment = "謹慎個鬼啊！"
            return f"陷阱！你受到 {damage} 傷害！"
    
    elif action == "escape":
        st.session_state.game_won = True
        st.session_state.toxic_comment = "不錯不錯，活著出去了。"
        return "你推開門，逃脫了恐怖實驗室！🎉"
    
    return event_result if event_result else "你還活著…暫時。"

# ==================== 主遊戲邏輯 ====================
def render_game():
    """渲染遊戲主界面"""
    # 設置頁面
    st.set_page_config(
        page_title="恐怖實驗室冒險",
        page_icon="🔬",
        layout="wide"
    )
    
    # 添加 CSS 主題
    st.markdown("""
    <style>
    .stApp {
        background-color: #1a0000;
        color: #e0e0e0;
    }
    .main {
        background-color: #1a0000;
    }
    h1, h2, h3 {
        color: #ff6b6b;
    }
    .stButton>button {
        background-color: #8b0000;
        color: #e0e0e0;
        border: 2px solid #551a1a;
        border-radius: 5px;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #ff0000;
        color: #000;
    }
    .health-bar {
        background-color: #1a1a1a;
        border: 2px solid #551a1a;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 初始化遊戲
    if not st.session_state.get("initialized", False):
        initialize_game()
    
    # 遊戲標題
    st.title("🔬 恐怖實驗室冒險 💀")
    
    # 遊戲狀態顯示
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        hp_percentage = (st.session_state.hp / st.session_state.max_hp) * 100
        if hp_percentage > 50:
            color = "green"
        elif hp_percentage > 25:
            color = "orange"
        else:
            color = "red"
        st.metric("❤️ 生命值", f"{st.session_state.hp}/{st.session_state.max_hp}", 
                 delta=f"{hp_percentage:.0f}%", delta_color="inverse")
    
    with col2:
        st.metric("⭐ 分數", st.session_state.score)
    
    with col3:
        treasure_count = len(st.session_state.inventory)
        st.metric("💎 寶箱", f"{treasure_count}/{TREASURE_NEEDED}")
    
    with col4:
        st.metric("🏆 遭遇", st.session_state.encounters)
    
    st.divider()
    
    # 檢查勝敗條件
    if st.session_state.hp <= 0:
        st.session_state.game_over = True
    
    if len(st.session_state.inventory) >= TREASURE_NEEDED and st.session_state.current_scene == "exit":
        st.session_state.game_won = True
    
    # 遊戲結束顯示
    if st.session_state.game_won:
        st.success("🎉 恭喜你逃脫了恐怖實驗室！！！", icon="✅")
        st.balloons()
        st.subheader(f"最終分數：{st.session_state.score} 分")
        if st.button("🔄 重新開始", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        return
    
    if st.session_state.game_over:
        st.error("💀 你死了！恐怖實驗室吞噬了你！", icon="❌")
        st.subheader(f"最終分數：{st.session_state.score} 分")
        if st.button("🔄 重新開始", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        return
    
    # 檢查是否需要逃生
    if len(st.session_state.inventory) >= TREASURE_NEEDED and st.session_state.current_scene != "exit":
        st.info(f"✨ 你已經收集了 {TREASURE_NEEDED} 個寶箱！現在你需要找到逃生出口。")
        # 隨機導向到出口
        if st.button("🎯 尋找逃生出口", use_container_width=True):
            st.session_state.current_scene = "exit"
            st.rerun()
        st.divider()
    
    # 顯示當前場景
    scene = SCENES[st.session_state.current_scene]
    st.subheader(scene["title"])
    st.write(scene["description"])
    
    # 毒舌評論顯示
    if st.session_state.toxic_comment:
        st.warning(f"😈 毒舌助手：「{st.session_state.toxic_comment}」", icon="👿")
    
    # 上一次動作結果
    if st.session_state.last_event:
        st.info(st.session_state.last_event)
    
    st.divider()
    
    # 顯示選項
    st.subheader("選擇你的下一步行動：")
    for i, option in enumerate(scene["options"]):
        if st.button(option["text"], key=f"btn_{i}", use_container_width=True):
            st.session_state.encounters += 1
            result = handle_action(option["action"])
            st.session_state.last_event = result
            st.session_state.toxic_comment = st.session_state.toxic_comment or random.choice(TOXIC_COMMENTS["safe"])
            st.rerun()
    
    # 遊戲狀態調試信息（可選）
    with st.expander("🔍 調試信息"):
        st.write(f"當前場景：{st.session_state.current_scene}")
        st.write(f"背包：{st.session_state.inventory}")
        st.write(f"已訪問場景：{st.session_state.visited_scenes}")

# ==================== 主程序 ====================
if __name__ == "__main__":
    render_game()
