class ReportStrategy:
    def generate(self, data):
        raise NotImplementedError


class VehicleLoadReport(ReportStrategy):
    def generate(self, trips):
        return {"total_trips": len(trips)}


class CostReport(ReportStrategy):
    def generate(self, expenses):
        return {"total_cost": float(sum(e.amount for e in expenses))}


class PeriodAnalyticsReport(ReportStrategy):
    def generate(self, trips, expenses):
        return {
            "trips": len(trips),
            "costs": float(sum(e.amount for e in expenses))
        }


class CostReport:
    def generate(self, expenses):
        result = {}
        for e in expenses:
            if e.expense_type not in result:
                result[e.expense_type] = 0
            result[e.expense_type] += e.amount
        return result
