# Documents Exp

> Russian version available: [README_RU.md](README_RU.md)

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Framework](https://img.shields.io/badge/Framework-PyQt5-39a)
![Architecture](https://img.shields.io/badge/Architecture-MVC-orange)
![License](https://img.shields.io/badge/License-MIT-success)

Desktop client application for searching, storing, and managing enterprise documentation and its content. The application interacts with a remote REST API and supports different access levels.

---

## 🖼 Screenshots

### Authorization

Secure login screen with auto-login capability. Supports Guest mode for read-only access.

![auth_window](screenshots/auth.png)

### Main Window

Displays the hierarchy of Departments and Categories. Features a document table with infinite scrolling and search.

![main_window](screenshots/main.png)

### Document Editor

Allows authorized users to create, edit, and manage document pages. Supports drag-and-drop reordering.

![editor_window](screenshots/editor.png)

---

## 📌 Overview

**Documents Exp** is designed to streamline the management of technical documentation within an organization. It provides a structured view of documents categorized by departments and allows for efficient searching and editing.

The application operates in two modes:

1.  **Guest Mode:** View and search documents only.
2.  **User Mode:** Full access to create, edit, delete, import, and export documents.

---

## 🎯 Key Features

### ✅ Document Management

- Organized by **Departments** and **Categories**.
- **Infinite scrolling** for large document lists.
- **Search** functionality with filtering.

### ✅ Document Editor

- Create and edit documents.
- Manage pages: **Add**, **Duplicate**, **Delete**.
- Drag-and-drop page reordering.

### ✅ Import & Export

- **Import** pages from `.docx` files (Word).
- **Export** documents to `.docx` format.
- **Print** documents directly from the application.

### ✅ UI/UX

- Modern **PyQt5** interface.
- **Dark** and **Light** themes.
- Responsive sidebar and navigation.
- Toast notifications for user actions.

### ✅ Security

- Secure token storage using system **Keyring**.
- Auto-login functionality.
- Password reset flow via email.

---

## 🏗 Architecture

The project follows the **MVC (Model-View-Controller)** pattern to ensure separation of concerns and maintainability.

```
┌──────┐     ┌────────────┐     ┌───────┐
│ View │ <-- │ Controller │ --> │ Model │
└──────┘     └────────────┘     └───────┘
  UI           Logic            Data/API
```

- **View:** Handles UI rendering and user events (PyQt5).
- **Controller:** Orchestrates logic, handles signals, and communicates between View and Model.
- **Model:** Manages data, API communication, and business logic.

---

## 🛠 Tech Stack

- **Language:** Python 3.14
- **GUI Framework:** PyQt5
- **API Communication:** Requests (with Session handling)
- **Security:** Keyring (for token storage)
- **Templating:** Jinja2 (for dynamic QSS generation)
- **Document Handling:** python-docx

---

## 🔧 Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-repo/documents-exp-desktop.git
    cd documents-exp-desktop
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Configure the application:
   Edit `config.yaml` to set your API URL:

    ```yaml
    base_url: "http://127.0.0.1:8000"
    ```

4. Run the application:
    ```bash
    python app.py
    ```

---

## 👤 Author

**Pavel (PN Tech)**
