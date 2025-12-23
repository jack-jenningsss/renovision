(function() {
  console.log("TradeVision Widget Loading... (Nano Banana Edition)");

  // --- 1. DEFINE THE CSS STYLES ---
  const css = `
    /* FLOATING BUTTON */
    #trade-widget-launcher {
      position: fixed; bottom: 20px; right: 20px;
      background-color: #0066cc; color: white;
      width: 60px; height: 60px; border-radius: 50%;
      border: none; cursor: pointer; z-index: 999999;
      font-size: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      display: flex; align-items: center; justify-content: center;
      transition: transform 0.2s;
    }
    #trade-widget-launcher:hover { transform: scale(1.05); }

    /* CHAT WINDOW */
    #trade-chat-window {
      position: fixed; bottom: 90px; right: 20px;
      width: 350px; height: 500px; background: white;
      border-radius: 12px; box-shadow: 0 5px 20px rgba(0,0,0,0.2);
      display: none; flex-direction: column; z-index: 999999;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      overflow: hidden; border: 1px solid #ccc;
    }
    .chat-header { background: #0066cc; color: white; padding: 15px; display: flex; justify-content: space-between; align-items: center; font-weight: bold; }
    .chat-messages { flex: 1; padding: 15px; overflow-y: auto; background: #f4f4f4; display: flex; flex-direction: column; gap: 10px; }
    .chat-input-area { padding: 10px; border-top: 1px solid #eee; display: flex; gap: 10px; background: white; }
    #chat-input { flex: 1; padding: 8px; border-radius: 20px; border: 1px solid #ccc; outline: none; }
    #send-btn { background: none; border: none; color: #0066cc; font-weight: bold; cursor: pointer; }
    
    /* MESSAGES */
    .message { max-width: 80%; padding: 10px; border-radius: 8px; font-size: 14px; line-height: 1.4; }
    .bot-msg { background: white; border: 1px solid #e0e0e0; align-self: flex-start; color: #333; }
    .user-msg { background: #0066cc; color: white; align-self: flex-end; }
    
    /* EXTRAS */
    .action-btn { background: white; border: 1px solid #0066cc; color: #0066cc; padding: 6px 12px; border-radius: 15px; margin: 2px; cursor: pointer; font-size: 12px; }
    .action-btn:hover { background: #0066cc; color: white; }
    .img-preview { max-width: 100%; border-radius: 5px; margin-top: 5px; border: 1px solid #ccc; }
    .spinner { border: 3px solid #f3f3f3; border-top: 3px solid #0066cc; border-radius: 50%; width: 20px; height: 20px; animation: spin 1s linear infinite; margin: 10px auto; }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
  `;

  // --- 2. INJECT CSS INTO THE PAGE ---
  const style = document.createElement('style');
  style.innerHTML = css;
  document.head.appendChild(style);

  // --- 3. INJECT HTML STRUCTURE ---
  const container = document.createElement('div');
  container.id = 'tradevision-root';
  container.innerHTML = `
    <button id="trade-widget-launcher">💬</button>
    <div id="trade-chat-window">
      <div class="chat-header">
        <span>TradeVision Assistant</span>
        <span style="cursor:pointer;" id="close-chat-btn">✕</span>
      </div>
      <div class="chat-messages" id="chat-messages"></div>
      <div class="chat-input-area">
        <input type="text" id="chat-input" placeholder="Type a message...">
        <button id="send-btn">Send</button>
      </div>
      <input type="file" id="image-upload" accept="image/*" style="display: none;">
    </div>
  `;
  document.body.appendChild(container);

  // --- 4. ATTACH THE LOGIC ---
  setTimeout(() => {
    const launcher = document.getElementById('trade-widget-launcher');
    const windowEl = document.getElementById('trade-chat-window');
    const closeBtn = document.getElementById('close-chat-btn');
    const messagesEl = document.getElementById('chat-messages');
    const inputEl = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const fileInput = document.getElementById('image-upload');
    
    const API_BASE = "https://renovision-1.onrender.com"; 
    const MAKE_WEBHOOK = "https://hook.eu1.make.com/tbw4om63qcv46ey6uph92pgpnhudi6ys"; 

    let chatState = 'initial';
    let userData = { photo: null, prompt: null, email: null, generatedImage: null };

    function toggleChat() {
        const isHidden = windowEl.style.display === 'none' || windowEl.style.display === '';
        windowEl.style.display = isHidden ? 'flex' : 'none';
        if (isHidden && messagesEl.children.length === 0) initChat();
    }
    launcher.onclick = toggleChat;
    closeBtn.onclick = toggleChat;

    function addMessage(text, sender, isImage = false) {
        const div = document.createElement('div');
        div.className = `message ${sender === 'bot' ? 'bot-msg' : 'user-msg'}`;
        if (isImage) {
            const img = document.createElement('img');
            img.src = text;
            img.className = 'img-preview';
            div.appendChild(img);
            messagesEl.appendChild(div);
            messagesEl.scrollTop = messagesEl.scrollHeight;
            return div; 
        } else {
            div.innerHTML = text;
        }
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        return div;
    }

    function initChat() {
        addMessage("Hi! I'm the AI assistant. How can I help you today?", 'bot');
        setTimeout(() => {
            addMessage(`
              <div style="display:flex; gap:5px; flex-wrap:wrap;">
                <button class="action-btn" id="btn-renovate">Visualise Renovation 🏠</button>
                <button class="action-btn" id="btn-support">Ask a Question ❓</button>
              </div>
            `, 'bot');
            setTimeout(() => {
                const rBtn = document.getElementById('btn-renovate');
                const sBtn = document.getElementById('btn-support');
                if(rBtn) rBtn.onclick = startRenovation;
                if(sBtn) sBtn.onclick = handleSupport;
            }, 100);
        }, 500);
    }

    function handleSupport() {
        chatState = 'support';
        addMessage("Sure, ask me anything about our services.", 'bot');
    }

    function startRenovation() {
        chatState = 'awaiting_photo';
        addMessage("Let's visualize! Please upload a clear photo of the area.", 'bot');
        addMessage(`<button class="action-btn" onclick="document.getElementById('image-upload').click()">📁 Click to Upload Photo</button>`, 'bot');
    }

    fileInput.onchange = (e) => {
        if(chatState !== 'awaiting_photo') return;
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (ev) => {
                userData.photo = ev.target.result; // Keep as Base64 string for Nano Banana
                addMessage(userData.photo, 'user', true);
                addMessage("Great photo! What would you like to change?", 'bot');
                chatState = 'awaiting_prompt';
            };
            reader.readAsDataURL(file);
        }
    };

    function handleInput() {
        const text = inputEl.value.trim();
        if(!text) return;
        addMessage(text, 'user');
        inputEl.value = '';

        if(chatState === 'support') {
            setTimeout(() => addMessage("Thanks for asking. Please call us at 01234 567890 for a quote.", 'bot'), 1000);
        }
        else if(chatState === 'awaiting_prompt') {
            userData.prompt = text;
            processPreview();
        } 
        else if (chatState === 'awaiting_email') {
            if(text.includes('@')) {
                userData.email = text;
                sendToMake();
            } else {
                addMessage("Please enter a valid email.", 'bot');
            }
        }
    }
    
    sendBtn.onclick = handleInput;
    inputEl.onkeypress = (e) => { if(e.key === 'Enter') handleInput(); };

    // --- MAIN API LOGIC (UPDATED TO MATCH TEST-WIDGET.HTML) ---
    async function processPreview() {
        chatState = 'processing';
        const loader = addMessage(`<div class="spinner"></div><div>Creating preview...</div>`, 'bot');
        
        try {
            // Using /visualize (Nano Banana) because you said it works perfectly
            const req = await fetch(`${API_BASE}/visualize`, { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: userData.photo, // Sends Base64
                    prompt: userData.prompt
                })
            });
            const res = await req.json();
            try { loader.remove(); } catch(e){}

            // Handle response
            const finalImage = res.image || res.imageUrl;

            if(finalImage) {
                userData.generatedImage = finalImage;
                const imgMsg = addMessage(finalImage, 'bot', true);
                
                // NO BLUR - Showing you the perfect result immediately
                
                addMessage("To receive a copy + Quote Ref, enter your <b>email</b>.", 'bot');
                chatState = 'awaiting_email';
                userData.lastPreviewEl = imgMsg;
            } else {
                addMessage("Error generating image.", 'bot');
                chatState = 'initial';
            }
        } catch(e) {
            try { loader.remove(); } catch(err){}
            console.error(e);
            addMessage("Server connection error.", 'bot');
            chatState = 'initial';
        }
    }

    async function sendToMake() {
        addMessage("Sending details...", 'bot');
        const ref = 'RV-' + Math.random().toString(36).substring(2,8).toUpperCase();
        
        try {
            await fetch(MAKE_WEBHOOK, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    email: userData.email,
                    image_url: userData.generatedImage,
                    prompt: userData.prompt,
                    reference: ref
                })
            });
            addMessage(`✅ Sent! Check inbox: <b>${userData.email}</b>`, 'bot');
            addMessage(`Ref: <b>${ref}</b>`, 'bot');
            setTimeout(() => {
                addMessage(`<button class="action-btn" onclick="location.reload()">Start Over 🔄</button>`, 'bot');
            }, 3000);
        } catch(e) {
            addMessage(`✅ Sent! (Ref: ${ref})`, 'bot');
        }
    }

  }, 100);
})();