from django.contrib import admin
from django.utils.html import format_html
from .models import Account
from simple_history.admin import SimpleHistoryAdmin
import json


class PayoutStatusFilter(admin.SimpleListFilter):
    title = 'Payout Status'
    parameter_name = 'payout_status'

    def lookups(self, request, model_admin):
        return (
            ('pending', 'Pending'),
            ('completed', 'Completed'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'pending':
            return queryset.filter(pending_payout__gt=0)
        if self.value() == 'completed':
            return queryset.filter(pending_payout=0)
        return queryset


@admin.register(Account)
class AccountAdmin(SimpleHistoryAdmin):
    list_display = (
        'user',
        'current_balance',
        'pending_payout',
        'payout_status_display',
        'bank_account_number',
    )
    readonly_fields = (
        'formatted_withdrawal_history',
        'current_balance',
    )
    list_filter = (
        'pending_payout',
        'payout_status',
    )
    actions = ['process_payouts']

    fieldsets = (
        (
            'Account Information',
            {
                'fields': (
                    'user',
                    'current_balance',
                    'bank_account_number',
                )
            },
        ),
        (
            'Payout Information',
            {
                'fields': (
                    'pending_payout',
                    'payout_requested_at',
                    'payout_status',
                ),
            },
        ),
        (
            'Withdrawal History',
            {'fields': ('formatted_withdrawal_history',)},
        ),
    )

    def payout_status_display(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            'red' if obj.pending_payout > 0 else 'green',
            'Pending' if obj.pending_payout > 0 else 'Completed',
        )

    payout_status_display.short_description = 'Payout Status'

    def process_payouts(self, request, queryset):
        for account in queryset:
            if account.process_payout():
                self.message_user(
                    request, f'Payout processed for {account.user.username}.'
                )
            else:
                self.message_user(
                    request,
                    f'No pending payout for {account.user.username}.',
                    level='warning',
                )

    process_payouts.short_description = 'Process Pending Payouts'

    def current_balance(self, obj):
        return obj.calculate_balance()

    current_balance.short_description = 'Current Balance'

    def formatted_withdrawal_history(self, obj):
    # Ensure withdrawal_history is decoded properly
        try:
            withdrawals = json.loads(obj.withdrawal_history) if obj.withdrawal_history else []
        except json.JSONDecodeError:
            withdrawals = []
            print(f"Failed to decode withdrawal_history: {obj.withdrawal_history}")

        if not withdrawals:
            return "No withdrawal history."

        table_rows = "".join(
            f"<tr><td>{w.get('date', 'N/A')}</td><td>{w.get('amount', 0)}</td></tr>"  # Use .get to avoid KeyError
            for w in sorted(withdrawals, key=lambda x: x.get('date', ''), reverse=True)  # Handle potential missing 'date'
        )

        return format_html(
            f"""
            <table style="width:100%; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th style="border: 1px solid #ddd; padding: 8px;">Date</th>
                        <th style="border: 1px solid #ddd; padding: 8px;">Amount</th>
                    </tr>
                </thead>
                <tbody>{table_rows}</tbody>
            </table>
            """
        )

        formatted_withdrawal_history.short_description = 'Withdrawal History'