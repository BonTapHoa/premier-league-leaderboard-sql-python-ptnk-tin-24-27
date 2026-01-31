import streamlit as st
import pandas as pd
import sqlite3
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Premier League Manager",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
    return df


def get_matches_by_round(game_round):
    conn = get_connection()
    query = "SELECT Home, Away, Homescore, Awayscore FROM Schedule WHERE Game = ?"
    df = pd.read_sql(query, conn, params=(game_round,))
    conn.close()
    return df


def update_match_score(game_round, home, away, home_score, away_score):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE Schedule SET Homescore = ?, Awayscore = ?
            WHERE Game = ? AND Home = ? AND Away = ?
        """,
            (home_score, away_score, game_round, home, away),
        )
        if cursor.rowcount == 0:
            return False, "⚠️ Không tìm thấy trận đấu!"
        conn.commit()
        return True, "✅ Đã cập nhật tỉ số!"
    except sqlite3.Error as e:
        return False, f"❌ Lỗi: {e}"
    finally:
        conn.close()


def get_team_history_data(team_name):
    conn = get_connection()
    query = """
        SELECT Game, Home, Homescore, Awayscore, Away 
        FROM Schedule 
        WHERE Home = ? OR Away = ?
        ORDER BY Game ASC
    """
    df = pd.read_sql(query, conn, params=(team_name, team_name))
    conn.close()

    played = df[df["Homescore"].notna()].copy()
    upcoming = df[df["Homescore"].isna()].copy()

    upcoming_next_4 = upcoming.head(4)
    final_df = pd.concat([played, upcoming_next_4])

    return final_df


def style_history_dataframe(df, target_team):
    processed_rows = []

    for _, row in df.iterrows():
        game = row["Game"]
        home = row["Home"]
        away = row["Away"]
        h_score = row["Homescore"]
        a_score = row["Awayscore"]

        opponent = away if home == target_team else home
        venue = "Sân Nhà" if home == target_team else "Sân Khách"

        result_icon = "📅"
        result_text = "Sắp đá"
        score_display = "- : -"

        if pd.notna(h_score):
            score_display = f"{int(h_score)} - {int(a_score)}"

            if home == target_team:
                if h_score > a_score:
                    result_icon = "✅ WIN"
                elif h_score == a_score:
                    result_icon = "⚪ DRAW"
                else:
                    result_icon = "❌ LOSS"
            else:
                if a_score > h_score:
                    result_icon = "✅ WIN"
                elif a_score == h_score:
                    result_icon = "⚪ DRAW"
                else:
                    result_icon = "❌ LOSS"

            result_text = result_icon

        processed_rows.append(
            {
                "Vòng": game,
                "Đối thủ": opponent,
                "Sân": venue,
                "Tỉ số": score_display,
                "Kết quả": result_text,
            }
        )

    return pd.DataFrame(processed_rows)


def show_team_page(team_name):
    if st.button("⬅️ Quay lại Bảng Xếp Hạng"):
        st.query_params.clear()
        st.rerun()

    col1, col2 = st.columns([1, 6])
    with col1:
        img_path = f"{ASSETS_DIR}/{team_name}.png"
        if os.path.exists(img_path):
            st.image(img_path, width=100)
    with col2:
        st.title(f"Lịch sử thi đấu: {team_name}")
        st.caption("Hiển thị các trận đã đấu và 4 vòng tiếp theo")

    raw_df = get_team_history_data(team_name)
    display_df = style_history_dataframe(raw_df, team_name)

    def highlight_rows(row):
        result = row["Kết quả"]

        color = "transparent"

        if "WIN" in result:
            color = "rgba(144, 238, 144, 0.3)"
        elif "DRAW" in result:
            color = "rgba(211, 211, 211, 0.3)"
        elif "LOSS" in result:
            color = "rgba(255, 182, 193, 0.3)"

        return [f"background-color: {color}"] * len(row)

    styler = display_df.style.apply(highlight_rows, axis=1)

    st.dataframe(
        styler,
        column_config={
            "Vòng": st.column_config.NumberColumn("Vòng", width="small"),
            "Kết quả": st.column_config.TextColumn("Phong độ", width="medium"),
        },
        use_container_width=True,
        hide_index=True,
        height=600,
    )


def show_main_page():
    st.title("⚽ Premier League Manager")

    tab1, tab2 = st.tabs(["🏆 Bảng Xếp Hạng", "📝 Cập Nhật Tỉ Số"])

    with tab1:
        st.info("💡 Mẹo: Bấm vào hàng của một đội để xem lịch sử đấu chi tiết.")

        df = load_leaderboard()
        event = st.dataframe(
            df,
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
            on_select="rerun",
            selection_mode="single-row",
        )

        if len(event.selection.rows) > 0:
            selected_row_index = event.selection.rows[0]
            selected_team = df.iloc[selected_row_index]["Team"]

            st.query_params["team"] = selected_team
            st.rerun()

    with tab2:
        st.header("Nhập kết quả thi đấu")
        selected_round = st.number_input(
            "Chọn Vòng Đấu (1-38)", min_value=1, max_value=38, value=1
        )
        matches_df = get_matches_by_round(selected_round)

        if not matches_df.empty:
            match_options = []
            for index, row in matches_df.iterrows():
                status = (
                    "Chưa đá"
                    if pd.isna(row["Homescore"])
                    else f"{int(row['Homescore'])} - {int(row['Awayscore'])}"
                )
                label = f"{row['Home']} vs {row['Away']} | [{status}]"
                match_options.append(label)

            selected_match_label = st.selectbox(
                "Chọn trận đấu cần nhập:", match_options
            )
            team_part = selected_match_label.split(" | ")[0]
            home_team, away_team = team_part.split(" vs ")

            st.write(f"Trận: **{home_team}** vs **{away_team}**")
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
            st.warning("Không tìm thấy dữ liệu.")


query_params = st.query_params

if "team" in query_params:
    target_team = query_params["team"]
    show_team_page(target_team)
else:
    show_main_page()
