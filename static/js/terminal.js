
document.addEventListener('DOMContentLoaded', () => {
    // Initialize terminal
    const terminal = new Terminal({
        cursorBlink: true,
        theme: {
            background: '#1e1e1e',
            foreground: '#f0f0f0',
            cursor: '#f0f0f0',
            cursorAccent: '#1e1e1e',
            selection: 'rgba(255, 255, 255, 0.3)',
        },
        fontFamily: 'Menlo, Consolas, "DejaVu Sans Mono", monospace',
        fontSize: 14,
        lineHeight: 1.2,
        rendererType: 'canvas',
        scrollback: 10000,
        allowTransparency: true
    });

    // Terminal addons
    const fitAddon = new FitAddon.FitAddon();
    const webLinksAddon = new WebLinksAddon.WebLinksAddon();
    
    terminal.loadAddon(fitAddon);
    terminal.loadAddon(webLinksAddon);
    
    // Open terminal
    terminal.open(document.getElementById('terminal'));
    
    // Connect to Socket.IO server
    const socket = io.connect(window.location.origin, {
        transports: ['websocket']
    });
    
    // Unique ID for this terminal session
    const terminalId = 'terminal_' + Date.now();
    
    // Terminal events
    socket.on('connect', () => {
        // Create a new terminal on the server
        socket.emit('create_terminal', {
            terminal_id: terminalId,
            rows: terminal.rows,
            cols: terminal.cols
        });
        
        terminal.writeln('Connected to terminal server');
        terminal.writeln('Type commands below...');
        terminal.writeln('');
    });
    
    socket.on('disconnect', () => {
        terminal.writeln('\r\nDisconnected from server. Please refresh to reconnect.');
    });
    
    socket.on(`terminal_output_${terminalId}`, (data) => {
        terminal.write(data.output);
    });
    
    // Terminal input
    terminal.onData(data => {
        socket.emit('terminal_input', {
            terminal_id: terminalId,
            input: data
        });
    });
    
    // Terminal resize
    terminal.onResize(size => {
        socket.emit('resize_terminal', {
            terminal_id: terminalId,
            rows: size.rows,
            cols: size.cols
        });
    });
    
    // Fit terminal to container
    const fitTerminal = () => {
        try {
            fitAddon.fit();
            socket.emit('resize_terminal', {
                terminal_id: terminalId,
                rows: terminal.rows,
                cols: terminal.cols
            });
        } catch (err) {
            console.error('Error fitting terminal:', err);
        }
    };
    
    // Initial fit
    setTimeout(fitTerminal, 100);
    
    // Handle window resize
    window.addEventListener('resize', fitTerminal);
    
    // Button handlers
    document.getElementById('clearBtn').addEventListener('click', () => {
        terminal.clear();
    });
    
    document.getElementById('resizeBtn').addEventListener('click', fitTerminal);
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        socket.emit('destroy_terminal', {
            terminal_id: terminalId
        });
    });
});
