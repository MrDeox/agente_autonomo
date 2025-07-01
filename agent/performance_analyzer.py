
import pandas as pd

class PerformanceAnalysisAgent:
    """
    An agent dedicated to analyzing the performance of Hephaestus.
    """

    def __init__(self, evolution_log_path="evolution_log.csv"):
        """
        Initializes the PerformanceAnalysisAgent.

        :param evolution_log_path: Path to the evolution log file.
        """
        self.evolution_log_path = evolution_log_path

    def analyze_performance(self):
        """
        Analyzes the evolution log to generate a performance summary.

        :return: A string containing the performance summary.
        """
        try:
            log_df = pd.read_csv(self.evolution_log_path)
            if log_df.empty:
                return "Evolution log is empty. No performance analysis available."
        except FileNotFoundError:
            return "Evolution log not found. No performance analysis available."
        except pd.errors.EmptyDataError:
            return "Evolution log is empty. No performance analysis available."

        summary = {
            "total_cycles": len(log_df),
            "successful_cycles": log_df["success"].sum(),
            "failed_cycles": len(log_df) - log_df["success"].sum(),
            "success_rate": (log_df["success"].sum() / len(log_df)) * 100,
        }

        return f"""
Performance Summary:
- Total Cycles: {summary['total_cycles']}
- Successful Cycles: {summary['successful_cycles']}
- Failed Cycles: {summary['failed_cycles']}
- Success Rate: {summary['success_rate']:.2f}%
"""
