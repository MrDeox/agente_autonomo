
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

        # Ensure 'success' column is boolean
        log_df['success'] = log_df['success'].eq(True) if log_df['success'].dtype == bool else log_df['success'].astype(str).str.lower().eq('true')

        total_cycles = len(log_df)
        successful_cycles = log_df['success'].sum()
        failed_cycles = total_cycles - successful_cycles
        success_rate = (successful_cycles / total_cycles) * 100 if total_cycles > 0 else 0

        # Analysis by strategy
        strategy_performance = log_df.groupby('strategy')['success'].agg(['sum', 'count'])
        strategy_performance['failure_count'] = strategy_performance['count'] - strategy_performance['sum']
        strategy_performance['success_rate'] = (strategy_performance['sum'] / strategy_performance['count']) * 100
        strategy_performance = strategy_performance.sort_values(by='failure_count', ascending=False)

        # Average duration
        avg_duration = log_df['duration_seconds'].mean()

        summary_str = f"""
Performance Summary:
- Total Cycles: {total_cycles}
- Successful Cycles: {successful_cycles}
- Failed Cycles: {failed_cycles}
- Success Rate: {success_rate:.2f}%
- Average Cycle Duration: {avg_duration:.2f} seconds

Performance by Strategy (sorted by failures):
"""
        for index, row in strategy_performance.iterrows():
            summary_str += f"- Strategy '{index}': Success Rate: {row['success_rate']:.2f}% (Failures: {row['failure_count']}/{row['count']})\n"

        return summary_str
