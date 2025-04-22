
# Python Flask Terminal

A web-based terminal that runs in your browser, powered by Flask and xterm.js.

## Features

- Real-time terminal emulation in your browser
- Full support for ANSI escape sequences and colors
- Resizable terminal interface
- Clean, modern UI
- Runs on port 8080 by default

## Requirements

- Python 3.7+
- Flask and other dependencies (listed in requirements.txt)

## Installation

1. Clone or download this repository

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Download the required JavaScript libraries:

```bash
python download_libs.py
```

## Usage

1. Start the server:

```bash
python app.py
```

2. Open your web browser and navigate to:

```
http://localhost:8080
```

3. You should now see the terminal interface in your browser and can start typing commands.

## Structure

- `app.py`: Flask application with WebSocket support for the terminal
- `templates/index.html`: Main HTML template for the terminal interface
- `static/css/`: CSS styles for the terminal
- `static/js/`: JavaScript files for terminal functionality
- `download_libs.py`: Helper script to download required JavaScript libraries

## Notes

- The terminal runs with the permissions of the user who started the Flask application
- For security reasons, consider running this within a container or with restricted permissions

## Troubleshooting

- If you encounter WebSocket connection issues, make sure no firewall is blocking port 8080
- For permission errors, check that your user has the necessary permissions to execute commands
