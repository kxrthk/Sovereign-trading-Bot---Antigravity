# Sovereign Bot Performance Metrics

To determine "Excellence" and "Knowledge," the bot operates on two scales:

## 1. The Internal Scale (Karma)
*   **Metric**: Win Rate % (Batting Average).
*   **Scale**: 0 to 100.
*   **Formula**: `(Winning Trades / Total Closed Trades) * 100`
*   **Excellence Threshold**:
    *   **> 60%**: "God-Mode" (Aggressive Mood). The bot is "seeing the matrix."
    *   **< 50%**: "Student Mode" (Conservative Mood). The bot is cautious.
    *   **Comparison**: Compares itself against its own history.

## 2. The External Benchmark (Alpha)
*   **Metric**: Total Return vs. Benchmark.
*   **Comparison**: Your Portfolio Return vs. **Nifty 100 Index** Return.
*   **Definition of Excellence**:
    *   If Bot > Nifty 100 = **Positive Alpha** (Excellent).
    *   If Bot < Nifty 100 = **Negative Alpha** (Poor).

## Missing Link: The Feedback Loop
Currently, the bot **opens** trades but does not **close** them. To measure excellence, we must implement a **Trade Resolver** that:
1.  Checks current prices of active trades.
2.  Marks them as **WIN** (Target Hit) or **LOSS** (Stop Loss Hit).
3.  Updates the Karma Score.
