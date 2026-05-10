from app.analyzer.code_analyzer import Severity, Thresholds


class ScoreEngine:

    @staticmethod
    def compute(issues: list[dict]) -> int:

        weight_map = {
            Severity.LOW: Thresholds.SCORE_WEIGHT_LOW,
            Severity.MEDIUM: Thresholds.SCORE_WEIGHT_MEDIUM,
            Severity.HIGH: Thresholds.SCORE_WEIGHT_HIGH,
            Severity.CRITICAL: Thresholds.SCORE_WEIGHT_CRITICAL,
        }

        penalty = sum(
            weight_map.get(issue["severity"], 1.0)
            for issue in issues
        )

        return max(0, round(10 - penalty))