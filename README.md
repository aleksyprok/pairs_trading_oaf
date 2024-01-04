# Introduction:

In this release, our focus is to centralize the fundamental pairs trading strategies within this repository. This effort is aimed at simplifying the comparison of different strategies and to facilitate easier collaboration across our team. By bringing these strategies together in one place, we make it more convenient for team members to access, compare, and contribute to the development of these trading methods. This repository serves as a central hub for our ongoing efforts in refining and enhancing pairs trading strategies.

# Installation instructions:

1. Install Python3.9 or greater.
2. Create a virtual environment with e.g. `python -m venv venv`
3. Activte the environment.
4. Install packages in `requirements.txt` with e.g. `pip install -r requirements.txt`

# Executing code:

1. Enter the pairs_trading_oaf diretory.
2. Execute main.py using e.g. `python main.py`.

# File Structure Overview:

- `.github/workflows`: Contains the .yml which directs the automatic testing.
- `pairs_trading_oaf`: The main application directory.
  - `main.py`: The entry point of the application.
  - `plotting.py`: Utility functions for data visualization.
  - `trading.py`: Core trading logic and functions.
- `tests`: Test cases for the application.
  - `test_trading.py`: Tests for the trading module.
- `.gitignore`: Specifies files to be ignored in Git version control.
- `README.md`: The file you are currently reading, with instructions and information about this project.
- `requirements.txt`: Lists all Python dependencies.
- `setup.py`: A script for setting up the application.

# Developer Advice

- **Issue Tracking for New Features**: Before adding new features, you are encouraged to raise an issue in the repository. This helps in tracking requests and discussions. When creating a new branch for the feature, include the issue number in the branch name for easy reference.

- **Code Style and Linting**: You are encouraged to follow the PyLint linting style to maintain code quality and consistency. You can install the PyLint package directly into Visual Studio Code to aid in adhering to these standards.
