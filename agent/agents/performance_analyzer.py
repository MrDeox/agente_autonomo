
import pandas as pd

class PerformanceAnalysisAgent:
    """
    An agent dedicated to analyzing the performance of Hephaestus.
    """

    def __init__(self, evolution_log_path="logs/evolution_log.csv"):
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

        # Ensure 'status' column is boolean and present
        if 'status' not in log_df.columns:
            return "Evolution log is missing the 'status' column. No performance analysis available."
        log_df['status'] = log_df['status'].eq(True) if log_df['status'].dtype == bool else log_df['status'].astype(str).str.lower().eq('sucesso')

        total_cycles = len(log_df)
        successful_cycles = log_df['status'].sum()
        failed_cycles = total_cycles - successful_cycles
        success_rate = (successful_cycles / total_cycles) * 100 if total_cycles > 0 else 0

        # Base summary
        summary_str = f"""Performance Summary:
- Total Cycles: {total_cycles}
- Successful Cycles: {successful_cycles}
- Failed Cycles: {failed_cycles}
- Success Rate: {success_rate:.2f}%"""

        # Average duration
        if 'duration_seconds' in log_df.columns:
            avg_duration = log_df['duration_seconds'].mean()
            summary_str += f"\n- Average Cycle Duration: {avg_duration:.2f} seconds"
        else:
            summary_str += f"\n- Average Cycle Duration: N/A"

        # Analysis by strategy
        if 'estrategia_usada' in log_df.columns:
            strategy_performance = log_df.groupby('estrategia_usada')['status'].agg(['sum', 'count'])
            strategy_performance['failure_count'] = strategy_performance['count'] - strategy_performance['sum']
            strategy_performance['success_rate'] = (strategy_performance['sum'] / strategy_performance['count']) * 100
            strategy_performance = strategy_performance.sort_values(by='failure_count', ascending=False)

            summary_str += "\n\nPerformance by Strategy (sorted by failures):\n"
            for index, row in strategy_performance.iterrows():
                summary_str += f"- Strategy '{index}': Success Rate: {row['success_rate']:.2f}% (Failures: {int(row['failure_count'])}/{int(row['count'])})\n"
        else:
            summary_str += "\n\nPerformance by Strategy: N/A\n"


        return summary_str
