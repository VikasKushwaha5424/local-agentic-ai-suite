/**
 * PeopleOps AI - Enterprise HR Policy Portal Client Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // Core DOM Elements
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

  // Metrics Modal Elements
  const metricsBtn = document.getElementById('metrics-btn');
  const metricsModal = document.getElementById('metrics-modal');
  const closeModalBtn = document.getElementById('close-modal-btn');

  // ---------------------------------------------------------------------------
  // 1. Theme Management (Light / Dark with localStorage)
  // ---------------------------------------------------------------------------
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('peopleops_hr_theme', theme);
    if (theme === 'dark') {
      themeIconSun.classList.remove('hidden');
      themeIconMoon.classList.add('hidden');
    } else {
      themeIconSun.classList.add('hidden');
      themeIconMoon.classList.remove('hidden');
    }
  }

  const savedTheme = localStorage.getItem('peopleops_hr_theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  applyTheme(savedTheme);

  themeToggleBtn.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    applyTheme(current === 'dark' ? 'light' : 'dark');
  });

  // ---------------------------------------------------------------------------
  // 2. Metrics Modal Control
  // ---------------------------------------------------------------------------
  if (metricsBtn && metricsModal) {
    metricsBtn.addEventListener('click', () => {
      metricsModal.classList.remove('hidden');
      metricsModal.setAttribute('aria-hidden', 'false');
    });

    closeModalBtn.addEventListener('click', () => {
      metricsModal.classList.add('hidden');
      metricsModal.setAttribute('aria-hidden', 'true');
    });

    metricsModal.addEventListener('click', (e) => {
      if (e.target === metricsModal) {
        metricsModal.classList.add('hidden');
        metricsModal.setAttribute('aria-hidden', 'true');
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !metricsModal.classList.contains('hidden')) {
        metricsModal.classList.add('hidden');
        metricsModal.setAttribute('aria-hidden', 'true');
      }
    });
  }

  // ---------------------------------------------------------------------------
  // 3. Engine Operational Status Polling
  // ---------------------------------------------------------------------------
  async function checkSystemStatus() {
    try {
      const res = await fetch('/api/status');
      if (!res.ok) throw new Error('Status non-200');
      const data = await res.json();

      if (data.status === 'online') {
        statusBadge.className = 'status-pill status-online';
        statusText.textContent = `Online • ${data.llm_model}`;
        statusBadge.title = `Engine: ${data.llm_model} | Embedding: ${data.embed_model} | Status: Ready`;
      } else {
        statusBadge.className = 'status-pill status-offline';
        statusText.textContent = 'Ollama Offline';
        statusBadge.title = 'Please ensure `ollama serve` is running.';
      }
    } catch (err) {
      statusBadge.className = 'status-pill status-offline';
      statusText.textContent = 'Offline';
    }
  }

  checkSystemStatus();
  setInterval(checkSystemStatus, 20000);

  // ---------------------------------------------------------------------------
  // 4. Textarea Auto-Resize & Dynamic Send Button
  // ---------------------------------------------------------------------------
  function updateInputState() {
    userInput.style.height = 'auto';
    userInput.style.height = `${Math.min(userInput.scrollHeight, 140)}px`;

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
  // 5. Prompt Suggestions Quick Click
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
  // 6. Form Submission & Agent Query Handling
  // ---------------------------------------------------------------------------
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = userInput.value.trim();
    if (!query) return;
    submitQuery(query);
  });

  async function submitQuery(queryText) {
    if (welcomeBanner) {
      welcomeBanner.classList.add('hidden');
    }

    appendUserMessage(queryText);

    userInput.value = '';
    updateInputState();
    userInput.focus();

    setLoadingState(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: queryText })
      });

      const data = await response.json();
      setLoadingState(false);

      if (data.response) {
        appendAssistantMessage(data.response, data.sources || [], data.escalated || false, data.reason || '');
      } else if (data.error) {
        appendAssistantMessage(`⚠️ An error occurred: ${data.error}`, [], false);
      }
    } catch (err) {
      setLoadingState(false);
      appendAssistantMessage(
        '⚠️ Could not connect to the HR Policy server. Please verify that `web_hr_portal.py` and local Ollama are active.',
        [],
        false
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
  // 7. Message Stream Rendering
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

  function appendAssistantMessage(text, sources = [], isEscalated = false, reason = '') {
    const row = document.createElement('div');
    row.className = 'message-row assistant';

    const wrapper = document.createElement('div');
    wrapper.className = 'assistant-wrapper';

    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'assistant-avatar';
    avatar.innerHTML = `
      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
      </svg>
    `;

    const body = document.createElement('div');
    body.className = 'assistant-body';

    // Check if this is an escalation ticket response
    if (isEscalated || text.includes('[ESCALATE_TO_HR')) {
      const ticketCard = document.createElement('div');
      ticketCard.className = 'escalation-ticket-card';
      ticketCard.innerHTML = `
        <div class="escalation-header">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
          <span>Routed to Human HR Specialist [Escalation Required]</span>
        </div>
        <div class="escalation-details">
          <div class="escalation-item">
            <span class="escalation-label">Reason:</span>
            <span>${escapeHtml(reason || 'Inquiry requires custom review or falls outside standard policy boundaries.')}</span>
          </div>
          <div class="escalation-item">
            <span class="escalation-label">Next Step:</span>
            <span>This matter involves custom contract adjustments, sabbaticals, or sensitive employee relations.</span>
          </div>
          <div class="escalation-item">
            <span class="escalation-label">Contact:</span>
            <span>Email <strong>hr-operations@enterprise.corp</strong> or visit <strong>HR Office (Building B, Room 402)</strong>.</span>
          </div>
        </div>
      `;
      body.appendChild(ticketCard);
    } else {
      const content = document.createElement('div');
      content.className = 'assistant-content';
      content.innerHTML = formatMarkdown(text);
      body.appendChild(content);
    }

    // Collapsible Sources
    if (sources && sources.length > 0) {
      const sourcesContainer = document.createElement('div');
      sourcesContainer.className = 'sources-container';

      const toggleBtn = document.createElement('button');
      toggleBtn.className = 'sources-toggle';
      toggleBtn.innerHTML = `
        <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
        <span>${sources.length} Verified HR Policy ${sources.length === 1 ? 'Excerpt' : 'Excerpts'} Referenced</span>
      `;

      const sourcesList = document.createElement('div');
      sourcesList.className = 'sources-list';

      sources.forEach((s) => {
        const scorePercent = Math.round((s.score || 0.6) * 100);
        const card = document.createElement('div');
        card.className = 'source-pill-card';
        card.innerHTML = `
          <div class="source-card-header">
            <span class="source-name">📄 hr_policy.txt (Section ${s.chunk_id || 1})</span>
            <span class="source-badge">${scorePercent}% relevance</span>
          </div>
          ${s.text_snippet ? `<div class="source-preview">${escapeHtml(s.text_snippet)}</div>` : ''}
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

    // Copy Action Button
    const actions = document.createElement('div');
    actions.className = 'message-actions';

    const copyBtn = document.createElement('button');
    copyBtn.className = 'action-pill-btn';
    copyBtn.innerHTML = `
      <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
      <span>Copy Response</span>
    `;

    copyBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(text).then(() => {
        copyBtn.querySelector('span').textContent = 'Copied!';
        setTimeout(() => {
          copyBtn.querySelector('span').textContent = 'Copy Response';
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
  // 8. Reset / New Inquiry
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
  // 9. Markdown Parser
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

    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

    const lines = text.split('\n');
    let html = '';
    let inUl = false;
    let inOl = false;

    lines.forEach((line) => {
      const trimmed = line.trim();

      if (trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
        if (!inUl) {
          if (inOl) { html += '</ol>'; inOl = false; }
          html += '<ul>';
          inUl = true;
        }
        html += `<li>${trimmed.substring(2)}</li>`;
      }
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
