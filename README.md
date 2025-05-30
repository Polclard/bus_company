# 🚌 Django Bus Company Application

Welcome to the **Django Bus Company Application**! This is a web-based platform that allows bus companies to manage buses, routes, and trips while providing users with an easy way to browse available trips.

## 🚀 Features

- ✅ **Manage Bus Companies** – Add and manage bus companies.
- ✅ **Bus Management** – Register buses and assign them to companies.
- ✅ **Route Management** – Define start and end locations for routes.
- ✅ **Ticket Management** – Schedule trips with departure times and prices.
- ✅ **Django Admin Panel** – Easily manage data via Django's built-in admin.
- ✅ **User-Friendly Interface** – Browse trips via a simple web UI.

## 🏗️ Installation

### 1️⃣ Clone the Repository

```sh
git clone https://github.com/Polclard/bus_company.git
cd django-bus-company
```

### 2️⃣ Create a Virtual Environment & Install Dependencies

```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3️⃣ Configure Database & Migrate Models

- This project on development uses postgresql so first open settings.py in /bus_company/settings.py and then configure this part by creating .env file or passing the values directly to the fields
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_NAME'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}
```
After changing this to match your local database settings and values you can proceed.

```sh
python manage.py makemigrations
python manage.py migrate
```

### 4️⃣ Create a Superuser

```sh
python manage.py createsuperuser
```

Follow the prompts to set up an admin user.

### 5️⃣ Run the Development Server

```sh
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the app.

## 🔗 API Endpoints

```python
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),  # new
    path("accounts/", include("django.contrib.auth.urls")),
    path("check-route/", views.check_route, name="check_route"),
    path('routes/', views.routes_list, name='routes_list'),
    path('busses/', views.busses, name='busses'),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("buy_ticket/<int:bus_id>/", views.buy_ticket, name="buy_ticket"),
    path("tickets/<int:user_id>/", views.tickets, name="tickets"),
    path("delete_ticket/<int:ticket_id>/", views.delete_ticket, name="delete_ticket"),
```

| Method | Endpoint       | Description       |
| ------ | -------------- | ----------------- |
| GET    | `/busses/`     | Get all busses    |
| POST   | `/buy_ticket{id}/` | By a new ticket   |
| GET    | `/trips/{id}/` | Get trip details  |
| PUT    | `/trips/{id}/` | Update a trip     |
| DELETE | `/trips/{id}/` | Delete a trip     |

## 📂 Project Structure

```
📁 bus_company
 ┣ 📁 buses          # Django app for bus management
 ┃ ┣ 📁 migrations  # Database migrations
 ┃ ┣ 📜 models.py   # Database models
 ┃ ┣ 📜 views.py    # Views for rendering data
 ┃ ┣ 📜 urls.py     # URL routing
 ┃ ┗ 📜 serializers.py # API serializers
 ┣ 📜 manage.py     # Django project management
 ┗ 📜 requirements.txt # Required dependencies
```

## 🌎 Deployment

To deploy the app, configure a production-ready database like PostgreSQL and use services like:

- **Python Anywhere**

## 🤝 Contributing

Contributions are welcome! Feel free to submit pull requests or report issues.

## 📜 License

This project is licensed under the MIT License. See `LICENSE` for details.

---

🎉 Happy coding & safe travels! 🚍

