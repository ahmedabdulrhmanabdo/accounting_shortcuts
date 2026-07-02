import os

import frappe


def after_install():
    ensure_apps_txt_integrity()


def ensure_apps_txt_integrity():
    """bench get-app / new-app regenerates sites/apps.txt from its own registry
    (sites/apps.json) and silently drops apps that were installed manually.
    Frappe's Jinja loader only searches apps listed in apps.txt, so a dropped
    app makes every one of its website pages fail with TemplateNotFound (500).

    Re-add any app that is installed on this site but missing from apps.txt.
    """
    apps_txt = os.path.join(frappe.local.sites_path, "apps.txt")
    try:
        with open(apps_txt) as f:
            listed = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return

    missing = [app for app in frappe.get_installed_apps() if app not in listed]
    if not missing:
        return

    with open(apps_txt, "a") as f:
        for app in missing:
            f.write(app + "\n")

    frappe.clear_cache()
    print(f"accounting_shortcuts: restored missing apps to apps.txt: {', '.join(missing)}")
