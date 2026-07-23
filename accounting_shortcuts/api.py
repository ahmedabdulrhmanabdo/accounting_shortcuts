import frappe
import random
import string
import json


# ── OTP / Auth ──────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def send_otp(email):
	email = email.strip().lower()
	if not frappe.utils.validate_email_address(email):
		frappe.throw("البريد الإلكتروني غير صحيح")
	otp = "".join(random.choices(string.digits, k=6))
	frappe.cache().set_value(f"acct_otp_{email}", otp, expires_in_sec=600)
	frappe.sendmail(
		recipients=[email],
		subject="كود التحقق — نظام المحاسبة",
		message=f"""<div dir="rtl" style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px;background:#f0fdf4;border-radius:12px;border:1px solid #d1fae5">
		<h2 style="color:#14532d;margin-bottom:8px">كود التحقق</h2>
		<p style="color:#374151;margin-bottom:24px">أدخل هذا الكود لإكمال إنشاء حسابك:</p>
		<div style="font-size:36px;font-weight:700;letter-spacing:8px;color:#14532d;background:#dcfce7;padding:16px 24px;border-radius:8px;text-align:center">{otp}</div>
		<p style="color:#6b7280;font-size:13px;margin-top:16px">ينتهي خلال 10 دقائق. لا تشاركه مع أحد.</p></div>""",
	)
	return {"status": "sent"}


@frappe.whitelist(allow_guest=True)
def verify_otp(email, otp):
	email = email.strip().lower()
	stored = frappe.cache().get_value(f"acct_otp_{email}")
	if stored and str(stored) == str(otp).strip():
		frappe.cache().set_value(f"acct_verified_{email}", True, expires_in_sec=600)
		frappe.cache().delete_value(f"acct_otp_{email}")
		return {"status": "verified"}
	return {"status": "invalid"}


@frappe.whitelist(allow_guest=True)
def create_account(email, phone, password, full_name=None):
	email = email.strip().lower()
	if not frappe.cache().get_value(f"acct_verified_{email}"):
		frappe.throw("انتهت صلاحية التحقق — أعد إرسال الكود")
	if frappe.db.exists("User", email):
		frappe.throw("البريد الإلكتروني مسجّل مسبقاً")
	if frappe.db.exists("User", {"mobile_no": phone}):
		frappe.throw("رقم الجوال مسجّل مسبقاً")
	user = frappe.get_doc({
		"doctype": "User",
		"email": email,
		"first_name": full_name or phone,
		"mobile_no": phone,
		"new_password": password,
		"send_welcome_email": 0,
		"roles": [{"role": "Accounts User"}],
	})
	user.flags.ignore_permissions = True
	user.insert()
	frappe.cache().delete_value(f"acct_verified_{email}")
	from frappe.auth import LoginManager
	lm = LoginManager()
	lm.authenticate(user=email, pwd=password)
	lm.post_login()
	return {"status": "created"}


@frappe.whitelist(allow_guest=True)
def login_by_phone(phone, password):
	phone = phone.strip()
	email = frappe.db.get_value("User", {"mobile_no": phone}, "email")
	if not email:
		frappe.throw("رقم الجوال غير مسجّل", frappe.AuthenticationError)
	from frappe.auth import LoginManager
	lm = LoginManager()
	lm.authenticate(user=email, pwd=password)
	lm.post_login()
	return {"status": "ok"}


# ── Company & User Info ──────────────────────────────────────────────────────

@frappe.whitelist()
def get_company_info():
	company_name = (
		frappe.defaults.get_user_default("company")
		or frappe.defaults.get_global_default("company")
	)
	if not company_name:
		companies = frappe.get_all("Company", limit=1, order_by="creation asc")
		company_name = companies[0].name if companies else ""
	if not company_name:
		return {"name": "", "abbr": "", "currency": "SAR"}
	c = frappe.get_doc("Company", company_name)
	return {
		"name": c.company_name,
		"abbr": c.abbr or "",
		"currency": c.default_currency or "SAR",
	}


# ── Customer ─────────────────────────────────────────────────────────────────

@frappe.whitelist()
def create_customer_quick(customer_name, phone, email=None, notes=None, payment_terms=None):
	doc = frappe.get_doc({
		"doctype": "Customer",
		"customer_name": customer_name,
		"customer_type": "Individual",
		"mobile_no": phone,
		"email_id": email or "",
		"payment_terms": payment_terms or "",
	})
	doc.flags.ignore_permissions = True
	doc.insert()
	return {"name": doc.name, "customer_name": doc.customer_name}


@frappe.whitelist()
def get_customer_list(search=None):
	filters = {}
	if search:
		filters["customer_name"] = ["like", f"%{search}%"]
	rows = frappe.get_all(
		"Customer",
		fields=["name", "customer_name", "mobile_no"],
		filters=filters,
		limit=30,
		order_by="modified desc",
	)
	return rows


# ── Items ────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_item_list(search=None):
	filters = {"disabled": 0, "is_sales_item": 1}
	if search:
		filters["item_name"] = ["like", f"%{search}%"]
	rows = frappe.get_all(
		"Item",
		fields=["name", "item_name", "standard_rate", "stock_uom"],
		filters=filters,
		limit=30,
		order_by="modified desc",
	)
	return rows


# ── Sales Invoice ────────────────────────────────────────────────────────────

@frappe.whitelist()
def create_sales_invoice(customer, items, posting_date=None, notes=None, apply_vat=0):
	if isinstance(items, str):
		items = json.loads(items)

	inv_items = []
	for it in items:
		inv_items.append({
			"item_name": it.get("item_name") or it.get("description"),
			"item_code": it.get("item_code") or it.get("item_name"),
			"description": it.get("item_name") or it.get("description"),
			"qty": float(it.get("qty", 1)),
			"rate": float(it.get("rate", 0)),
			"uom": it.get("uom", "Nos"),
		})

	taxes = []
	if int(apply_vat):
		account = frappe.db.get_value(
			"Account",
			{"account_type": "Tax", "tax_rate": 15},
			"name",
		)
		if not account:
			account = frappe.db.get_value(
				"Account",
				{"account_name": ["like", "%ضريبة%"], "account_type": "Tax"},
				"name",
			)
		if account:
			taxes = [{"charge_type": "On Net Total", "account_head": account, "rate": 15, "description": "ضريبة القيمة المضافة 15%"}]

	inv = frappe.get_doc({
		"doctype": "Sales Invoice",
		"customer": customer,
		"posting_date": posting_date or frappe.utils.today(),
		"items": inv_items,
		"taxes": taxes,
		"remarks": notes or "",
	})
	inv.flags.ignore_permissions = True
	inv.insert()
	return {
		"name": inv.name,
		"total": inv.total,
		"grand_total": inv.grand_total,
		"taxes_and_charges_added": inv.total_taxes_and_charges,
	}
