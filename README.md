# 💬 Real-Time Chat Application

A real-time private chat application built using **Django** and **Django Channels**.  
This project supports instant messaging, read receipts, typing indicators, and online/offline user status using WebSockets.

---

## 🚀 Features

- 🔐 User Authentication (Login / Logout)
- 👥 Active user listing
- 💬 Real-time private messaging
- 👀 Read receipts (Seen status)
- ✍️ Typing indicator
- 🟢 Online / Offline status
- 📩 Unread message counter
- 🗑️ Soft delete messages
- ⚡ WebSocket communication using Django Channels

---

## 🛠️ Tech Stack

- Python
- Django
- Django Channels
- WebSockets
- HTML / CSS / JavaScript
- SQLite (default) / PostgreSQL (optional)

---

## 📦 Installation Guide

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Ajith027/zybo_chatapp.git
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Apply Migrations

```bash
python manage.py migrate
```

### 5️⃣ Create Superuser

```bash
python manage.py createsuperuser
```

### 6️⃣ Run Application (Using Daphne for Channels)

Since this project uses **Django Channels**, the application runs using **Daphne (ASGI server)** instead of the default Django development server.

```bash
daphne -p 8000 chat_app.asgi:application
```

Now open:

```
http://127.0.0.1:8000/
```

---

## ⚙️ How It Works

- Uses **Django Channels** for handling WebSocket connections.
- Each private chat creates a unique room between two users.
- Messages are stored in the database.
- WebSocket groups broadcast messages instantly.
- Unread message count updates dynamically.
- Read receipts update when chat window opens.
- Soft delete is handled using an `is_deleted` flag.

---

## Project Structure
```
chat_app/          # Django project settings
    asgi.py       # ASGI config with Channels
    settings.py   # App settings
    urls.py       # Root URL config
chat/             # Main application
    models.py     # User + Message models
    views.py      # HTTP views (MVT)
    consumers.py  # WebSocket consumer
    routing.py    # WS URL routing
    forms.py      # Auth forms
    admin.py      # Admin config
    urls.py       # App URL patterns
templates/        # Django templates (MVT)
    base.html
    register.html
    login.html
    user_list.html
    chat.html
static/
    css/style.css
    js/chat.js
```

---

## 🖼️ Screenshots

_Add screenshots here if available._

```
/screenshots/chat_page.png
/screenshots/user_list.png
```

---

## 🔮 Future Improvements

- Group Chat Support
- Message Reactions (Like, Emoji)
- File & Image Sharing
- Message Search
- Deployment using Redis + Daphne
- Docker Support

---

## 👤 Author

**Ajith N A**  
Backend Developer  

---

## 📌 Notes

This project is built for learning and demonstration purposes.  
It showcases real-time communication using Django Channels and WebSockets.

