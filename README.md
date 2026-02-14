# Documents Exp

> Russian version available: [README_RU.md](README_RU.md)

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Framework](https://img.shields.io/badge/Framework-PyQt5-39a)
![Architecture](https://img.shields.io/badge/Architecture-MVC-orange)
![License](https://img.shields.io/badge/License-MIT-success)

Desktop client application for searching, storing, and managing enterprise documentation. Built with Python and PyQt5, utilizing a robust MVC architecture and communicating with a remote REST API.

---

## 🖼 Screenshots

### Authorization window:

Secure login screen with auto-login capability. Supports Guest mode for read-only access.

![auth_window](screenshots/auth.png)

### Main Window:

Displays the hierarchy of Departments and Categories. Features a document table with infinite scrolling and search.

![main_window](screenshots/main.png)

### Document Editor:

Allows authorized users to create, edit, and manage document pages. Supports drag-and-drop reordering.

![editor_window](screenshots/editor.png)

---

## 📌 Overview

**Documents Exp** is designed to streamline the management of technical documentation within an organization. It provides a structured view of documents categorized by departments and allows for efficient searching and editing.

The application ensures data consistency by interacting with a central REST API and supports different access modes for guests and authorized personnel.

---

## 🎯 Key Features

### ✅ Document Management

- **Hierarchy:** Organized by **Departments** and **Categories**.
- **Navigation:** Sidebar navigation with badge counters.
- **Search:** Real-time search by document code or name with debounce.
- **Sorting:** "Natural Sort" order for intuitive code listing.
- **Pagination:** Infinite scrolling for large datasets.

### ✅ Two Access Modes

#### 🔐 Authorized Mode

- Full access to **Create**, **Edit**, and **Delete** documents.
- Manage structure (Departments/Categories).
- Import/Export functionality.

#### 👤 Guest Mode

- Read-only access.
- Search and view documents.
- No editing privileges.

### ✅ Document Editor

- **Page Management:** Add, Edit, Duplicate, and Delete pages.
- **Drag-and-Drop:** Reorder pages intuitively.
- **Word Integration:**
    - **Import:** Parse pages directly from `.docx` tables.
    - **Export:** Generate formatted `.docx` files.
- **Printing:** Built-in printing support.

### ✅ Security & Auth

- **JWT Authentication:** Secure Access/Refresh token flow.
- **Auto-Login:** Secure session persistence using system **Keyring**.
- **Account Management:** Sign up, Email verification, Password reset.

### ✅ UI/UX Highlights

- **Modern Interface:** Clean PyQt5 design.
- **Theming:** Dynamic **Light** and **Dark** themes (Jinja2 generated).
- **Responsiveness:** Adaptive layouts.
- **Feedback:** Toast notifications for user actions.

---

## 🧩 Who is this for?

✅ **Engineering Departments**: For storing technical specifications and drawings.  
✅ **Enterprises**: To maintain a centralized repository of documentation.  
✅ **Managers**: To organize workflow and document structure.

---

## 🧠 What this project demonstrates

✅ **MVC Architecture**: Strict separation of concerns (Model-View-Controller).  
✅ **PyQt5 Mastery**: Custom widgets, signals/slots, event filtering, animations.  
✅ **Asynchronous Programming**: Non-blocking UI using `QThread` for API calls.  
✅ **REST API Integration**: Robust HTTP client with session handling and error management.  
✅ **Security Best Practices**: Safe token storage and validation.  
✅ **Dynamic Theming**: Using template engines (Jinja2) for QSS generation.

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

## 📂 Project Structure

```
DOCUMENTS-EXP-DESKTOP/
│ app.py
│ config.yaml
│ requirements.txt
│ README.md
│
├─ api/
│ └─ api_client.py
│
├─ core/
│ └─ worker.py
│
├─ modules/
│ ├─ auth/
│ ├─ main/
│ ├─ document_editor/
│ ├─ departments_editings/
│ └─ categories_editings/
│
├─ resources/
│ ├─ icons/
│ ├─ logo/
│ ├─ slides/
│ └─ templates/
│
├─ ui/
│ ├─ custom_widgets/
│ ├─ styles/
│ └─ ui_converted/
│
└─ utils/
  ├─ notifications/
  └─ ...
```

---

## 🔒 Security Model

✅ JWT Authentication  
✅ Secure token storage (Keyring)  
✅ No plaintext password saving  
✅ Session management  
✅ Safe for internal distribution

---

## 🚦 Project Status

✅ Active  
✅ Under active development  
✅ New features planned  
✅ Regular updates

---

## 📜 License

MIT License

Copyright (c) 2025 Pavel (PN Tech)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 👤 Author

**Pavel (PN Tech)**
Python desktop and web developer, UI/UX designer, electronics engineer
