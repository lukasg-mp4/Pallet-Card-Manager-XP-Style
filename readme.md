# Enterprise Inventory & Pallet Card Manager

A robust desktop application designed for efficient inventory management, data manipulation, and physical label generation. This project demonstrates a custom-built graphical user interface (GUI) engine designed to replicate the Windows XP aesthetic while providing modern functionality through a modular Model-View-Controller (MVC) architecture.

## Project Overview

This application serves as a centralized tool for warehouse or inventory environments. It allows users to manage multiple sheets of inventory data, import external datasets via Excel, track modification history, and interface directly with Windows print spoolers for precise label generation.

The software was originally developed as a monolithic script and has been extensively refactored into a scalable, object-oriented codebase to ensure maintainability and extensibility.

## Key Features

* **Custom UI Engine:** A high-performance, canvas-based rendering engine built on Tkinter. It draws custom grids, headers, and window controls (Title Bars, Resize Handles) to strictly adhere to a specific visual design language (Windows XP) independent of the host OS theme.
* **Multi-Sheet Architecture:** Supports dynamic creation, renaming, and deletion of multiple inventory sheets with independent state management.
* **Excel Integration:** Utilizes Pandas for robust importing of complex Excel datasets, including automatic header detection and data cleaning.
* **Win32 GDI Printing:** Bypasses standard high-level printing dialogs to use the Windows GDI (Graphics Device Interface) via PyWin32. This ensures pixel-perfect physical alignment for thermal label printers.
* **Session History & Persistence:** Implements a custom undo/redo stack and a global history log that persists between sessions via JSON serialization.
* **Keyboard Navigation:** Full support for keyboard-centric workflows, including navigation, shortcuts, and bulk editing.

## Technical Architecture

The project follows a strict **Model-View-Controller (MVC)** separation of concerns:

### 1. Presentation Layer (UI)

Located in the `UI/` directory. This layer handles all visual elements and user input. It contains no business logic.

* **XP_Styling:** Contains low-level UI definitions, custom title bars, and window management logic using `ctypes` for native Windows behavior (Taskbar grouping, window styles).
* **Sheet_Editor:** A custom grid widget responsible for rendering thousands of cells efficiently using a canvas coordinate system rather than instantiating thousands of individual widgets.

### 2. Logic Layer (Util)

Located in the `Util/` directory. This layer acts as the Controller.

* **Hotkeys:** Manages keybinding maps and event propagation.
* **History:** Manages the session state, snapshot logging, and rollback capabilities.
* **Navigation:** Handles focus management between the grid editor and the preview pane.

### 3. Data & Hardware Layer (Managers)

* **Excel_Manager:** Handles file I/O and data parsing using Pandas.
* **Print_Manager:** Interfaces with the Windows Spooler API to handle print jobs and GDI drawing contexts.

## Project Structure

```text
Root/
│
├── main.py                   # Application Entry Point & Integrity Check
├── UI/                       # Presentation Layer
│   ├── Main_Layout/          # Layout Orchestration
│   ├── Sheet_Editor/         # Custom Grid Rendering Engine
│   ├── XP_Styling/           # Custom Window Decorations & Dialogs
│   ├── Tabs/                 # Custom Tab Logic
│   └── Menus/                # Top Menu Bar Implementation
│
├── Util/                     # Application Logic
│   └── UI_Functionality/
│       ├── History/          # Session Logging & Persistence
│       ├── Hotkeys/          # Keyboard Shortcut Management
│       ├── Navigation/       # Focus & Scroll Logic
│       └── Sheets/           # Row/Column Data Operations
│
├── Excel_Manager/            # Data Import Subsystem
└── Print_Manager/            # Win32 Printing Subsystem
```

## Installation and Usage

### Prerequisites

* **Python 3.10 or higher**
* **Windows Operating System (Required for Win32 API calls)**

### Dependencies

**Install the required packages using the provided requirements file:**

pip install -r requirements.txt

**Required libraries include:** **pandas**, **openpyxl**, **pywin32**.


### Running the Application

**Execute the main entry point:**

python main.py



## License and Copyright

**This software is proprietary. Usage is granted via the End User License Agreement (EULA) presented upon the first launch of the application. The software verifies a locally generated license key for integrity on startup.**

**Copyright (c) 2025 Lukas Geciauskas. All Rights Reserved.**
