import frappe


def get_customer_home_page(user):
    """Send any logged-in System User to the accounting dashboard."""
    if user in ('Administrator', 'Guest'):
        return None
    try:
        u = frappe.get_doc('User', user)
        if u.user_type == 'System User':
            return 'saas-home'
    except Exception:
        pass
    return None
