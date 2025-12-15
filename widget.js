(function() {
    // 1. Create the container
    const widgetContainer = document.createElement('div');
    widgetContainer.id = 'trade-vision-root';
    document.body.appendChild(widgetContainer);

    // 2. Inject CSS (So it doesn't clash with their website)
    const style = document.createElement('style');
    style.innerHTML = `
        /* PASTE YOUR CSS HERE */
        #trade-widget-launcher { position: fixed; bottom: 20px; right: 20px; ... }
    `;
    document.head.appendChild(style);

    // 3. Inject HTML
    widgetContainer.innerHTML = `
        <button id="trade-widget-launcher">💬</button>
        <div id="trade-chat-window">...ALL YOUR CHAT HTML...</div>
    `;

    // 4. PASTE YOUR JAVASCRIPT LOGIC HERE
    // (The logic for toggling chat, uploading images, fetching API)
    
})();