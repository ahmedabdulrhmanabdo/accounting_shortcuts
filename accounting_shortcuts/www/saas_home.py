import frappe
from frappe.utils import nowdate, get_first_day


def get_context(context):
    user = frappe.session.user
    if user == 'Guest':
        frappe.local.flags.redirect_location = '/login'
        raise frappe.Redirect

    u = frappe.get_doc('User', user)
    context.user_fullname = u.full_name or user
    context.user_initial = (u.full_name or user)[0]

    # الوحدات المفعّلة: لو فيه جدول "Block Module" على المستخدم (مضاف من تطبيق
    # SaaS billing) نحترمه، غير كذا نعرض كل الوحدات القياسية
    all_modules = ['Accounts', 'Selling', 'Buying', 'Stock', 'HR', 'Payroll']
    try:
        blocked_modules = set(row.module for row in u.block_modules)
    except Exception:
        blocked_modules = set()
    context.enabled_modules = [m for m in all_modules if m not in blocked_modules]

    try:
        company = frappe.db.get_single_value('Global Defaults', 'default_company') or ''
        context.company_abbr = (frappe.db.get_value('Company', company, 'abbr') if company else None) or (company[:8] if company else '')
    except Exception:
        context.company_abbr = ''

    today = nowdate()
    month_start = get_first_day(today)

    def fmt(v):
        try:
            return '{:,.0f}'.format(float(v or 0))
        except Exception:
            return '0'

    try:
        cash_balance = frappe.db.sql("""
            SELECT IFNULL(SUM(debit - credit), 0)
            FROM `tabGL Entry`
            WHERE account IN (
                SELECT name FROM `tabAccount`
                WHERE account_type IN ('Cash', 'Bank') AND is_group = 0
            ) AND is_cancelled = 0
        """)[0][0] or 0
    except Exception:
        cash_balance = 0

    try:
        total_sales = frappe.db.sql("""
            SELECT IFNULL(SUM(grand_total), 0) FROM `tabSales Invoice`
            WHERE docstatus = 1 AND posting_date BETWEEN %s AND %s
        """, (month_start, today))[0][0] or 0
    except Exception:
        total_sales = 0

    try:
        total_purchases = frappe.db.sql("""
            SELECT IFNULL(SUM(grand_total), 0) FROM `tabPurchase Invoice`
            WHERE docstatus = 1 AND posting_date BETWEEN %s AND %s
        """, (month_start, today))[0][0] or 0
    except Exception:
        total_purchases = 0

    try:
        today_invoices = frappe.db.count('Sales Invoice', {'posting_date': today, 'docstatus': ['!=', 2]})
    except Exception:
        today_invoices = 0

    try:
        recent_invoices = frappe.db.sql("""
            SELECT name, customer, posting_date, status, grand_total,
                   CONCAT(FORMAT(grand_total, 0), ' ر.س') as grand_total_fmt
            FROM `tabSales Invoice`
            WHERE docstatus != 2
            ORDER BY posting_date DESC, creation DESC
            LIMIT 10
        """, as_dict=True)
    except Exception:
        recent_invoices = []

    context.cash_balance_fmt = fmt(cash_balance)
    context.total_sales_fmt = fmt(total_sales)
    context.total_purchases_fmt = fmt(total_purchases)
    context.today_invoices = today_invoices or 0
    context.recent_invoices = recent_invoices
    context.no_cache = 1
