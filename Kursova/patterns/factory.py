from domain.models import Expense


class ExpenseFactory:
    @staticmethod
    def create(vehicle_id, expense_type, amount, date):
        return Expense(
            vehicle_id=vehicle_id,
            expense_type=expense_type,
            amount=amount,
            expense_date=date
        )
