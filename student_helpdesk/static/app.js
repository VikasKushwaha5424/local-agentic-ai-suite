/**
 * CampusDesk - Minimalist Modern Helpdesk Frontend
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const chatForm = document.getElementById('chat-form');
  const userInput = document.getElementById('user-input');
  const sendBtn = document.getElementById('send-btn');
  const messagesStream = document.getElementById('messages-stream');
  const welcomeBanner = document.getElementById('welcome-banner');
  const typingIndicator = document.getElementById('typing-indicator');
  const clearChatBtn = document.getElementById('clear-chat-btn');
  const statusBadge = document.getElementById('system-status-badge');
  const statusText = document.getElementById('status-text');
  const chatViewport = document.querySelector('.chat-viewport');
  
  // Theme Toggle Elements
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const themeIconSun = document.getElementById('theme-icon-sun');
  const themeIconMoon = document.getElementById('theme-icon-moon');

  // ---------------------------------------------------------------------------
  // 1. Theme Management (Light / Dark with localStorage persistence)
  // ---------------------------------------------------------------------------
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('campusdesk_theme', theme);
    if (theme === 'dark') {
      themeIconSun.classList.remove('hidden');
      themeIconMoon.classList.add('hidden');
    } else {
      themeIconSun.classList.add('hidden');
      themeIconMoon.classList.remove('hidden');
    }
  }

  const savedTheme = localStorage.getItem('campusdesk_theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  applyTheme(savedTheme);

  themeToggleBtn.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    applyTheme(current === 'dark' ? 'light' : 'dark');
  });

  // ---------------------------------------------------------------------------
  // 2. Local Engine Status Check
  // ---------------------------------------------------------------------------
  async function checkSystemStatus() {
    try {
      const res = await fetch('/api/status');
      if (!res.ok) throw new Error('Status endpoint returned non-200');
      const data = await res.json();

      if (data.status === 'online') {
        statusBadge.className = 'status-pill status-online';
        statusText.textContent = `Online • ${data.llm_model}`;
        statusBadge.title = `Engine: ${data.llm_model} | Embedding: ${data.embed_model} | Status: Ready`;
      } else {
        statusBadge.className = 'status-pill status-offline';
        statusText.textContent = 'Ollama Offline';
        statusBadge.title = 'Ollama service is not responding. Please run `ollama serve`.';
      }
    } catch (err) {
      statusBadge.className = 'status-pill status-offline';
      statusText.textContent = 'Offline';
      statusBadge.title = 'Helpdesk server not reachable.';
    }
  }

  checkSystemStatus();
  setInterval(checkSystemStatus, 20000);

  // ---------------------------------------------------------------------------
  // 3. Textarea Auto-Resize & Send Button Activation
  // ---------------------------------------------------------------------------
  function updateInputState() {
    // Auto-grow height
    userInput.style.height = 'auto';
    userInput.style.height = `${Math.min(userInput.scrollHeight, 140)}px`;

    // Toggle button active state
    if (userInput.value.trim().length > 0) {
      sendBtn.classList.add('active');
    } else {
      sendBtn.classList.remove('active');
    }
  }

  userInput.addEventListener('input', updateInputState);

  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (userInput.value.trim().length > 0) {
        chatForm.requestSubmit();
      }
    }
  });

  // ---------------------------------------------------------------------------
  // 4. Quick Suggestion Prompt Click
  // ---------------------------------------------------------------------------
  document.querySelectorAll('.prompt-chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      const query = chip.getAttribute('data-query');
      if (query) {
        submitQuery(query);
      }
    });
  });

  // ---------------------------------------------------------------------------
  // 5. Query Submission & Pipeline
  // ---------------------------------------------------------------------------
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = userInput.value.trim();
    if (!query) return;
    submitQuery(query);
  });

  async function submitQuery(queryText) {
    // Hide welcome banner once conversation starts
    if (welcomeBanner) {
      welcomeBanner.classList.add('hidden');
    }

    // Render User Query
    appendUserMessage(queryText);

    // Reset Input Box
    userInput.value = '';
    updateInputState();
    userInput.focus();

    // Show Minimal Typing State
    setLoadingState(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: queryText })
      });

      const data = await response.json();
      setLoadingState(false);

      if (data.answer) {
        appendAssistantMessage(data.answer, data.sources || []);
      } else if (data.error) {
        appendAssistantMessage(`⚠️ An error occurred: ${data.error}`, []);
      }
    } catch (err) {
      setLoadingState(false);
      appendAssistantMessage(
        '⚠️ Could not connect to the campus helpdesk engine. Please verify that `web_helpdesk.py` and local Ollama are running.',
        []
      );
    }
  }

  function setLoadingState(isLoading) {
    if (isLoading) {
      typingIndicator.classList.remove('hidden');
      sendBtn.classList.remove('active');
      scrollToBottom();
    } else {
      typingIndicator.classList.add('hidden');
    }
  }

  function scrollToBottom() {
    requestAnimationFrame(() => {
      if (chatViewport) {
        chatViewport.scrollTop = chatViewport.scrollHeight;
      }
    });
  }

  // ---------------------------------------------------------------------------
  // 6. Message Rendering
  // ---------------------------------------------------------------------------
  function appendUserMessage(text) {
    const row = document.createElement('div');
    row.className = 'message-row user';

    const bubble = document.createElement('div');
    bubble.className = 'user-bubble';
    bubble.textContent = text;

    row.appendChild(bubble);
    messagesStream.appendChild(row);
    scrollToBottom();
  }

  function appendAssistantMessage(text, sources = []) {
    const row = document.createElement('div');
    row.className = 'message-row assistant';

    const wrapper = document.createElement('div');
    wrapper.className = 'assistant-wrapper';

    // Minimal assistant avatar
    const avatar = document.createElement('div');
    avatar.className = 'assistant-avatar';
    avatar.innerHTML = `
      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
        <path d="M2 17l10 5 10-5"></path>
        <path d="M2 12l10 5 10-5"></path>
      </svg>
    `;

    // Assistant content body
    const body = document.createElement('div');
    body.className = 'assistant-body';

    const content = document.createElement('div');
    content.className = 'assistant-content';
    content.innerHTML = formatMarkdown(text);
    body.appendChild(content);

    // Collapsible Sources (Minimal Tray)
    if (sources && sources.length > 0) {
      const sourcesContainer = document.createElement('div');
      sourcesContainer.className = 'sources-container';

      const toggleBtn = document.createElement('button');
      toggleBtn.className = 'sources-toggle';
      toggleBtn.innerHTML = `
        <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
        <span>${sources.length} Verified ${sources.length === 1 ? 'Source' : 'Sources'} Referenced</span>
      `;

      const sourcesList = document.createElement('div');
      sourcesList.className = 'sources-list';

      sources.forEach((s) => {
        const scorePercent = Math.round((s.score || 0.85) * 100);
        const card = document.createElement('div');
        card.className = 'source-pill-card';
        card.innerHTML = `
          <div class="source-card-header">
            <span class="source-name">
              📄 ${escapeHtml(s.source)}
            </span>
            <span class="source-badge">${scorePercent}% match</span>
          </div>
          ${s.preview ? `<div class="source-preview">${escapeHtml(s.preview)}</div>` : ''}
        `;
        sourcesList.appendChild(card);
      });

      toggleBtn.addEventListener('click', () => {
        sourcesContainer.classList.toggle('open');
      });

      sourcesContainer.appendChild(toggleBtn);
      sourcesContainer.appendChild(sourcesList);
      body.appendChild(sourcesContainer);
    }

    // Message Actions Bar (Copy button)
    const actions = document.createElement('div');
    actions.className = 'message-actions';

    const copyBtn = document.createElement('button');
    copyBtn.className = 'action-pill-btn';
    copyBtn.innerHTML = `
      <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
      <span>Copy</span>
    `;

    copyBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(text).then(() => {
        copyBtn.querySelector('span').textContent = 'Copied!';
        setTimeout(() => {
          copyBtn.querySelector('span').textContent = 'Copy';
        }, 1800);
      });
    });

    actions.appendChild(copyBtn);
    body.appendChild(actions);

    wrapper.appendChild(avatar);
    wrapper.appendChild(body);
    row.appendChild(wrapper);

    messagesStream.appendChild(row);
    scrollToBottom();
  }

  // ---------------------------------------------------------------------------
  // 7. Reset / New Chat Action
  // ---------------------------------------------------------------------------
  clearChatBtn.addEventListener('click', () => {
    messagesStream.innerHTML = '';
    if (welcomeBanner) {
      welcomeBanner.classList.remove('hidden');
    }
    userInput.value = '';
    updateInputState();
    userInput.focus();
  });

  // ---------------------------------------------------------------------------
  // 8. Clean Markdown Parser
  // ---------------------------------------------------------------------------
  function escapeHtml(string) {
    if (!string) return '';
    return String(string)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function formatMarkdown(rawText) {
    if (!rawText) return '';
    let text = escapeHtml(rawText);

    // Bold (**text**)
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Italic (*text*)
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Inline code (`code`)
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Parse lists and paragraphs line-by-line
    const lines = text.split('\n');
    let html = '';
    let inUl = false;
    let inOl = false;

    lines.forEach((line) => {
      const trimmed = line.trim();

      // Unordered list item (- or *)
      if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
        if (!inUl) {
          if (inOl) { html += '</ol>'; inOl = false; }
          html += '<ul>';
          inUl = true;
        }
        html += `<li>${trimmed.substring(2)}</li>`;
      }
      // Ordered list item (1. or 2.)
      else if (/^\d+\.\s/.test(trimmed)) {
        if (!inOl) {
          if (inUl) { html += '</ul>'; inUl = false; }
          html += '<ol>';
          inOl = true;
        }
        const itemText = trimmed.replace(/^\d+\.\s/, '');
        html += `<li>${itemText}</li>`;
      }
      else {
        if (inUl) { html += '</ul>'; inUl = false; }
        if (inOl) { html += '</ol>'; inOl = false; }
        if (trimmed.length > 0) {
          html += `<p>${trimmed}</p>`;
        }
      }
    });

    if (inUl) html += '</ul>';
    if (inOl) html += '</ol>';

    return html;
  }
});
