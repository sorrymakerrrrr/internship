import os
import datetime

__all__ = ['min_distance']


# 最小编辑距离
def min_distance(words1: str, words2: str) -> int:
    m = len(words1)
    n = len(words2)
    if m == 0 or n == 0:
        return m + n
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for i in range(n + 1):
        dp[0][i] = i

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            left = dp[i][j - 1] + 1
            down = dp[i - 1][j] + 1
            if words1[i - 1] == words2[j - 1]:
                left_down = dp[i - 1][j - 1]
            else:
                left_down = dp[i - 1][j - 1] + 1
            dp[i][j] = min(left, down, left_down)

    return dp[m][n]
