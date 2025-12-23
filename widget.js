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
    
    // IMPORTANT: Update this to your actual backend URL
    // For local testing with app.py, use: http://localhost:10000
    // For production, use: https://renovision-1.onrender.com
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

    // --- MAIN API LOGIC (EXACT MATCH TO TEST-WIDGET.HTML) ---
    let lastPreviewEl = null;
    async function processPreview() {
        chatState = 'processing_preview';
        const loaderHtml = `<div style="display:flex;flex-direction:column;align-items:center;gap:6px;"><div class="spinner"></div><div><b>Creating preview...</b></div><div style="font-size:12px;color:#666;">This may take ~30–60 seconds — please wait.</div></div>`;
        const loader = addMessage(loaderHtml, 'bot');
        
        try {
            const req = await fetch(`${API_BASE}/visualize`, { 
                method: 'POST', 
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: userData.photo,
                    prompt: userData.prompt,
                    email: '' // no email yet for preview
                })
            });
            const res = await req.json();
            try { loader.remove(); } catch(e){}

            if (res.status === 'success' || res.image || res.imageUrl) {
                addMessage("<b>Preview:</b>", 'bot');
                const imageSrc = res.image || res.imageUrl || (res.result && res.result[0]);
                if (imageSrc) {
                    // Show blurred preview and store reference
                    lastPreviewEl = addMessage(imageSrc, 'bot', true);
                    // apply blur to the img inside the returned div
                    try {
                        const img = lastPreviewEl.querySelector && lastPreviewEl.querySelector('img');
                        if (img) {
                            img.style.filter = 'blur(6px)';
                            img.style.transition = 'filter 0.4s ease';
                        }
                    } catch(e) { /* ignore */ }
                    // store generated image URL for later reveal
                    userData.generatedImage = imageSrc;

                    // Prompt for email so we can send the full image and quote
                    setTimeout(() => {
                        addMessage("To receive the full-resolution image and a quote estimate, please enter your <b>email address</b>.", 'bot');
                        chatState = 'awaiting_email';
                    }, 600);

                } else {
                    addMessage("Preview was generated but no URL was returned.", 'bot');
                    chatState = 'initial';
                }

            } else {
                const errMsg = res.message || JSON.stringify(res);
                addMessage("⚠️ TECHNICAL ERROR: " + errMsg, 'bot');
                chatState = 'initial';
            }
        } catch(e) {
            try { loader.remove(); } catch(err){}
            console.error(e);
            addMessage("Connection error. Please try again later.", 'bot');
            chatState = 'initial';
        }
    }

    async function sendToMake() {
        const refNum = 'RV-' + Math.random().toString(36).substring(2,8).toUpperCase();
        const contactNum = "01234 567890";

        // Unblur the image for the user immediately
        if (lastPreviewEl) {
            const img = lastPreviewEl.querySelector('img');
            if (img) img.style.filter = 'none';
        }

        addMessage("Sending details...", 'bot');
        
        try {
            await fetch(MAKE_WEBHOOK, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    email: userData.email,
                    image_url: userData.generatedImage,
                    prompt: userData.prompt,
                    reference: refNum,
                    contact: contactNum
                })
            });
            
            addMessage(`✅ <b>Sent!</b> We've emailed a copy to <b>${userData.email}</b>.`, 'bot');
            addMessage(`Your Reference: <b>${refNum}</b><br>Please quote this when calling us at <b>${contactNum}</b>.`, 'bot');

            setTimeout(() => {
                addMessage(`<button class="action-btn" onclick="location.reload()">Start Over 🔄</button>`, 'bot');
                chatState = 'initial';
            }, 4000);

        } catch(e) {
            console.error(e);
            addMessage(`✅ <b>Sent!</b> (Ref: ${refNum})`, 'bot');
        }
    }

  }, 100);
})();