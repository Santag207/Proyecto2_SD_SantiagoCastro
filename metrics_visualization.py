import matplotlib.pyplot as plt
import sqlite3

class MetricsVisualization:
    def __init__(self, db_name="system_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def fetch_metrics(self):
        self.cursor.execute("SELECT * FROM metrics")
        return self.cursor.fetchall()

    def plot_metrics_by_component(self):
        metrics = self.fetch_metrics()
        primary_metrics = [row for row in metrics if row[1] == "primary"]
        backup_metrics = [row for row in metrics if row[1] == "backup"]

        plt.plot([row[2] for row in primary_metrics], label="Primary", color="blue")
        plt.plot([row[2] for row in backup_metrics], label="Backup", color="orange")
        plt.xlabel("Time")
        plt.ylabel("Services")
        plt.legend()
        plt.title("Metrics by Component")
        plt.show()

if __name__ == "__main__":
    metrics = MetricsVisualization()
    metrics.plot_metrics()
