# Project Status

- Created `base.html` as the main template.
- The `base.html` template includes a navigation bar.
- The navigation bar displays "Register" and "Login" links for unauthenticated users.
- For authenticated users, the navbar shows the username and a "Logout" link.
- A `{% block content %}` is included in `base.html` for child templates.
- The template is linked to `static/css/style.css`.
- Verified that `register`, `login`, and `logout` URLs are defined in `learning/urls.py`.
- Installed Django and applied database migrations.
- Applied a new dark theme to `static/css/style.css` with custom colors, typography, layout, and component styling.
- Updated `base.html` to use the new CSS classes for navigation, main content, and footer.
- Updated `subject_list.html` to use the new card-based layout for displaying subjects.
- Updated `registration/login.html` and `registration/register.html` to use the new form styling with `form-group` and `form-control` classes.
- Centered input boxes within forms by applying `flexbox` properties to the form elements in `static/css/style.css`.
- Centered the `.card` element horizontally on the page by setting `margin: 16px auto;` and `max-width: 600px;` in `static/css/style.css`.