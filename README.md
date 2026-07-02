### Accounting Shortcuts

لوحة تحكم مخصصة لعملاء ERPNext/Frappe — واجهة مبسطة بالعربي والإنجليزي (RTL/LTR) تعرض
اختصارات وإحصائيات محاسبية سريعة، وتفتح نماذج ERPNext الأصلية (فاتورة مبيعات، قيود
يومية، سندات قبض/صرف...) داخل نفس تصميم الداشبورد بدل واجهة Frappe Desk الكاملة.

A custom customer-facing dashboard for ERPNext/Frappe sites. Renders a lightweight
bilingual (Arabic/English, RTL/LTR) shell with quick accounting stats and shortcuts,
and hosts native ERPNext forms (Sales Invoice, Journal Entry, Payment Entry, ...)
inside a controlled iframe with simplified styling — instead of exposing the full
Frappe Desk UI to end customers.

**الصفحة الرئيسية / Entry point:** `/saas-home` (يحوّل الزائر غير المسجل إلى `/login`)

### المتطلبات / Requirements

- Frappe Framework v15
- ERPNext v15

### التثبيت / Installation

```bash
# 1) ادخل على مجلد الـ bench عندك (المسار الافتراضي)
cd /home/frappe/frappe-bench

# 2) حمّل التطبيق من GitHub
bench get-app https://github.com/ahmedabdulrhmanabdo/accounting_shortcuts --branch main

# 3) ثبّته على موقعك (استبدل site1.local باسم موقعك)
bench --site site1.local install-app accounting_shortcuts

# 4) حدّث الأصول والكاش ثم أعد التشغيل
bench --site site1.local migrate
bench --site site1.local clear-cache
bench restart
```

### بعد التثبيت / After install

- افتح `https://your-site/saas-home` وستظهر لوحة التحكم مباشرة.
- أي مستخدم من نوع `System User` (غير Administrator) يتوجه تلقائياً إلى
  `/saas-home` عند تسجيل الدخول، عبر hook `get_website_user_home_page`.
- زر 🌐 أعلى الصفحة يبدّل اللغة بين العربية (RTL) والإنجليزية (LTR) ويحفظ
  الاختيار في المتصفح.

### بنية الملفات / File structure

```
accounting_shortcuts/
├── accounting_shortcuts/
│   ├── hooks.py                  # get_website_user_home_page hook
│   ├── website_home.py           # توجيه المستخدمين إلى /saas-home
│   └── www/
│       ├── saas-home.html        # واجهة الداشبورد (HTML/CSS/JS)
│       └── saas_home.py          # منطق الصفحة (الإحصائيات وآخر الفواتير)
└── README.md
```

> ملاحظة: ملف البايثون اسمه `saas_home.py` بشرطة سفلية — Frappe يحوّل الشرطات (`-`)
> في اسم الصفحة إلى شرطات سفلية (`_`) عند البحث عن موديول البايثون المرافق.

### إلغاء التثبيت / Uninstall

```bash
cd /home/frappe/frappe-bench
bench --site site1.local uninstall-app accounting_shortcuts
bench restart
```

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

MIT
