import sqlite3

class ReportDatabase:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.c.execute("""CREATE TABLE IF NOT EXISTS reported_users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            discord_username TEXT UNIQUE,
                            violation_count INTEGER DEFAULT 0,
                            scam_count INTEGER DEFAULT 0,
                            harassment_count INTEGER DEFAULT 0,
                            violence_count INTEGER DEFAULT 0,
                            other_count INTEGER DEFAULT 0
                        )""")
        self.conn.commit()

    def add_report(self, discord_username, category):
        self.c.execute("SELECT * FROM reported_users WHERE discord_username=?", (discord_username,))
        user = self.c.fetchone()

        if user:
            if category == "scam":
                self.c.execute("UPDATE reported_users SET violation_count = violation_count + 1, scam_count = scam_count + 1 WHERE discord_username=?", (discord_username,))
            elif category == "harassment":
                self.c.execute("UPDATE reported_users SET violation_count = violation_count + 1, harassment_count = harassment_count + 1 WHERE discord_username=?", (discord_username,))
            elif category == "violence":
                self.c.execute("UPDATE reported_users SET violation_count = violation_count + 1, violence_count = violence_count + 1 WHERE discord_username=?", (discord_username,))
            else:
                self.c.execute("UPDATE reported_users SET violation_count = violation_count + 1, other_count = other_count + 1 WHERE discord_username=?", (discord_username,))
        else:
            if category == "scam":
                self.c.execute("INSERT INTO reported_users (discord_username, violation_count, scam_count) VALUES (?, 1, 1)", (discord_username,))
            elif category == "harassment":
                self.c.execute("INSERT INTO reported_users (discord_username, violation_count, harassment_count) VALUES (?, 1, 1)", (discord_username,))
            elif category == "violence":
                self.c.execute("INSERT INTO reported_users (discord_username, violation_count, violence_count) VALUES (?, 1, 1)", (discord_username,))
            else:
                self.c.execute("INSERT INTO reported_users (discord_username, violation_count, other_count) VALUES (?, 1, 1)", (discord_username,))

        self.conn.commit()

    def get_report_count(self, discord_username):
        self.c.execute("SELECT violation_count FROM reported_users WHERE discord_username=?", (discord_username,))
        count = self.c.fetchone()
        return count[0] if count else 0

    def close_connection(self):
        self.conn.close()
