import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Premier League Manager", page_icon="⚽", layout="wide")

DB_FILE = "football.db"
ASSETS_DIR = "assets"


def get_connection():
    return sqlite3.connect(DB_FILE)


def load_leaderboard():
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM LeaderBoard ORDER BY Pts DESC, Dif DESC, G DESC", conn
    )
    conn.close()
    df["Logo"] = df["Team"].apply(
        lambda x: (
            f"{ASSETS_DIR}/{x}.png" if os.path.exists(f"{ASSETS_DIR}/{x}.png") else None
        )
    )
    return df[["Logo"] + [c for c in df.columns if c != "Logo"]]


def get_matches_by_round(game_round):
    conn = get_connection()
    # Lấy danh sách trận đấu trong vòng, kèm tỉ số hiện tại (nếu có)
    query = """
        SELECT Home, Away, Homescore, Awayscore 
        FROM Schedule 
        WHERE Game = ?
    """
    df = pd.read_sql(query, conn, params=(game_round,))
    conn.close()
    return df


def update_match_score(game_round, home, away, home_score, away_score):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # CHỈ UPDATE, KHÔNG INSERT
        cursor.execute(
            """
            UPDATE Schedule 
            SET Homescore = ?, Awayscore = ?
            WHERE Game = ? AND Home = ? AND Away = ?
        """,
            (home_score, away_score, game_round, home, away),
        )

        if cursor.rowcount == 0:
            return False, "⚠️ Không tìm thấy trận đấu này!"

        conn.commit()
        return True, "✅ Đã cập nhật tỉ số thành công!"
    except sqlite3.Error as e:
        return False, f"❌ Lỗi Database: {e}"
    finally:
        conn.close()


# --- UI ---
st.title("⚽ Premier League Manager")

tab1, tab2 = st.tabs(["🏆 Bảng Xếp Hạng", "📝 Cập Nhật Tỉ Số"])

# TAB 1: BẢNG XẾP HẠNG
with tab1:
    st.dataframe(
        load_leaderboard(),
        column_config={
            "Logo": st.column_config.ImageColumn("Logo", width="small"),
            "Pts": st.column_config.ProgressColumn(
                "Điểm", format="%d", min_value=0, max_value=114
            ),
            "Dif": st.column_config.NumberColumn("Hiệu số", format="%+d"),
        },
        use_container_width=True,
        hide_index=True,
        height=800,
    )

# TAB 2: CẬP NHẬT TỈ SỐ (Logic Mới)
with tab2:
    st.header("Nhập kết quả thi đấu")

    # Bước 1: Chọn vòng đấu
    selected_round = st.number_input(
        "Chọn Vòng Đấu (1-38)", min_value=1, max_value=38, value=1
    )

    # Bước 2: Lấy danh sách trận trong vòng đó
    matches_df = get_matches_by_round(selected_round)

    if not matches_df.empty:
        # Tạo danh sách hiển thị dễ đọc cho Selectbox
        # Format: "Arsenal vs Wolves (Chưa đá)" hoặc "Arsenal vs Wolves (3 - 0)"
        match_options = []
        for index, row in matches_df.iterrows():
            status = (
                "Chưa đá"
                if pd.isna(row["Homescore"])
                else f"{int(row['Homescore'])} - {int(row['Awayscore'])}"
            )
            label = f"{row['Home']} vs {row['Away']} | [{status}]"
            match_options.append(label)

        selected_match_label = st.selectbox("Chọn trận đấu cần nhập:", match_options)

        # Parse lại tên đội từ label user chọn
        # Label format: "Home vs Away | ..." -> Tách chuỗi để lấy tên đội
        team_part = selected_match_label.split(" | ")[0]
        home_team, away_team = team_part.split(" vs ")

        st.write(f"Đang nhập tỉ số cho: **{home_team}** vs **{away_team}**")

        c1, c2 = st.columns(2)
        with c1:
            s_home = st.number_input(f"Bàn thắng {home_team}", min_value=0, step=1)
        with c2:
            s_away = st.number_input(f"Bàn thắng {away_team}", min_value=0, step=1)

        if st.button("Lưu Tỉ Số", type="primary"):
            success, msg = update_match_score(
                selected_round, home_team, away_team, s_home, s_away
            )
            if success:
                st.success(msg)
                st.balloons()
            else:
                st.error(msg)
    else:
        st.warning("Không tìm thấy dữ liệu lịch thi đấu cho vòng này.")
