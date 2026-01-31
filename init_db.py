import sqlite3


def init_database():
    db_name = "football.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    schema_script = """
    DROP TABLE IF EXISTS Schedule;
    DROP TABLE IF EXISTS LeaderBoard;

    CREATE TABLE LeaderBoard (
        Team VARCHAR(50) NOT NULL PRIMARY KEY,
        GP INT DEFAULT 0, W INT DEFAULT 0, D INT DEFAULT 0, L INT DEFAULT 0,
        G INT DEFAULT 0, GC INT DEFAULT 0,
        Dif INT GENERATED ALWAYS AS (G - GC) STORED,
        Pts INT GENERATED ALWAYS AS (3*W + D) STORED
    );

    CREATE TABLE Schedule (
        Game INT NOT NULL,
        Home VARCHAR(50) NOT NULL,
        Homescore INT, Awayscore INT,
        Away VARCHAR(50) NOT NULL,
        PRIMARY KEY(Game, Home, Away),
        FOREIGN KEY(Home) REFERENCES LeaderBoard(Team),
        FOREIGN KEY(Away) REFERENCES LeaderBoard(Team)
    );

    INSERT INTO LeaderBoard (Team) VALUES
    ('Arsenal'), ('Man City'), ('Aston Villa'), ('Liverpool'), ('Brentford'), ('Newcastle'), ('Man Utd'), ('Chelsea'),
    ('Fulham'), ('Sunderland'), ('Brighton'), ('Everton'), ('Crystal Palace'), ('Tottenham'), ('Bournemouth'), ('Leeds'),
    ('Nottm Forest'), ('West Ham'), ('Burnley'), ('Wolves');

    CREATE TRIGGER trg_MatchUpdate
    AFTER UPDATE ON Schedule
    WHEN (OLD.Homescore IS NOT NULL OR NEW.Homescore IS NOT NULL)
    BEGIN
        UPDATE LeaderBoard SET 
            GP=GP-1, G=G-OLD.Homescore, GC=GC-OLD.Awayscore,
            W=W-(CASE WHEN OLD.Homescore>OLD.Awayscore THEN 1 ELSE 0 END),
            D=D-(CASE WHEN OLD.Homescore=OLD.Awayscore THEN 1 ELSE 0 END),
            L=L-(CASE WHEN OLD.Homescore<OLD.Awayscore THEN 1 ELSE 0 END)
        WHERE Team=OLD.Home AND OLD.Homescore IS NOT NULL;
        
        UPDATE LeaderBoard SET 
            GP=GP-1, G=G-OLD.Awayscore, GC=GC-OLD.Homescore,
            W=W-(CASE WHEN OLD.Awayscore>OLD.Homescore THEN 1 ELSE 0 END),
            D=D-(CASE WHEN OLD.Awayscore=OLD.Homescore THEN 1 ELSE 0 END),
            L=L-(CASE WHEN OLD.Awayscore<OLD.Homescore THEN 1 ELSE 0 END)
        WHERE Team=OLD.Away AND OLD.Awayscore IS NOT NULL;

        UPDATE LeaderBoard SET 
            GP=GP+1, G=G+NEW.Homescore, GC=GC+NEW.Awayscore,
            W=W+(CASE WHEN NEW.Homescore>NEW.Awayscore THEN 1 ELSE 0 END),
            D=D+(CASE WHEN NEW.Homescore=NEW.Awayscore THEN 1 ELSE 0 END),
            L=L+(CASE WHEN NEW.Homescore<NEW.Awayscore THEN 1 ELSE 0 END)
        WHERE Team=NEW.Home AND NEW.Homescore IS NOT NULL;

        UPDATE LeaderBoard SET 
            GP=GP+1, G=G+NEW.Awayscore, GC=GC+NEW.Homescore,
            W=W+(CASE WHEN NEW.Awayscore>NEW.Homescore THEN 1 ELSE 0 END),
            D=D+(CASE WHEN NEW.Awayscore=NEW.Homescore THEN 1 ELSE 0 END),
            L=L+(CASE WHEN NEW.Awayscore<NEW.Homescore THEN 1 ELSE 0 END)
        WHERE Team=NEW.Away AND NEW.Awayscore IS NOT NULL;
    END;
    """
    cursor.executescript(schema_script)

    schedule_data = """
    (1, 'Arsenal', 'Wolves'), (1, 'Man City', 'Burnley'), (1, 'Aston Villa', 'West Ham'), (1, 'Liverpool', 'Nottm Forest'), (1, 'Brentford', 'Leeds'), (1, 'Newcastle', 'Bournemouth'), (1, 'Man Utd', 'Tottenham'), (1, 'Chelsea', 'Crystal Palace'), (1, 'Fulham', 'Everton'), (1, 'Sunderland', 'Brighton'),
    (2, 'Arsenal', 'Burnley'), (2, 'Wolves', 'West Ham'), (2, 'Man City', 'Nottm Forest'), (2, 'Aston Villa', 'Leeds'), (2, 'Liverpool', 'Bournemouth'), (2, 'Brentford', 'Tottenham'), (2, 'Newcastle', 'Crystal Palace'), (2, 'Man Utd', 'Everton'), (2, 'Chelsea', 'Brighton'), (2, 'Fulham', 'Sunderland'),
    (3, 'Arsenal', 'West Ham'), (3, 'Burnley', 'Nottm Forest'), (3, 'Wolves', 'Leeds'), (3, 'Man City', 'Bournemouth'), (3, 'Aston Villa', 'Tottenham'), (3, 'Liverpool', 'Crystal Palace'), (3, 'Brentford', 'Everton'), (3, 'Newcastle', 'Brighton'), (3, 'Man Utd', 'Sunderland'), (3, 'Chelsea', 'Fulham'),
    (4, 'Arsenal', 'Nottm Forest'), (4, 'West Ham', 'Leeds'), (4, 'Burnley', 'Bournemouth'), (4, 'Wolves', 'Tottenham'), (4, 'Man City', 'Crystal Palace'), (4, 'Aston Villa', 'Everton'), (4, 'Liverpool', 'Brighton'), (4, 'Brentford', 'Sunderland'), (4, 'Newcastle', 'Fulham'), (4, 'Man Utd', 'Chelsea'),
    (5, 'Arsenal', 'Leeds'), (5, 'Nottm Forest', 'Bournemouth'), (5, 'West Ham', 'Tottenham'), (5, 'Burnley', 'Crystal Palace'), (5, 'Wolves', 'Everton'), (5, 'Man City', 'Brighton'), (5, 'Aston Villa', 'Sunderland'), (5, 'Liverpool', 'Fulham'), (5, 'Brentford', 'Chelsea'), (5, 'Newcastle', 'Man Utd'),
    (6, 'Arsenal', 'Bournemouth'), (6, 'Leeds', 'Tottenham'), (6, 'Nottm Forest', 'Crystal Palace'), (6, 'West Ham', 'Everton'), (6, 'Burnley', 'Brighton'), (6, 'Wolves', 'Sunderland'), (6, 'Man City', 'Fulham'), (6, 'Aston Villa', 'Chelsea'), (6, 'Liverpool', 'Man Utd'), (6, 'Brentford', 'Newcastle'),
    (7, 'Arsenal', 'Tottenham'), (7, 'Bournemouth', 'Crystal Palace'), (7, 'Leeds', 'Everton'), (7, 'Nottm Forest', 'Brighton'), (7, 'West Ham', 'Sunderland'), (7, 'Burnley', 'Fulham'), (7, 'Wolves', 'Chelsea'), (7, 'Man City', 'Man Utd'), (7, 'Aston Villa', 'Newcastle'), (7, 'Liverpool', 'Brentford'),
    (8, 'Arsenal', 'Crystal Palace'), (8, 'Tottenham', 'Everton'), (8, 'Bournemouth', 'Brighton'), (8, 'Leeds', 'Sunderland'), (8, 'Nottm Forest', 'Fulham'), (8, 'West Ham', 'Chelsea'), (8, 'Burnley', 'Man Utd'), (8, 'Wolves', 'Newcastle'), (8, 'Man City', 'Brentford'), (8, 'Aston Villa', 'Liverpool'),
    (9, 'Arsenal', 'Everton'), (9, 'Crystal Palace', 'Brighton'), (9, 'Tottenham', 'Sunderland'), (9, 'Bournemouth', 'Fulham'), (9, 'Leeds', 'Chelsea'), (9, 'Nottm Forest', 'Man Utd'), (9, 'West Ham', 'Newcastle'), (9, 'Burnley', 'Brentford'), (9, 'Wolves', 'Liverpool'), (9, 'Man City', 'Aston Villa'),
    (10, 'Arsenal', 'Brighton'), (10, 'Everton', 'Sunderland'), (10, 'Crystal Palace', 'Fulham'), (10, 'Tottenham', 'Chelsea'), (10, 'Bournemouth', 'Man Utd'), (10, 'Leeds', 'Newcastle'), (10, 'Nottm Forest', 'Brentford'), (10, 'West Ham', 'Liverpool'), (10, 'Burnley', 'Aston Villa'), (10, 'Wolves', 'Man City'),
    (11, 'Arsenal', 'Sunderland'), (11, 'Brighton', 'Fulham'), (11, 'Everton', 'Chelsea'), (11, 'Crystal Palace', 'Man Utd'), (11, 'Tottenham', 'Newcastle'), (11, 'Bournemouth', 'Brentford'), (11, 'Leeds', 'Liverpool'), (11, 'Nottm Forest', 'Aston Villa'), (11, 'West Ham', 'Man City'), (11, 'Burnley', 'Wolves'),
    (12, 'Arsenal', 'Fulham'), (12, 'Sunderland', 'Chelsea'), (12, 'Brighton', 'Man Utd'), (12, 'Everton', 'Newcastle'), (12, 'Crystal Palace', 'Brentford'), (12, 'Tottenham', 'Liverpool'), (12, 'Bournemouth', 'Aston Villa'), (12, 'Leeds', 'Man City'), (12, 'Nottm Forest', 'Wolves'), (12, 'West Ham', 'Burnley'),
    (13, 'Arsenal', 'Chelsea'), (13, 'Fulham', 'Man Utd'), (13, 'Sunderland', 'Newcastle'), (13, 'Brighton', 'Brentford'), (13, 'Everton', 'Liverpool'), (13, 'Crystal Palace', 'Aston Villa'), (13, 'Tottenham', 'Man City'), (13, 'Bournemouth', 'Wolves'), (13, 'Leeds', 'Burnley'), (13, 'Nottm Forest', 'West Ham'),
    (14, 'Arsenal', 'Man Utd'), (14, 'Chelsea', 'Newcastle'), (14, 'Fulham', 'Brentford'), (14, 'Sunderland', 'Liverpool'), (14, 'Brighton', 'Aston Villa'), (14, 'Everton', 'Man City'), (14, 'Crystal Palace', 'Wolves'), (14, 'Tottenham', 'Burnley'), (14, 'Bournemouth', 'West Ham'), (14, 'Leeds', 'Nottm Forest'),
    (15, 'Arsenal', 'Newcastle'), (15, 'Man Utd', 'Brentford'), (15, 'Chelsea', 'Liverpool'), (15, 'Fulham', 'Aston Villa'), (15, 'Sunderland', 'Man City'), (15, 'Brighton', 'Wolves'), (15, 'Everton', 'Burnley'), (15, 'Crystal Palace', 'West Ham'), (15, 'Tottenham', 'Nottm Forest'), (15, 'Bournemouth', 'Leeds'),
    (16, 'Arsenal', 'Brentford'), (16, 'Newcastle', 'Liverpool'), (16, 'Man Utd', 'Aston Villa'), (16, 'Chelsea', 'Man City'), (16, 'Fulham', 'Wolves'), (16, 'Sunderland', 'Burnley'), (16, 'Brighton', 'West Ham'), (16, 'Everton', 'Nottm Forest'), (16, 'Crystal Palace', 'Leeds'), (16, 'Tottenham', 'Bournemouth'),
    (17, 'Arsenal', 'Liverpool'), (17, 'Brentford', 'Aston Villa'), (17, 'Newcastle', 'Man City'), (17, 'Man Utd', 'Wolves'), (17, 'Chelsea', 'Burnley'), (17, 'Fulham', 'West Ham'), (17, 'Sunderland', 'Nottm Forest'), (17, 'Brighton', 'Leeds'), (17, 'Everton', 'Bournemouth'), (17, 'Crystal Palace', 'Tottenham'),
    (18, 'Arsenal', 'Aston Villa'), (18, 'Liverpool', 'Man City'), (18, 'Brentford', 'Wolves'), (18, 'Newcastle', 'Burnley'), (18, 'Man Utd', 'West Ham'), (18, 'Chelsea', 'Nottm Forest'), (18, 'Fulham', 'Leeds'), (18, 'Sunderland', 'Bournemouth'), (18, 'Brighton', 'Tottenham'), (18, 'Everton', 'Crystal Palace'),
    (19, 'Arsenal', 'Man City'), (19, 'Aston Villa', 'Wolves'), (19, 'Liverpool', 'Burnley'), (19, 'Brentford', 'West Ham'), (19, 'Newcastle', 'Nottm Forest'), (19, 'Man Utd', 'Leeds'), (19, 'Chelsea', 'Bournemouth'), (19, 'Fulham', 'Tottenham'), (19, 'Sunderland', 'Crystal Palace'), (19, 'Brighton', 'Everton'),
    (20, 'Wolves', 'Arsenal'), (20, 'Burnley', 'Man City'), (20, 'West Ham', 'Aston Villa'), (20, 'Nottm Forest', 'Liverpool'), (20, 'Leeds', 'Brentford'), (20, 'Bournemouth', 'Newcastle'), (20, 'Tottenham', 'Man Utd'), (20, 'Crystal Palace', 'Chelsea'), (20, 'Everton', 'Fulham'), (20, 'Brighton', 'Sunderland'),
    (21, 'Burnley', 'Arsenal'), (21, 'West Ham', 'Wolves'), (21, 'Nottm Forest', 'Man City'), (21, 'Leeds', 'Aston Villa'), (21, 'Bournemouth', 'Liverpool'), (21, 'Tottenham', 'Brentford'), (21, 'Crystal Palace', 'Newcastle'), (21, 'Everton', 'Man Utd'), (21, 'Brighton', 'Chelsea'), (21, 'Sunderland', 'Fulham'),
    (22, 'West Ham', 'Arsenal'), (22, 'Nottm Forest', 'Burnley'), (22, 'Leeds', 'Wolves'), (22, 'Bournemouth', 'Man City'), (22, 'Tottenham', 'Aston Villa'), (22, 'Crystal Palace', 'Liverpool'), (22, 'Everton', 'Brentford'), (22, 'Brighton', 'Newcastle'), (22, 'Sunderland', 'Man Utd'), (22, 'Fulham', 'Chelsea'),
    (23, 'Nottm Forest', 'Arsenal'), (23, 'Leeds', 'West Ham'), (23, 'Bournemouth', 'Burnley'), (23, 'Tottenham', 'Wolves'), (23, 'Crystal Palace', 'Man City'), (23, 'Everton', 'Aston Villa'), (23, 'Brighton', 'Liverpool'), (23, 'Sunderland', 'Brentford'), (23, 'Fulham', 'Newcastle'), (23, 'Chelsea', 'Man Utd'),
    (24, 'Leeds', 'Arsenal'), (24, 'Bournemouth', 'Nottm Forest'), (24, 'Tottenham', 'West Ham'), (24, 'Crystal Palace', 'Burnley'), (24, 'Everton', 'Wolves'), (24, 'Brighton', 'Man City'), (24, 'Sunderland', 'Aston Villa'), (24, 'Fulham', 'Liverpool'), (24, 'Chelsea', 'Brentford'), (24, 'Man Utd', 'Newcastle'),
    (25, 'Bournemouth', 'Arsenal'), (25, 'Tottenham', 'Leeds'), (25, 'Crystal Palace', 'Nottm Forest'), (25, 'Everton', 'West Ham'), (25, 'Brighton', 'Burnley'), (25, 'Sunderland', 'Wolves'), (25, 'Fulham', 'Man City'), (25, 'Chelsea', 'Aston Villa'), (25, 'Man Utd', 'Liverpool'), (25, 'Newcastle', 'Brentford'),
    (26, 'Tottenham', 'Arsenal'), (26, 'Crystal Palace', 'Bournemouth'), (26, 'Everton', 'Leeds'), (26, 'Brighton', 'Nottm Forest'), (26, 'Sunderland', 'West Ham'), (26, 'Fulham', 'Burnley'), (26, 'Chelsea', 'Wolves'), (26, 'Man Utd', 'Man City'), (26, 'Newcastle', 'Aston Villa'), (26, 'Brentford', 'Liverpool'),
    (27, 'Crystal Palace', 'Arsenal'), (27, 'Everton', 'Tottenham'), (27, 'Brighton', 'Bournemouth'), (27, 'Sunderland', 'Leeds'), (27, 'Fulham', 'Nottm Forest'), (27, 'Chelsea', 'West Ham'), (27, 'Man Utd', 'Burnley'), (27, 'Newcastle', 'Wolves'), (27, 'Brentford', 'Man City'), (27, 'Liverpool', 'Aston Villa'),
    (28, 'Everton', 'Arsenal'), (28, 'Brighton', 'Crystal Palace'), (28, 'Sunderland', 'Tottenham'), (28, 'Fulham', 'Bournemouth'), (28, 'Chelsea', 'Leeds'), (28, 'Man Utd', 'Nottm Forest'), (28, 'Newcastle', 'West Ham'), (28, 'Brentford', 'Burnley'), (28, 'Liverpool', 'Wolves'), (28, 'Aston Villa', 'Man City'),
    (29, 'Brighton', 'Arsenal'), (29, 'Sunderland', 'Everton'), (29, 'Fulham', 'Crystal Palace'), (29, 'Chelsea', 'Tottenham'), (29, 'Man Utd', 'Bournemouth'), (29, 'Newcastle', 'Leeds'), (29, 'Brentford', 'Nottm Forest'), (29, 'Liverpool', 'West Ham'), (29, 'Aston Villa', 'Burnley'), (29, 'Man City', 'Wolves'),
    (30, 'Sunderland', 'Arsenal'), (30, 'Fulham', 'Brighton'), (30, 'Chelsea', 'Everton'), (30, 'Man Utd', 'Crystal Palace'), (30, 'Newcastle', 'Tottenham'), (30, 'Brentford', 'Bournemouth'), (30, 'Liverpool', 'Leeds'), (30, 'Aston Villa', 'Nottm Forest'), (30, 'Man City', 'West Ham'), (30, 'Wolves', 'Burnley'),
    (31, 'Fulham', 'Arsenal'), (31, 'Chelsea', 'Sunderland'), (31, 'Man Utd', 'Brighton'), (31, 'Newcastle', 'Everton'), (31, 'Brentford', 'Crystal Palace'), (31, 'Liverpool', 'Tottenham'), (31, 'Aston Villa', 'Bournemouth'), (31, 'Man City', 'Leeds'), (31, 'Wolves', 'Nottm Forest'), (31, 'Burnley', 'West Ham'),
    (32, 'Chelsea', 'Arsenal'), (32, 'Man Utd', 'Fulham'), (32, 'Newcastle', 'Sunderland'), (32, 'Brentford', 'Brighton'), (32, 'Liverpool', 'Everton'), (32, 'Aston Villa', 'Crystal Palace'), (32, 'Man City', 'Tottenham'), (32, 'Wolves', 'Bournemouth'), (32, 'Burnley', 'Leeds'), (32, 'West Ham', 'Nottm Forest'),
    (33, 'Man Utd', 'Arsenal'), (33, 'Newcastle', 'Chelsea'), (33, 'Brentford', 'Fulham'), (33, 'Liverpool', 'Sunderland'), (33, 'Aston Villa', 'Brighton'), (33, 'Man City', 'Everton'), (33, 'Wolves', 'Crystal Palace'), (33, 'Burnley', 'Tottenham'), (33, 'West Ham', 'Bournemouth'), (33, 'Nottm Forest', 'Leeds'),
    (34, 'Newcastle', 'Arsenal'), (34, 'Brentford', 'Man Utd'), (34, 'Liverpool', 'Chelsea'), (34, 'Aston Villa', 'Fulham'), (34, 'Man City', 'Sunderland'), (34, 'Wolves', 'Brighton'), (34, 'Burnley', 'Everton'), (34, 'West Ham', 'Crystal Palace'), (34, 'Nottm Forest', 'Tottenham'), (34, 'Leeds', 'Bournemouth'),
    (35, 'Brentford', 'Arsenal'), (35, 'Liverpool', 'Newcastle'), (35, 'Aston Villa', 'Man Utd'), (35, 'Man City', 'Chelsea'), (35, 'Wolves', 'Fulham'), (35, 'Burnley', 'Sunderland'), (35, 'West Ham', 'Brighton'), (35, 'Nottm Forest', 'Everton'), (35, 'Leeds', 'Crystal Palace'), (35, 'Bournemouth', 'Tottenham'),
    (36, 'Liverpool', 'Arsenal'), (36, 'Aston Villa', 'Brentford'), (36, 'Man City', 'Newcastle'), (36, 'Wolves', 'Man Utd'), (36, 'Burnley', 'Chelsea'), (36, 'West Ham', 'Fulham'), (36, 'Nottm Forest', 'Sunderland'), (36, 'Leeds', 'Brighton'), (36, 'Bournemouth', 'Everton'), (36, 'Tottenham', 'Crystal Palace'),
    (37, 'Aston Villa', 'Arsenal'), (37, 'Man City', 'Liverpool'), (37, 'Wolves', 'Brentford'), (37, 'Burnley', 'Newcastle'), (37, 'West Ham', 'Man Utd'), (37, 'Nottm Forest', 'Chelsea'), (37, 'Leeds', 'Fulham'), (37, 'Bournemouth', 'Sunderland'), (37, 'Tottenham', 'Brighton'), (37, 'Crystal Palace', 'Everton'),
    (38, 'Man City', 'Arsenal'), (38, 'Wolves', 'Aston Villa'), (38, 'Burnley', 'Liverpool'), (38, 'West Ham', 'Brentford'), (38, 'Nottm Forest', 'Newcastle'), (38, 'Leeds', 'Man Utd'), (38, 'Bournemouth', 'Chelsea'), (38, 'Tottenham', 'Fulham'), (38, 'Crystal Palace', 'Sunderland'), (38, 'Everton', 'Brighton')
    """

    try:
        import ast

        values = schedule_data.strip().replace("\n", "").replace("    ", "")
        cursor.execute(f"INSERT INTO Schedule (Game, Home, Away) VALUES {values}")

        conn.commit()
        print("Đã nạp dữ liệu.")
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
