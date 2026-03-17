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

![auth_window](screenshots/auth_window.gif)

### Main Window:

Displays the hierarchy of Departments and Categories. Features a document table with infinite scrolling and search.

![main_window](screenshots/main_window.png)

### Document Editor:

Allows authorized users to create, edit, and manage document pages. Support for adding and working with electronic document files. Supports drag-and-drop reordering.

![editor_window](screenshots/document_editor.png)
![editor_window_files](screenshots/document_editor_files.png)

---

## 💡 What's New (v0.2.5) - Settings Compatibility

This patch release improves compatibility and reliability of saved search settings.

### 🛠 Improved

- Migrated legacy search filter settings to the current format automatically.
- Unified default search filter schema with the current main window behavior.
- Added tests for legacy-to-current settings migration and schema consistency.

---

## 💡 What's New (v0.2.0) - Profile & Settings

This update focuses on personalization and user experience.

### 👤 Profile Editing

- **Personal Info:** You can now edit your user information (First Name, Last Name, Department) directly within the application.
- **Access:** The profile dialog is accessible from the main application menu.

### ⚙️ Settings Persistence

- **Personalization:** The application now remembers your preferences on a per-user basis.
- **Theme:** Your selected theme (Light/Dark) is saved between sessions.
- **Filters:** Your most recently used search filters are also saved, speeding up repeated searches.

### ⚡ Also in this update

- Added a dedicated "What's New" changelog window that opens after updates and shows version changes.
- Minor UI improvements and bug fixes for a more stable experience.
- Improved session stability after idle time: document lists and search results no longer disappear if a reload or search request fails.
- Main window startup loading was moved off the UI thread to reduce freezes during the initial data fetch.
- Authentication flows now fail safely if the system keyring or session storage is unavailable.
- API client now correctly handles empty successful responses such as `204 No Content`.
- Logging out now explicitly disables auto-login for the current profile.

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

1. Download the latest installer (`.exe`) from the Releases page.

2. Run the installer and follow the instructions.

3. Configure the application:
   Navigate to the installation directory (usually `%LOCALAPPDATA%\Programs\Documents Exp`).
   Edit `config.yaml` to set your API URL:

    ```yaml
    base_url: "http://127.0.0.1:8000"
    ```

4. Run the application using the desktop shortcut or Start Menu entry.

---

## 📦 Compilation

To build the application into an executable file (EXE):

1. Install PyInstaller:

    ```bash
    pip install pyinstaller
    ```

2. Run the build command using the provided spec file:

    ```bash
    pyinstaller "Documents Exp.spec"
    ```

3. The compiled application will be available in the `dist/Documents Exp` directory.

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
