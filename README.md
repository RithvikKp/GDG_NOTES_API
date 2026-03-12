# GDG Notes Management API

A secure, lightweight backend API built with Flask and SQLite for managing personal notes. This project features token-based authentication (JWT), password hashing, Role-Based Access Control (RBAC), and an optional search enhancement.

## 🚀 Documentation of the Process

Here is the step-by-step development process followed to build this API:

1. **Environment & Tool Selection:** * Selected **Python/Flask** for rapid, lightweight API development.
   * Chose **SQLite** for the database as it requires zero configuration and is highly portable.
   * Configured the local development environment (Kali Linux) to properly handle Python virtual environment/system package constraints for seamless dependency installation.

2. **Database Design:**
   * Built a `User` model with `username`, `password` (hashed), and `role` (user/admin).
   * Built a `Note` model with `title`, `content`, timestamps, and a `user_id` foreign key to establish strict ownership of data.

3. **Authentication & Security:**
   * Implemented `werkzeug.security` (`generate_password_hash` and `check_password_hash`) to securely encrypt passwords before storing them.
   * Integrated `Flask-JWT-Extended` to issue JSON Web Tokens upon successful login. The user's ID and Role are embedded into the token claims to enable stateless authentication.

4. **Core API Logic & RBAC:**
   * Developed secure routing for `/register` and `/login`.
   * Created the `/notes` endpoints (GET, POST, PUT, DELETE) enforcing the `@jwt_required()` decorator.
   * Implemented **Role-Based Access Control (RBAC)**:
     * Regular users are restricted to viewing, editing, and deleting only their own notes via strict `user_id` checks.
     * Admin users bypass the ownership check, granting them the ability to view or delete any note in the system.

5. **Bonus Feature Implementation (Search):**
   * Enhanced the `GET /notes` endpoint to accept a `?search=` query parameter, allowing users to filter their retrieved notes by title using SQLAlchemy's `.ilike()` method.

---

## 🛠️ Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/RithvikKp/GDG_NOTES_API.git](https://github.com/RithvikKp/GDG_NOTES_API.git)
   cd GDG_NOTES_API
