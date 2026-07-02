import os

import frappe


def after_install():
    ensure_apps_txt_integrity()


def ensure_apps_txt_integrity():
    """bench get-app / new-app / install-app regenerates sites/apps.txt and
    silently drops any app it does not consider valid (bench requires
    hooks.py, modules.txt AND patches.txt to exist). Frappe's Jinja loader
    and module map only include apps listed in apps.txt, so a dropped app
    breaks all its website pages (TemplateNotFound 500) and desk pages
    (Module not found).

    Scan the bench apps directory and re-add every real Frappe app missing
    from apps.txt — not just apps installed on the current site.
    """
    sites_path = os.path.abspath(frappe.local.sites_path)
    apps_txt = os.path.join(sites_path, "apps.txt")
    apps_dir = os.path.join(os.path.dirname(sites_path), "apps")
    try:
        with open(apps_txt) as f:
            listed = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return

    missing = []
    for app in sorted(os.listdir(apps_dir)):
        if app in listed:
            continue
        inner = os.path.join(apps_dir, app, app)
        if os.path.exists(os.path.join(inner, "hooks.py")) and os.path.exists(
            os.path.join(inner, "modules.txt")
        ):
            missing.append(app)

    if not missing:
        return

    with open(apps_txt, "a") as f:
        for app in missing:
            f.write(app + "\n")

    frappe.clear_cache()
    print(f"accounting_shortcuts: restored missing apps to apps.txt: {', '.join(missing)}")
