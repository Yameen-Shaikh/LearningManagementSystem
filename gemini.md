# Project Status

- Created `base.html` as the main template.
- The `base.html` template includes a navigation bar.
- The navigation bar displays "Register" and "Login" links for unauthenticated users.
- For authenticated users, the navbar shows the username and a "Logout" link.
- A `{% block content %}` is included in `base.html` for child templates.
- The template is linked to `static/css/style.css`.
- Verified that `register`, `login`, and `logout` URLs are defined in `learning/urls.py`.
- Installed Django and applied database migrations.