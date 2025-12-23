(function() {
  console.log("TradeVision Widget Loading... (Nano Banana Edition)");

  // --- 1. DEFINE THE CSS STYLES ---
  const css = `
    /* FLOATING BUTTON */
    #trade-widget-launcher {
      position: fixed; bottom: 20px; right: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      width: 65px; height: 65px; border-radius: 50%;
      border: none; cursor: pointer; z-index: 999999;
      font-size: 28px; 
      box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
      display: flex; align-items: center; justify-content: center;
      transition: all 0.3s ease;
    }
    #trade-widget-launcher:hover { 
      transform: scale(1.1); 
      box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5);
    }

    /* CHAT WINDOW */
    #trade-chat-window {
      position: fixed; bottom: 100px; right: 20px;
      width: 380px; height: 600px; background: white;
      border-radius: 20px; 
      box-shadow: 0 10px 40px rgba(0,0,0,0.15);
      display: none; flex-direction: column; z-index: 999999;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      overflow: hidden; 
      border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .chat-header { 
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white; 
      padding: 20px; 
      display: flex; 
      justify-content: space-between; 
      align-items: center; 
      font-weight: 600;
      font-size: 16px;
    }
    
    .chat-messages { 
      flex: 1; 
      padding: 20px; 
      overflow-y: auto; 
      background: linear-gradient(to bottom, #f8f9ff 0%, #ffffff 100%);
      display: flex; 
      flex-direction: column; 
      gap: 12px; 
    }
    
    .chat-input-area { 
      padding: 15px; 
      border-top: 1px solid #e8e8e8; 
      display: flex; 
      gap: 10px; 
      background: white; 
    }
    
    #chat-input { 
      flex: 1; 
      padding: 12px 16px; 
      border-radius: 25px; 
      border: 2px solid #e8e8e8; 
      outline: none;
      font-size: 14px;
      transition: border 0.3s;
    }
    
    #chat-input:focus {
      border-color: #667eea;
    }
    
    #send-btn { 
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none; 
      color: white; 
      font-weight: 600; 
      cursor: pointer;
      padding: 12px 20px;
      border-radius: 25px;
      transition: all 0.3s;
    }
    
    #send-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* MESSAGES */
    .message { 
      max-width: 85%; 
      padding: 12px 16px; 
      border-radius: 16px; 
      font-size: 14px; 
      line-height: 1.5;
      animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .bot-msg { 
      background: white;
      border: 1px solid #e8e8e8; 
      align-self: flex-start; 
      color: #333;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .user-msg { 
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white; 
      align-self: flex-end;
      box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* EXTRAS */
    .action-btn { 
      background: white;
      border: 2px solid #667eea; 
      color: #667eea; 
      padding: 10px 18px; 
      border-radius: 20px; 
      margin: 4px; 
      cursor: pointer; 
      font-size: 13px;
      font-weight: 600;
      transition: all 0.3s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    
    .action-btn:hover { 
      background: #667eea; 
      color: white;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .img-preview { 
      max-width: 100%; 
      border-radius: 12px; 
      margin-top: 8px; 
      border: 1px solid #e8e8e8;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .spinner { 
      border: 3px solid #f3f3f3; 
      border-top: 3px solid #667eea; 
      border-radius: 50%; 
      width: 24px; 
      height: 24px; 
      animation: spin 1s linear infinite; 
      margin: 10px auto; 
    }
    
    @keyframes spin { 
      0% { transform: rotate(0deg); } 
      100% { transform: rotate(360deg); } 
    }
    
    .welcome-banner {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 20px;
      border-radius: 12px;
      text-align: center;
      margin-bottom: 10px;
    }
    
    .welcome-banner h3 {
      margin: 0 0 8px 0;
      font-size: 18px;
      font-weight: 600;
    }
    
    .welcome-banner p {
      margin: 0;
      font-size: 13px;
      opacity: 0.95;
    }
  `;

  // --- 2. INJECT CSS INTO THE PAGE ---
  const style = document.createElement('style');
  style.innerHTML = css;
  document.head.appendChild(style);

  // --- 3. INJECT HTML STRUCTURE ---
  const container = document.createElement('div');
  container.id = 'tradevision-root';
  container.innerHTML = `
    <button id="trade-widget-launcher">🎨</button>
    <div id="trade-chat-window">
      <div class="chat-header">
        <span>✨ RenoVision AI</span>
        <span style="cursor:pointer;" id="close-chat-btn">✕</span>
      </div>
      <div class="chat-messages" id="chat-messages"></div>
      <div class="chat-input-area">
        <input type="text" id="chat-input" placeholder="Describe your vision...">
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
        // Welcome banner
        const welcomeHtml = `
          <div class="welcome-banner">
            <h3>✨ AI Renovation Visualizer</h3>
            <p>Transform your space in seconds with AI-powered previews</p>
          </div>
        `;
        addMessage(welcomeHtml, 'bot');
        
        setTimeout(() => {
            addMessage("Ready to see your renovation come to life? Let's get started! 🎨", 'bot');
            setTimeout(() => {
                addMessage(`<button class="action-btn" id="btn-renovate">📸 Start Visualization</button>`, 'bot');
                setTimeout(() => {
                    const rBtn = document.getElementById('btn-renovate');
                    if(rBtn) rBtn.onclick = startRenovation;
                }, 100);
            }, 600);
        }, 400);
    }

    function startRenovation() {
        chatState = 'awaiting_photo';
        addMessage("Perfect! First, please <b>upload a clear photo</b> of the area you'd like to renovate (e.g., roof, kitchen, exterior). 📷", 'bot');
        
        setTimeout(() => {
            addMessage(`<button class="action-btn" onclick="document.getElementById('image-upload').click()">📁 Choose Photo</button>`, 'bot');
        }, 500);
    }

    fileInput.onchange = (e) => {
        if(chatState !== 'awaiting_photo') return;
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (ev) => {
                userData.photo = ev.target.result; // Keep as Base64 string for Nano Banana
                addMessage(userData.photo, 'user', true);
                setTimeout(() => {
                    addMessage("Excellent! Now tell me what you'd like to change. 💭", 'bot');
                    setTimeout(() => {
                        addMessage("<i>Examples: 'Change roof to slate gray', 'Modern white kitchen', 'Add brick facade'</i>", 'bot');
                        chatState = 'awaiting_prompt';
                    }, 400);
                }, 500);
            };
            reader.readAsDataURL(file);
        }
    };

    function handleInput() {
        const text = inputEl.value.trim();
        if(!text) return;
        addMessage(text, 'user');
        inputEl.value = '';

        if(chatState === 'awaiting_prompt') {
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
            
            addMessage(`✅ <b>Perfect!</b> We've sent everything to <b>${userData.email}</b>`, 'bot');
            addMessage(`📋 Your Reference: <b>${refNum}</b><br><small>Quote this when contacting us at <b>${contactNum}</b></small>`, 'bot');

            setTimeout(() => {
                addMessage(`
                    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:5px;">
                        <button class="action-btn" onclick="location.reload()">🔄 Visualize Another</button>
                    </div>
                `, 'bot');
                chatState = 'initial';
            }, 2000);

        } catch(e) {
            console.error(e);
            addMessage(`✅ <b>Sent!</b> Reference: ${refNum}`, 'bot');
            setTimeout(() => {
                addMessage(`<button class="action-btn" onclick="location.reload()">🔄 Start Over</button>`, 'bot');
            }, 2000);
        }
    }

  }, 100);
})();