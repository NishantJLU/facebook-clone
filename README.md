# 🚀 Facebook UI Clone (Built with Python & Flet)

I’ve always been curious about what goes into making a "big" app feel so smooth. So, I decided to spend some time rebuilding the Facebook UI from scratch using **Python** and **Flet**. 

What started as a simple UI test turned into a full-scale clone. I wanted to see if I could get that native "mobile feel" using Python, and Flet really delivered. This project features a responsive "phone frame" that looks like a real device on your desktop but fits perfectly on a mobile screen.

## 🌟 What’s Under the Hood

- **Responsive Design:** A sleek phone mockup for desktop that seamlessly transitions to a full-screen native experience on mobile.
- **Advanced Navigation:** Full support for Home, Watch, Groups, Profile, Notifications, and Menu views.
- **Interactive UI Components:**
  - **Dynamic Story Viewer:** Active, timed stories with progress bars and smooth transitions.
  - **Enhanced Post Interaction:** Long-press or hover to open the **Reaction Picker Panel** (Like, Love, Haha, Wow, Sad, Angry).
  - **Marketplace:** Fully functional marketplace view with product category filtering and detailed product bottom sheets.
  - **Native Video Player:** Integrated video playback in the Watch view using Flet's native video component.
  - **Post Composer:** Real-time post creation with live image preview support.
- **Real-time Search:** Global search functionality that filters users and posts instantly.
- **Theme Support:** One-tap Dark/Light mode switching with Material 3 color consistency.
- **Flet 0.85+ Optimized:** Fully updated to the latest Flet standards for maximum performance and compatibility.

## 🛠️ Technology Stack

- **Language:** Python 3.9+
- **UI Framework:** [Flet](https://flet.dev/) (Flutter for Python)
- **State Management:** Local state handling with cached views for smooth tab switching.
- **Database:** JSON-based local management with modular `DatabaseManager` logic.
- **CI/CD:** Automated Android APK builds via GitHub Actions.

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

<img width="424" height="891" alt="image" src="https://github.com/user-attachments/assets/a1bc32d1-b6a2-4f27-878b-ebcb6ad1a1f7" />


## 🤝 Contributing

Contributions are welcome! If you have suggestions or want to improve the UI/UX, feel free to fork the repo and submit a pull request.

## 📄 License

This project is open-source and available under the MIT License.
