from collections import Counter

from app.schemas.case import CaseInput


class TransactionPatternService:
    SUB_THRESHOLD_LIMIT = 10000.0

    def extract_patterns(self, case: CaseInput) -> dict:
        txns = case.transactions
        if not txns:
            return {"patterns": [], "stats": {"count": 0, "total_volume": 0}}

        amounts = [t.amount for t in txns]
        total = sum(amounts)
        avg = total / len(amounts)
        inbound = sum(t.amount for t in txns if t.direction == "inbound")
        outbound = sum(t.amount for t in txns if t.direction == "outbound")

        patterns: list[str] = []
        sub_threshold_count = sum(1 for a in amounts if a < self.SUB_THRESHOLD_LIMIT)
        if sub_threshold_count >= 5:
            patterns.append("repeated_sub_threshold_transactions")

        if inbound > 0 and outbound / inbound > 0.85:
            patterns.append("rapid_movement_of_funds")

        high = max(amounts)
        if high > (avg * 3):
            patterns.append("sudden_spike_in_volume")

        country_counter = Counter(t.destination_country for t in txns if t.destination_country)
        if len(country_counter) >= 3:
            patterns.append("cross_border_activity")

        if len(txns) >= 20:
            patterns.append("unusual_transaction_frequency")

        if case.customer_profile.segment.lower() == "retail" and total > 200000:
            patterns.append("profile_behavior_mismatch")

        return {
            "patterns": patterns,
            "stats": {
                "count": len(txns),
                "total_volume": total,
                "average_amount": avg,
                "inbound_volume": inbound,
                "outbound_volume": outbound,
            },
        }
