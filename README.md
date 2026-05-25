# Facebook Clone (Flet-Python)

A modern, responsive Facebook UI clone built entirely using the [Flet](https://flet.dev/) framework in Python. This project mimics the mobile application experience within a desktop-friendly phone frame, featuring high-fidelity UI components and seamless navigation.

## 🚀 Features

- **Responsive Design:** Adapts from a centered phone mockup on desktop to a full-screen mobile experience.
- **Multi-View Navigation:**
  - **Home:** Main feed with stories and posts.
  - **Watch:** Video feed simulation.
  - **Groups:** Group discovery and management.
  - **Profile:** User profile information and personal feed.
  - **Notifications:** Activity and alerts.
  - **Menu:** App settings and navigation shortcuts.
- **High-Fidelity Components:**
  - Story cards with interactive feel.
  - Post composer and feed items.
  - Custom status bar and home indicator mockup.
- **Theme Support:** Dynamic Dark/Light mode switching.
- **Modular Architecture:** Clean separation of views, components, and database logic.

## 🛠️ Technology Stack

- **Language:** Python 3.x
- **UI Framework:** [Flet](https://flet.dev/) (powered by Flutter)
- **Database:** JSON-based local storage management.

## 📁 Project Structure

```text
├── components/          # Reusable UI widgets (Story Cards, Post Cards, etc.)
├── database/            # Data management and local JSON DB
├── views/               # Individual page layouts
├── main.py              # Application entry point and layout shell
└── requirements.txt     # Python dependencies
```

## 🏁 Getting Started

### Prerequisites

- Python 3.8 or higher installed.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/NishantJLU/facebook-clone.git
   cd facebook-clone
   ```

2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

Execute the main script to launch the application:
```bash
python main.py
```

## 📸 Screenshots

*(Add screenshots of your application here to make it more appealing!)*

## 🤝 Contributing

Contributions are welcome! If you have suggestions or want to improve the UI/UX, feel free to fork the repo and submit a pull request.

## 📄 License

This project is open-source and available under the MIT License.
