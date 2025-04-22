
#!/usr/bin/env python
import os
import urllib.request

# Create directories if they don't exist
os.makedirs('static/js', exist_ok=True)

# URLs for the libraries
libraries = {
    'static/js/xterm.min.js': 'https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.min.js',
    'static/js/xterm-addon-fit.min.js': 'https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.min.js',
    'static/js/xterm-addon-web-links.min.js': 'https://cdn.jsdelivr.net/npm/xterm-addon-web-links@0.9.0/lib/xterm-addon-web-links.min.js',
    'static/js/socket.io.min.js': 'https://cdn.socket.io/4.7.4/socket.io.min.js'
}

print("Downloading required libraries...")

for path, url in libraries.items():
    try:
        print(f"Downloading {url} to {path}...")
        urllib.request.urlretrieve(url, path)
        print(f"Successfully downloaded {path}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

print("Download complete!")
