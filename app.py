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


def get_full_schedule_view():
    conn = get_connection()
    query = (
        "SELECT Game, Home, Homescore, Awayscore, Away FROM Schedule ORDER BY Game DESC"
    )
    df = pd.read_sql(query, conn)
    conn.close()

    played_matches = df[df["Homescore"].notna()]

    if not played_matches.empty:
        current_round = played_matches["Game"].max()
    else:
        current_round = 0

    view_limit = current_round + 1

    final_df = df[df["Game"] <= view_limit].copy()

    def format_score(row):
        if pd.isna(row["Homescore"]):
            return "Sắp đá"
        return f"{int(row['Homescore'])} - {int(row['Awayscore'])}"

    final_df["Tỉ số"] = final_df.apply(format_score, axis=1)

    return final_df[["Game", "Home", "Tỉ số", "Away"]]


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


def get_recent_form(team_name):
    conn = get_connection()
    query = """
        SELECT Home, Homescore, Awayscore, Away
        FROM Schedule
        WHERE (Home = ? OR Away = ?) AND Homescore IS NOT NULL
        ORDER BY Game DESC
        LIMIT 5
    """
    df = pd.read_sql(query, conn, params=(team_name, team_name))
    conn.close()

    results = []
    # Duyệt qua các trận đấu
    for _, row in df.iterrows():
        h_score = row["Homescore"]
        a_score = row["Awayscore"]

        if row["Home"] == team_name:
            if h_score > a_score:
                results.append("🟢")
            elif h_score == a_score:
                results.append("⚪")
            else:
                results.append("🔴")
        else:  # Đội hiện tại là khách
            if a_score > h_score:
                results.append("🟢")
            elif a_score == h_score:
                results.append("⚪")
            else:
                results.append("🔴")

    return " ".join(results[::-1])


def load_leaderboard():
    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM LeaderBoard ORDER BY Pts DESC, Dif DESC, G DESC", conn
    )
    conn.close()
    df["Form"] = df["Team"].apply(get_recent_form)

    return df


def highlight_standings(row):
    rank = row.name + 1

    color = ""

    if rank <= 4:
        color = "background-color: rgba(66, 133, 244, 0.2)"
    elif rank == 5:
        color = "background-color: rgba(255, 165, 0, 0.2)"
    elif rank >= 18:
        color = "background-color: rgba(255, 77, 77, 0.2)"

    return [color] * len(row)


def show_main_page():
    st.title("⚽ Premier League Manager")

    tab1, tab2, tab3 = st.tabs(
        ["🏆 Bảng Xếp Hạng", "📝 Cập Nhật Tỉ Số", "📅 Lịch Thi Đấu & Kết Quả"]
    )

    with tab1:
        st.info("💡 Hint: Bấm vào tên đội bóng để xem lịch sử đấu.")

        st.markdown(
            """
        <div style="display: flex; gap: 15px; margin-bottom: 10px; font-size: 0.9em;">
            <span style="color: #4285F4; font-weight: bold;">■ Top 4: Champions League</span>
            <span style="color: #FFA500; font-weight: bold;">■ Top 5: Europa League</span>
            <span style="color: #FF4D4D; font-weight: bold;">■ Top 18-20: Xuống hạng</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

        df = load_leaderboard()
        df = df.reset_index(drop=True)
        df.insert(0, "Hạng", df.index + 1)
        df["Team_URL"] = df["Team"].apply(lambda x: f"/?team={x}")

        styler = df.style.apply(highlight_standings, axis=1)

        st.dataframe(
            styler,
            column_config={
                "Team": None,
                "Hạng": st.column_config.NumberColumn(
                    "Thứ hạng", format="%d", width="small"
                ),
                "Team_URL": st.column_config.LinkColumn(
                    "Đội bóng",
                    display_text="team=(.*)",
                    width="medium",
                ),
                "Form": st.column_config.TextColumn(
                    "Phong độ",
                    width="medium",
                    help="🟢 Thắng | ⚪ Hòa | 🔴 Thua",
                ),
                "GP": st.column_config.NumberColumn("Trận", format="%d"),
                "W": st.column_config.NumberColumn("Thắng", format="%d"),
                "D": st.column_config.NumberColumn("Hòa", format="%d"),
                "L": st.column_config.NumberColumn("Bại", format="%d"),
                "G": st.column_config.NumberColumn("BT", format="%d"),
                "GC": st.column_config.NumberColumn("BB", format="%d"),
                "Pts": st.column_config.ProgressColumn(
                    "Điểm", format="%d", min_value=0, max_value=114
                ),
                "Dif": st.column_config.NumberColumn("+/-", format="%+d"),
            },
            column_order=[
                "Hạng",
                "Team_URL",
                "GP",
                "W",
                "D",
                "L",
                "G",
                "GC",
                "Dif",
                "Pts",
                "Form",
            ],
            use_container_width=True,
            hide_index=True,
            height=800,
        )

    with tab2:
        # (Giữ nguyên code cũ của tab 2)
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

    with tab3:
        # (Giữ nguyên code cũ của tab 3)
        st.header("Toàn bộ kết quả & Lịch thi đấu")
        full_schedule = get_full_schedule_view()

        full_schedule["Home_URL"] = full_schedule["Home"].apply(lambda x: f"/?team={x}")
        full_schedule["Away_URL"] = full_schedule["Away"].apply(lambda x: f"/?team={x}")

        def highlight_upcoming(row):
            if row["Tỉ số"] == "Sắp đá":
                return ["background-color: rgba(255, 255, 0, 0.1)"] * len(row)
            return [""] * len(row)

        st.dataframe(
            full_schedule.style.apply(highlight_upcoming, axis=1),
            column_config={
                "Game": st.column_config.NumberColumn("Vòng", width="small"),
                "Home": None,
                "Away": None,
                "Home_URL": st.column_config.LinkColumn(
                    "Chủ nhà",
                    display_text="team=(.*)",
                    width="medium",
                ),
                "Tỉ số": st.column_config.TextColumn("Kết quả", width="small"),
                "Away_URL": st.column_config.LinkColumn(
                    "Khách",
                    display_text="team=(.*)",
                    width="medium",
                ),
            },
            column_order=["Game", "Home_URL", "Tỉ số", "Away_URL"],
            use_container_width=True,
            hide_index=True,
            height=800,
        )


query_params = st.query_params

if "team" in query_params:
    target_team = query_params["team"]
    show_team_page(target_team)
else:
    show_main_page()
