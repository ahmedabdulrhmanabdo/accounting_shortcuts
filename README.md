### Accounting Shortcuts

لوحة تحكم مخصصة لعملاء ERPNext/Frappe — واجهة مبسطة بالعربي والإنجليزي (RTL/LTR) تعرض
اختصارات وإحصائيات محاسبية سريعة، وتفتح نماذج ERPNext الأصلية (فاتورة مبيعات، قيود
يومية، سندات قبض/صرف...) داخل نفس تصميم الداشبورد بدل واجهة Frappe Desk الكاملة.

A custom customer-facing dashboard for ERPNext/Frappe sites. Renders a lightweight
bilingual (Arabic/English, RTL/LTR) shell with quick accounting stats and shortcuts,
and hosts native ERPNext forms (Sales Invoice, Journal Entry, Payment Entry, ...)
inside a controlled iframe with simplified styling — instead of exposing the full
Frappe Desk UI to end customers.

**الصفحة الرئيسية / Entry point:** `/saas-home` (redirects `Guest` → `/login`)

### Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app accounting_shortcuts
```

بعد التثبيت، أي مستخدم من نوع `System User` (غير Administrator) بيتوجه تلقائياً
لـ `/saas-home` عند تسجيل الدخول، عبر hook `get_website_user_home_page`.

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/accounting_shortcuts
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
