
#!/bin/bash

# Make sure the script is executable
chmod +x app.py

# Check if requirements are installed
if ! pip list | grep -q "flask"; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Check if JS libraries are downloaded
if [ ! -f "static/js/xterm.min.js" ]; then
    echo "Downloading JavaScript libraries..."
    python download_libs.py
fi

# Make directories if they don't exist
mkdir -p static/js static/css templates

# Start the application
echo "Starting Flask Terminal on port 8080..."
python app.py
