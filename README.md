# 🚌 Django Bus Company Application

Welcome to the **Django Bus Company Application**! This is a web-based platform that allows bus companies to manage buses, routes, and trips while providing users with an easy way to browse available trips.

## 🚀 Features

- ✅ **Manage Bus Companies** – Add and manage bus companies.
- ✅ **Bus Management** – Register buses and assign them to companies.
- ✅ **Route Management** – Define start and end locations for routes.
- ✅ **Trip Management** – Schedule trips with departure times and prices.
- ✅ **Django Admin Panel** – Easily manage data via Django's built-in admin.
- ✅ **REST API** – Access data programmatically with Django REST Framework.
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

| Method | Endpoint       | Description       |
| ------ | -------------- | ----------------- |
| GET    | `/trips/`      | Get all trips     |
| POST   | `/trips/`      | Create a new trip |
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

- **Heroku**
- **DigitalOcean**
- **AWS Elastic Beanstalk**
- **Railway.app**

## 🤝 Contributing

Contributions are welcome! Feel free to submit pull requests or report issues.

## 📜 License

This project is licensed under the MIT License. See `LICENSE` for details.

---

🎉 Happy coding & safe travels! 🚍

