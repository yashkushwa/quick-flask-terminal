
#!/bin/bash

# Make scripts executable
chmod +x app.py
chmod +x download_libs.py
chmod +x run.sh

# Create necessary directories
mkdir -p static/js static/css templates

# Download JavaScript libraries
python download_libs.py

echo "Setup complete! Run './run.sh' to start the terminal."
