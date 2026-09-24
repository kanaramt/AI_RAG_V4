// Google 'G' 4-color SVG Icon Helper
function getGoogleGSVG(size = 14) {
    return `<svg class="google-g-svg" width="${size}" height="${size}" viewBox="0 0 24 24" style="vertical-align: middle; flex-shrink: 0;"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/></svg>`;
}

// Universal Clipboard Copy Helper with execCommand Fallback
function copyToClipboard(textToCopy) {
    if (!textToCopy) return Promise.reject("Empty text");
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(textToCopy).catch(() => {
            return fallbackCopyToClipboard(textToCopy);
        });
    } else {
        return fallbackCopyToClipboard(textToCopy);
    }
}

function fallbackCopyToClipboard(text) {
    return new Promise((resolve, reject) => {
        try {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            textArea.style.left = "-999999px";
            textArea.style.top = "-999999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            if (successful) {
                resolve();
            } else {
                reject("execCommand copy failed");
            }
        } catch (err) {
            reject(err);
        }
    });
}

// App State
let state = {
    chats: [],
    activeChatId: null,
    selectedModel: 'llama3', // Global selection state for new chats
    searchMode: 'local', // 'local' (default) or 'web'
    stagedFiles: [],
    indexedDocuments: [],
    ragSettings: {
        topK: 3,
        similarity: 0.70,
        temperature: 0.2
    }
};

let activeAbortController = null;

const LEGACY_MODEL_MAP = {
    'llama-3.1-8b-instant': 'openai/gpt-oss-20b',
    'llama-3.3-70b-versatile': 'openai/gpt-oss-120b',
    'claude-3-5-sonnet': 'claude-sonnet-4-6',
    'claude-3-5-haiku': 'claude-haiku-4-5-20251001',
    'claude-3-opus': 'claude-opus-4-7',
    'grok-beta': 'grok-4.5',
    'grok-2': 'grok-4.6',
    'gemini-1.5-flash': 'gemini-3.5-flash',
    'gemini-1.5-pro': 'gemini-3.7-flash',
    'gemini-2.0-flash': 'gemini-3.6-flash',
    'gemini-2.5-flash': 'gemini-3.5-flash'
};

const modelLabels = {
    // OpenAI
    'gpt-5.5': 'gpt-5.5 (OpenAI)',
    'gpt-5.4': 'gpt-5.4 (OpenAI)',
    'gpt-5.4-mini': 'gpt-5.4-mini (OpenAI)',
    'gpt-5.4-nano': 'gpt-5.4-nano (OpenAI)',
    'gpt-4o': 'gpt-4o (OpenAI)',
    'gpt-4o-mini': 'gpt-4o-mini (OpenAI)',
    'gpt-4.1': 'gpt-4.1 (OpenAI)',
    'gpt-4.1-mini': 'gpt-4.1-mini (OpenAI)',

    // Anthropic Claude
    'claude-opus-5': 'claude-opus-5 (Claude)',
    'claude-opus-4-8': 'claude-opus-4-8 (Claude)',
    'claude-opus-4-7': 'claude-opus-4-7 (Claude)',
    'claude-opus-4-6': 'claude-opus-4-6 (Claude)',
    'claude-sonnet-5': 'claude-sonnet-5 (Claude)',
    'claude-sonnet-4-6': 'claude-sonnet-4-6 (Claude)',
    'claude-sonnet-4-5-20250929': 'claude-sonnet-4-5 (Claude)',
    'claude-haiku-4-5-20251001': 'claude-haiku-4-5 (Claude)',

    // Google Gemini
    'gemini-3.8-flash': 'gemini-3.8-flash (Gemini)',
    'gemini-3.7-flash': 'gemini-3.7-flash (Gemini)',
    'gemini-3.6-flash': 'gemini-3.6-flash (Gemini)',
    'gemini-3.5-flash': 'gemini-3.5-flash (Gemini)',
    'gemini-3.5-flash-lite': 'gemini-3.5-flash-lite (Gemini)',
    'gemini-3.1-flash-lite': 'gemini-3.1-flash-lite (Gemini)',

    // xAI Grok
    'grok-4.7': 'grok-4.7 (xAI)',
    'grok-4.6': 'grok-4.6 (xAI)',
    'grok-4.5': 'grok-4.5 (xAI)',

    // Groq Cloud
    'openai/gpt-oss-120b': 'openai/gpt-oss-120b (Groq)',
    'openai/gpt-oss-20b': 'openai/gpt-oss-20b (Groq)',

    // Ollama Local
    'llama3': 'llama3:8b (Ollama)',
    'llama3:8b': 'llama3:8b (Ollama)',
    'llama3:latest': 'llama3:latest (Ollama)',
    'llama3.1': 'llama3.1 (Ollama)',
    'llama3.2': 'llama3.2 (Ollama)',
    'mistral': 'mistral:7b (Ollama)',
    'phi3': 'phi3:3.8b (Ollama)',
    'phi3.5': 'phi3.5 (Ollama)',
    'deepseek-r1': 'deepseek-r1 (Ollama)',
    'gemma2': 'gemma2 (Ollama)',
    'qwen2.5': 'qwen2.5 (Ollama)'
};

// DOM Elements
const appContainer = document.querySelector('.app-container');
const sidebarList = document.getElementById('recent-chats-list');
const newChatBtn = document.getElementById('new-chat-btn');
const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
const dbDocCount = document.getElementById('db-document-count');
const toggleConfigBtn = document.getElementById('toggle-config-btn');
const configDrawer = document.getElementById('config-drawer');
const closeConfigBtn = document.getElementById('close-config-btn');
const chatViewport = document.getElementById('chat-viewport');
const welcomeView = document.getElementById('welcome-view');
const messagesContainer = document.getElementById('messages-container');
const stagedPreview = document.getElementById('staged-attachments-preview');
const promptTextarea = document.getElementById('prompt-textarea');
const sendBtn = document.getElementById('send-btn');
const attachBtn = document.getElementById('attach-btn');
const hiddenFileInput = document.getElementById('hidden-file-input');
const dragDropOverlay = document.getElementById('drag-drop-overlay');
const toastNotification = document.getElementById('toast-notification');
const toastMessage = document.getElementById('toast-message');
const scrollDownBtn = document.getElementById('scroll-down-btn');

// Model Selector Elements
const modelPillBtn = document.getElementById('model-pill-btn');
const modelPillName = document.getElementById('model-pill-name');
const modelDropdownMenu = document.getElementById('model-dropdown-menu');

// RAG config panel elements
const paramTopK = document.getElementById('param-top-k');
const valTopK = document.getElementById('val-top-k');
const paramSimilarity = document.getElementById('param-similarity');
const valSimilarity = document.getElementById('val-similarity');
const paramTemperature = document.getElementById('param-temperature');
const valTemperature = document.getElementById('val-temperature');
const dbUploadZone = document.getElementById('db-upload-zone');
const dbFileInput = document.getElementById('db-file-input');
const indexedDocsList = document.getElementById('indexed-docs-list');
const indexedCountLabel = document.getElementById('indexed-count');

// Initialize Lucide Icons
function initIcons() {
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// Toast Logger
function showToast(message) {
    toastMessage.textContent = message;
    toastNotification.classList.add('show');
    toastNotification.classList.remove('hidden');
    setTimeout(() => {
        toastNotification.classList.remove('show');
        setTimeout(() => toastNotification.classList.add('hidden'), 300);
    }, 3000);
}

// Provider configurations with permitted models and official API key direct links
const PROVIDER_CONFIGS = {
    'openai': {
        name: 'OpenAI',
        models: [
            { id: 'gpt-5.5', label: 'gpt-5.5 (Flagship Frontier)' },
            { id: 'gpt-5.4', label: 'gpt-5.4 (Advanced Multimodal)' },
            { id: 'gpt-5.4-mini', label: 'gpt-5.4-mini (Efficient Fast)' },
            { id: 'gpt-5.4-nano', label: 'gpt-5.4-nano (Ultra Lightweight)' },
            { id: 'gpt-4o', label: 'gpt-4o (Omni Reasoning)' },
            { id: 'gpt-4o-mini', label: 'gpt-4o-mini (Fast & Efficient)' },
            { id: 'gpt-4.1', label: 'gpt-4.1 (High Capacity)' },
            { id: 'gpt-4.1-mini', label: 'gpt-4.1-mini (Compact High Speed)' }
        ],
        placeholder: 'sk-proj-...',
        link: 'https://platform.openai.com/api-keys',
        linkLabel: 'Get OpenAI Key',
        apiKeyField: 'openai_api_key',
        maskedField: 'openai_masked'
    },
    'gemini': {
        name: 'Google Gemini',
        models: [
            { id: 'gemini-3.8-flash', label: 'gemini-3.8-flash (Frontier Speed)' },
            { id: 'gemini-3.7-flash', label: 'gemini-3.7-flash (Hybrid Reasoning)' },
            { id: 'gemini-3.6-flash', label: 'gemini-3.6-flash (Fast & Accurate)' },
            { id: 'gemini-3.5-flash', label: 'gemini-3.5-flash (Balanced Multimodal)' },
            { id: 'gemini-3.5-flash-lite', label: 'gemini-3.5-flash-lite (Cost Efficient)' },
            { id: 'gemini-3.1-flash-lite', label: 'gemini-3.1-flash-lite (Ultra Lightweight)' }
        ],
        placeholder: 'AIzaSy...',
        link: 'https://aistudio.google.com/app/apikey',
        linkLabel: 'Get Gemini Key',
        apiKeyField: 'gemini_api_key',
        maskedField: 'gemini_masked'
    },
    'claude': {
        name: 'Anthropic Claude',
        models: [
            { id: 'claude-opus-5', label: 'claude-opus-5 (Ultimate Frontier)' },
            { id: 'claude-opus-4-8', label: 'claude-opus-4-8 (Deep Reasoning)' },
            { id: 'claude-opus-4-7', label: 'claude-opus-4-7 (Complex Analysis)' },
            { id: 'claude-opus-4-6', label: 'claude-opus-4-6 (High Intelligence)' },
            { id: 'claude-sonnet-5', label: 'claude-sonnet-5 (Frontier Coding & Math)' },
            { id: 'claude-sonnet-4-6', label: 'claude-sonnet-4-6 (Fast Agentic)' },
            { id: 'claude-sonnet-4-5-20250929', label: 'claude-sonnet-4-5 (Hybrid Speed)' },
            { id: 'claude-haiku-4-5-20251001', label: 'claude-haiku-4-5 (Instant Response)' }
        ],
        placeholder: 'sk-ant-api...',
        link: 'https://console.anthropic.com/settings/keys',
        linkLabel: 'Get Anthropic Key',
        apiKeyField: 'anthropic_api_key',
        maskedField: 'anthropic_masked'
    },
    'grok': {
        name: 'xAI Grok',
        models: [
            { id: 'grok-4.7', label: 'grok-4.7 (Frontier Reasoning)' },
            { id: 'grok-4.6', label: 'grok-4.6 (High Performance)' },
            { id: 'grok-4.5', label: 'grok-4.5 (Real-time Knowledge)' }
        ],
        placeholder: 'xai-...',
        link: 'https://console.x.ai/',
        linkLabel: 'Get xAI Grok Key',
        apiKeyField: 'grok_api_key',
        maskedField: 'grok_masked'
    },
    'groq': {
        name: 'Groq Cloud',
        models: [
            { id: 'openai/gpt-oss-120b', label: 'openai/gpt-oss-120b (Ultra Fast Inference)' },
            { id: 'openai/gpt-oss-20b', label: 'openai/gpt-oss-20b (Instant Low Latency)' }
        ],
        placeholder: 'gsk_...',
        link: 'https://console.groq.com/keys',
        linkLabel: 'Get Groq Key',
        apiKeyField: 'groq_api_key',
        maskedField: 'groq_masked'
    },
    'ollama': {
        name: 'Ollama (Local System)',
        models: [
            { id: 'llama3', label: 'llama3:8b (Local System)' },
            { id: 'llama3.1', label: 'llama3.1:8b (Local System)' },
            { id: 'llama3.2', label: 'llama3.2:3b (Local System)' },
            { id: 'mistral', label: 'mistral:7b (Local System)' },
            { id: 'phi3', label: 'phi3:3.8b (Local System)' },
            { id: 'phi3.5', label: 'phi3.5 (Local System)' },
            { id: 'deepseek-r1', label: 'deepseek-r1 (Local Reasoning)' },
            { id: 'gemma2', label: 'gemma2 (Local Google)' },
            { id: 'qwen2.5', label: 'qwen2.5 (Local Alibaba)' }
        ],
        placeholder: 'No API key required for local Ollama',
        link: 'http://localhost:11434',
        linkLabel: 'Check Ollama Server',
        apiKeyField: null,
        maskedField: null
    }
};

let cachedApiKeys = {
    openai_api_key: '',
    anthropic_api_key: '',
    gemini_api_key: '',
    grok_api_key: '',
    groq_api_key: '',
    openai_masked: '',
    anthropic_masked: '',
    gemini_masked: '',
    grok_masked: '',
    groq_masked: '',
    default_cloud_model: 'gpt-4o'
};

function getProviderFromModel(modelId) {
    if (!modelId) return 'openai';
    const m = modelId.toLowerCase();
    for (const [pKey, pConf] of Object.entries(PROVIDER_CONFIGS)) {
        if (pConf.models && pConf.models.some(item => item.id.toLowerCase() === m)) {
            return pKey;
        }
    }
    if (m.includes('gemini')) return 'gemini';
    if (m.includes('claude') || m.includes('anthropic')) return 'claude';
    if (m.includes('grok') || m.includes('xai')) return 'grok';
    if (m.includes('llama-3.3') || m.includes('llama-3.1') || m.includes('mixtral') || m.includes('gemma')) return 'groq';
    if (m.includes('gpt') || m.includes('o1') || m.includes('o3') || m.includes('openai')) return 'openai';
    if (m.includes('llama') || m.includes('mistral') || m.includes('phi') || m.includes('ollama')) return 'ollama';
    return 'openai';
}

// Render API tab state based on selected provider
function updateAPITabUI() {
    const providerSelect = document.getElementById('api-provider-select');
    const submodelSelect = document.getElementById('api-submodel-select');
    const apiKeyInput = document.getElementById('api-key-input');
    const getLink = document.getElementById('api-get-key-link');
    const linkLabel = document.getElementById('api-link-label');
    const statusBadge = document.getElementById('api-key-status-badge');

    if (!providerSelect || !submodelSelect || !apiKeyInput) return;

    const providerKey = providerSelect.value;
    const config = PROVIDER_CONFIGS[providerKey];
    if (!config) return;

    // 1. Populate Submodels Dropdown
    submodelSelect.innerHTML = config.models.map(m => 
        `<option value="${m.id}">${m.label}</option>`
    ).join('');

    // Pre-select active model if present in this provider
    const targetModel = state.selectedModel || cachedApiKeys.default_cloud_model;
    if (targetModel) {
        const found = config.models.find(m => m.id === targetModel);
        if (found) {
            submodelSelect.value = found.id;
        }
    }

    // 2. Update Direct Web Link & Label
    if (getLink && linkLabel) {
        getLink.href = config.link;
        linkLabel.textContent = config.linkLabel;
    }

    // 3. Update API Key Input & Status Badge
    if (config.apiKeyField) {
        apiKeyInput.disabled = false;
        apiKeyInput.placeholder = config.placeholder;
        const currentVal = cachedApiKeys[config.apiKeyField] || '';
        apiKeyInput.value = currentVal;

        const masked = cachedApiKeys[config.maskedField];
        if (statusBadge) {
            if (currentVal || masked) {
                statusBadge.textContent = `Status: Configured (${masked || 'Active'}) ✅`;
                statusBadge.style.color = 'var(--accent-emerald,#10b981)';
            } else {
                statusBadge.textContent = 'Status: Not configured ⚠️';
                statusBadge.style.color = 'var(--text-muted)';
            }
        }
    } else {
        // Ollama Local System
        apiKeyInput.value = '';
        apiKeyInput.disabled = true;
        apiKeyInput.placeholder = config.placeholder;
        if (statusBadge) {
            statusBadge.textContent = 'Status: Runs locally on http://localhost:11434 (No API key needed) 💻';
            statusBadge.style.color = 'var(--accent-purple,#8b5cf6)';
        }
    }
}

// Load API keys & Default Cloud Model from backend
// Load Centralized System Settings (Single Source of Truth) from Backend
async function loadCentralizedSettings() {
    try {
        const resp = await fetch('/api/settings');
        if (resp.ok) {
            const data = await resp.json();
            
            if (data.active_model) {
                state.selectedModel = data.active_model;
            }
            if (data.active_provider) {
                state.selectedProvider = data.active_provider;
            }
            if (data.retriever_params) {
                state.ragSettings = data.retriever_params;
            }
            if (data.system_prompt) {
                state.systemPrompt = data.system_prompt;
            }

            if (data.api_keys) {
                cachedApiKeys = {
                    ...cachedApiKeys,
                    ...data.api_keys,
                    ...data.masked_keys,
                    default_cloud_model: data.active_model
                };
            }

            // Synchronize UI Controls without overwriting or showing toasts
            selectModel(state.selectedModel, false, false);
            updateAPITabUI();

            // Populate Retriever Sliders
            if (typeof paramTopK !== 'undefined' && paramTopK) {
                paramTopK.value = state.ragSettings.topK;
                valTopK.textContent = state.ragSettings.topK;
            }
            if (typeof paramSimilarity !== 'undefined' && paramSimilarity) {
                paramSimilarity.value = state.ragSettings.similarity;
                valSimilarity.textContent = parseFloat(state.ragSettings.similarity).toFixed(2);
            }
            if (typeof paramTemperature !== 'undefined' && paramTemperature) {
                paramTemperature.value = state.ragSettings.temperature;
                valTemperature.textContent = parseFloat(state.ragSettings.temperature).toFixed(1);
            }

            // Populate System Prompt
            const systemPromptTextarea = document.getElementById('val-system-prompt');
            if (systemPromptTextarea && state.systemPrompt) {
                systemPromptTextarea.value = state.systemPrompt;
                localStorage.setItem('rag_system_prompt', state.systemPrompt);
            }
        }
    } catch (err) {
        console.error("Failed to load centralized settings:", err);
    }
}

async function loadAPIKeys() {
    await loadCentralizedSettings();
}

// Save API keys & Default Cloud Model to backend
async function saveAPIKeys() {
    const providerSelect = document.getElementById('api-provider-select');
    const submodelSelect = document.getElementById('api-submodel-select');
    const apiKeyInput = document.getElementById('api-key-input');

    if (!providerSelect || !submodelSelect || !apiKeyInput) return;

    const providerKey = providerSelect.value;
    const selectedModel = submodelSelect.value;
    const inputKey = apiKeyInput.value.trim();

    const config = PROVIDER_CONFIGS[providerKey];
    if (config && config.apiKeyField && inputKey.length > 0) {
        cachedApiKeys[config.apiKeyField] = inputKey;
    }

    try {
        const resp = await fetch('/api/settings', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                active_provider: providerKey,
                active_model: selectedModel,
                openai_api_key: cachedApiKeys.openai_api_key,
                anthropic_api_key: cachedApiKeys.anthropic_api_key,
                gemini_api_key: cachedApiKeys.gemini_api_key,
                grok_api_key: cachedApiKeys.grok_api_key,
                groq_api_key: cachedApiKeys.groq_api_key,
            })
        });

        if (resp.ok) {
            showToast(`✅ API connection saved for ${config ? config.name : providerKey} (${selectedModel})!`);
            selectModel(selectedModel, false, true);
            await loadCentralizedSettings();
            const settingsModal = document.getElementById('settings-modal');
            if (settingsModal) settingsModal.classList.add('hidden');
        } else {
            showToast("⚠️ Failed to save API connection.");
        }
    } catch (err) {
        console.error("Error saving API keys:", err);
        showToast("Error connecting to settings server.");
    }
}

// ------------------------------------------------------------------
// Embedding Models Management (OpenSource vs Paid & Custom Add)
// ------------------------------------------------------------------

let availableEmbeddingModels = [];

// Load and populate Embedding Models in System Settings
async function loadEmbeddingModels() {
    try {
        const resp = await fetch('/api/settings/embeddings');
        if (resp.ok) {
            const data = await resp.json();
            availableEmbeddingModels = data.models || [];
            
            const selectEl = document.getElementById('embedding-model-select');
            if (selectEl) {
                selectEl.innerHTML = availableEmbeddingModels.map(m => {
                    const badge = m.type === 'paid' ? '💰 Paid API' : '⚡ OpenSource';
                    return `<option value="${m.id}" ${m.id === data.active_model ? 'selected' : ''}>${m.name} (${badge} - ${m.provider})</option>`;
                }).join('');
                
                updateEmbeddingModelDetailsCard(data.active_model);
            }
        }
    } catch (err) {
        console.error("Failed to load embedding models:", err);
    }
}

// Update Active Embedding Model Info Card
function updateEmbeddingModelDetailsCard(modelId) {
    const titleEl = document.getElementById('embed-detail-title');
    const badgeEl = document.getElementById('embed-detail-badge');
    const descEl = document.getElementById('embed-detail-desc');
    const providerEl = document.getElementById('embed-detail-provider');

    const model = availableEmbeddingModels.find(m => m.id === modelId) || {
        id: modelId,
        name: modelId,
        type: 'opensource',
        provider: 'Local System',
        desc: 'Vector embedding model'
    };

    if (titleEl) titleEl.textContent = model.name;
    if (descEl) descEl.textContent = model.desc || 'High accuracy vector embedding model.';
    if (providerEl) providerEl.textContent = `Provider: ${model.provider}`;

    if (badgeEl) {
        if (model.type === 'paid') {
            badgeEl.textContent = 'Paid (Cloud API)';
            badgeEl.style.background = 'rgba(139, 92, 246, 0.15)';
            badgeEl.style.color = 'var(--accent-purple,#8b5cf6)';
            badgeEl.style.borderColor = 'rgba(139, 92, 246, 0.3)';
        } else {
            badgeEl.textContent = 'OpenSource (Local)';
            badgeEl.style.background = 'rgba(16, 185, 129, 0.15)';
            badgeEl.style.color = '#10b981';
            badgeEl.style.borderColor = 'rgba(16, 185, 129, 0.3)';
        }
    }
}

// Activate Selected Embedding Model
async function activateEmbeddingModel() {
    const selectEl = document.getElementById('embedding-model-select');
    if (!selectEl) return;

    const selectedId = selectEl.value;
    try {
        const resp = await fetch('/api/settings/embeddings/select', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_id: selectedId })
        });
        if (resp.ok) {
            showToast(`✅ Active embedding model updated to '${selectedId}'!`);
            await loadEmbeddingModels();
        } else {
            showToast("⚠️ Failed to update embedding model.");
        }
    } catch (err) {
        console.error("Error activating embedding model:", err);
    }
}

// Register New Custom Embedding Model
async function registerCustomEmbeddingModel() {
    const nameInput = document.getElementById('custom-embed-name');
    const providerSelect = document.getElementById('custom-embed-provider');
    const apiKeyInput = document.getElementById('custom-embed-api-key');
    const typeRadio = document.querySelector('input[name="custom-embed-type"]:checked');

    const name = nameInput?.value.trim();
    const provider = providerSelect?.value || 'Custom';
    const type = typeRadio?.value || 'opensource';
    const apiKey = apiKeyInput?.value.trim() || '';

    if (!name) {
        showToast("⚠️ Please enter a Model ID / Name.");
        return;
    }

    try {
        const resp = await fetch('/api/settings/embeddings/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                type: type,
                provider: provider,
                api_key: apiKey
            })
        });

        if (resp.ok) {
            showToast(`✅ Custom Embedding Model '${name}' registered and set active!`);
            nameInput.value = '';
            if (apiKeyInput) apiKeyInput.value = '';
            document.getElementById('add-embedding-form-container')?.classList.add('hidden');
            await loadEmbeddingModels();
        } else {
            showToast("⚠️ Failed to register embedding model.");
        }
    } catch (err) {
        console.error("Error registering custom embedding model:", err);
    }
}

// Backend API Integration Functions
async function fetchChats() {
    try {
        const response = await fetch('/api/chats');
        state.chats = await response.json();
        renderRecentChatsList();
    } catch (e) {
        console.error("Failed to load chats from API:", e);
        showToast("Error connecting to server. Using offline defaults.");
    }
}

async function fetchIndexedDocs() {
    try {
        const response = await fetch('/api/documents');
        state.indexedDocuments = await response.json();
        renderIndexedDocsList();
        updateDBBadges();
    } catch (e) {
        console.error("Failed to load document metadata:", e);
    }
}

// Theme Manager (Dark, Light, System)
function initThemeManager() {
    const themeBtn = document.getElementById('theme-btn');
    const themeDropdown = document.getElementById('theme-dropdown-menu');
    const themeIcon = document.getElementById('theme-icon');

    // Get stored theme or default to 'dark'
    let currentTheme = localStorage.getItem('antigravity_theme') || 'dark';

    function applyTheme(theme) {
        currentTheme = theme;
        localStorage.setItem('antigravity_theme', theme);

        let effectiveTheme = theme;
        if (theme === 'system') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            effectiveTheme = prefersDark ? 'dark' : 'light';
        }

        document.documentElement.setAttribute('data-theme', effectiveTheme);

        // Update Theme Icon
        if (themeIcon) {
            if (theme === 'light') {
                themeIcon.setAttribute('data-lucide', 'sun');
                themeIcon.style.color = '#f59e0b';
            } else if (theme === 'system') {
                themeIcon.setAttribute('data-lucide', 'laptop');
                themeIcon.style.color = '#3b82f6';
            } else {
                themeIcon.setAttribute('data-lucide', 'moon');
                themeIcon.style.color = '#a78bfa';
            }
            initIcons();
        }

        // Update active checkmarks in Theme Dropdown Menu
        document.querySelectorAll('#theme-dropdown-menu .dropdown-item').forEach(item => {
            const val = item.getAttribute('data-theme-val');
            item.classList.toggle('active', val === theme);
        });
    }

    // System theme change listener
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (currentTheme === 'system') {
            applyTheme('system');
        }
    });

    // Initial theme application
    applyTheme(currentTheme);

    // Toggle Dropdown Menu
    if (themeBtn && themeDropdown) {
        themeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isHidden = themeDropdown.classList.contains('hidden');
            themeDropdown.classList.toggle('hidden', !isHidden);
        });

        document.querySelectorAll('#theme-dropdown-menu .dropdown-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const selected = item.getAttribute('data-theme-val');
                applyTheme(selected);
                themeDropdown.classList.add('hidden');
                showToast(`Theme changed to ${selected.toUpperCase()}`);
            });
        });

        document.addEventListener('click', (e) => {
            if (!themeBtn.contains(e.target) && !themeDropdown.contains(e.target)) {
                themeDropdown.classList.add('hidden');
            }
        });
    }
}

// Initial Setup
document.addEventListener('DOMContentLoaded', async () => {
    initThemeManager();

    // 1. Load Centralized Settings from Backend (Single Source of Truth)
    await loadCentralizedSettings();
    await loadEmbeddingModels();

    // 2. Load backend data states
    await fetchChats();
    await fetchIndexedDocs();

    // 3. Restore current active chat session on browser refresh if present
    const activeId = localStorage.getItem('antigravity_rag_active_id');
    if (activeId && state.chats.some(c => c.id === activeId)) {
        await loadChat(activeId);
    } else {
        showWelcomeView();
    }
    
    initIcons();
    setupEventListeners();

    // Sync initial state of top new chat button
    const topNewChatBtn = document.getElementById('top-new-chat-btn');
    if (topNewChatBtn) {
        const isCollapsed = appContainer.classList.contains('sidebar-collapsed');
        if (isCollapsed) {
            topNewChatBtn.classList.remove('hidden');
        } else {
            topNewChatBtn.classList.add('hidden');
        }
    }
});

// Event Listeners Configuration
function setupEventListeners() {
    // New Chat Button
    newChatBtn.addEventListener('click', createNewChat);

    // Top New Chat Button
    const topNewChatBtn = document.getElementById('top-new-chat-btn');
    if (topNewChatBtn) {
        topNewChatBtn.addEventListener('click', createNewChat);
    }

    // Sidebar Collapsible Toggle Button
    toggleSidebarBtn.addEventListener('click', () => {
        const isCollapsed = appContainer.classList.toggle('sidebar-collapsed');
        toggleSidebarBtn.title = isCollapsed ? "Expand Sidebar" : "Collapse Sidebar";
        
        if (topNewChatBtn) {
            if (isCollapsed) {
                topNewChatBtn.classList.remove('hidden');
            } else {
                topNewChatBtn.classList.add('hidden');
            }
        }
    });

    // Config panel toggle
    toggleConfigBtn.addEventListener('click', () => {
        configDrawer.classList.toggle('open');
        if (configDrawer.classList.contains('open')) {
            updatePerformanceSidebarStats();
        }
    });
    closeConfigBtn.addEventListener('click', () => {
        configDrawer.classList.remove('open');
    });

    // Helper functions for auto-collapsing sidebars
    function collapseSidebar() {
        if (!appContainer.classList.contains('sidebar-collapsed')) {
            appContainer.classList.add('sidebar-collapsed');
            toggleSidebarBtn.title = "Expand Sidebar";
            if (topNewChatBtn) {
                topNewChatBtn.classList.remove('hidden');
            }
        }
    }

    function closeConfigDrawer() {
        if (configDrawer.classList.contains('open')) {
            configDrawer.classList.remove('open');
        }
    }

    // Auto-collapse sidebars when clicking anywhere on the chat window / main area
    document.addEventListener('click', (e) => {
        const sidebar = document.querySelector('.sidebar');
        
        // Close RAG config drawer if click is outside drawer and its toggle button
        if (configDrawer.classList.contains('open') &&
            !configDrawer.contains(e.target) &&
            !toggleConfigBtn.contains(e.target)) {
            closeConfigDrawer();
        }

        // Auto-collapse left sidebar if click is anywhere outside sidebar and toggle button
        if (!appContainer.classList.contains('sidebar-collapsed') &&
            sidebar && !sidebar.contains(e.target) &&
            !toggleSidebarBtn.contains(e.target)) {
            collapseSidebar();
        }
    });

    // Settings Modal (Document DB & System Prompt) toggle
    const openSettingsBtn = document.getElementById('open-settings-btn');
    const closeSettingsBtn = document.getElementById('close-settings-btn');
    const settingsModal = document.getElementById('settings-modal');

    if (openSettingsBtn && closeSettingsBtn && settingsModal) {
        openSettingsBtn.addEventListener('click', () => {
            settingsModal.classList.remove('hidden');
            // Refresh textarea view with current saved prompt
            const promptArea = document.getElementById('val-system-prompt');
            if (promptArea) {
                promptArea.value = localStorage.getItem('rag_system_prompt') || '';
            }
            // Load API keys & cloud model configuration from backend
            loadAPIKeys();
            loadEmbeddingModels();
        });
        closeSettingsBtn.addEventListener('click', () => {
            settingsModal.classList.add('hidden');
        });
        settingsModal.addEventListener('click', (e) => {
            if (e.target === settingsModal) {
                settingsModal.classList.add('hidden');
            }
        });

        // Tabs switching inside Settings Modal
        settingsModal.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                settingsModal.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                settingsModal.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
                
                btn.classList.add('active');
                const tabId = btn.getAttribute('data-tab');
                const pane = document.getElementById(tabId);
                if (pane) pane.classList.add('active');
            });
        });

        // Save Custom System Prompt Instructions
        const savePromptBtn = document.getElementById('save-system-prompt-btn');
        const systemPromptTextarea = document.getElementById('val-system-prompt');
        if (savePromptBtn && systemPromptTextarea) {
            savePromptBtn.addEventListener('click', async () => {
                const newPrompt = systemPromptTextarea.value.trim();
                state.systemPrompt = newPrompt;
                localStorage.setItem('rag_system_prompt', newPrompt);
                try {
                    await fetch('/api/settings', {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ system_prompt: newPrompt })
                    });
                } catch (err) {
                    console.error("Error saving system prompt:", err);
                }
                showToast("System instructions saved. RAG app behavior updated!");
                settingsModal.classList.add('hidden');
            });
        }

        // Save API Keys & Cloud Model Connections
        const saveAPIKeysBtn = document.getElementById('save-api-keys-btn');
        if (saveAPIKeysBtn) {
            saveAPIKeysBtn.addEventListener('click', () => {
                saveAPIKeys();
            });
        }

        // Provider & Submodel Select change listeners for API Keys tab (Two-Way Sync)
        const providerSelect = document.getElementById('api-provider-select');
        const submodelSelect = document.getElementById('api-submodel-select');
        if (providerSelect) {
            providerSelect.addEventListener('change', () => {
                updateAPITabUI();
                if (submodelSelect && submodelSelect.value) {
                    selectModel(submodelSelect.value, true, true);
                }
            });
        }
        if (submodelSelect) {
            submodelSelect.addEventListener('change', () => {
                if (submodelSelect.value) {
                    selectModel(submodelSelect.value, true, true);
                }
            });
        }

        // Embedding Models Tab Event Listeners
        const embedSelect = document.getElementById('embedding-model-select');
        if (embedSelect) {
            embedSelect.addEventListener('change', (e) => {
                updateEmbeddingModelDetailsCard(e.target.value);
            });
        }

        const saveEmbedBtn = document.getElementById('save-embedding-model-btn');
        if (saveEmbedBtn) {
            saveEmbedBtn.addEventListener('click', activateEmbeddingModel);
        }

        const toggleAddEmbedBtn = document.getElementById('toggle-add-embedding-btn');
        const addEmbedFormContainer = document.getElementById('add-embedding-form-container');
        if (toggleAddEmbedBtn && addEmbedFormContainer) {
            toggleAddEmbedBtn.addEventListener('click', () => {
                addEmbedFormContainer.classList.toggle('hidden');
            });
        }

        const submitCustomEmbedBtn = document.getElementById('submit-custom-embedding-btn');
        if (submitCustomEmbedBtn) {
            submitCustomEmbedBtn.addEventListener('click', registerCustomEmbeddingModel);
        }

        // Toggle API key field when switching custom embed type radio buttons
        document.querySelectorAll('input[name="custom-embed-type"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                const keyWrapper = document.getElementById('custom-embed-key-wrapper');
                if (keyWrapper) {
                    if (e.target.value === 'paid') {
                        keyWrapper.classList.remove('hidden');
                    } else {
                        keyWrapper.classList.add('hidden');
                    }
                }
            });
        });
    }

    // Custom Model dropdown toggler
    modelPillBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isHidden = modelDropdownMenu.classList.toggle('hidden');
        modelPillBtn.classList.toggle('active', !isHidden);
        if (!isHidden) {
            const activeItem = modelDropdownMenu.querySelector('.dropdown-item.active');
            if (activeItem) {
                setTimeout(() => {
                    activeItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
                }, 50);
            }
        }
    });


    // Custom Model selection items
    document.querySelectorAll('.model-dropdown-menu .dropdown-item').forEach(item => {
        item.addEventListener('click', (e) => {
            const val = item.getAttribute('data-value');
            selectModel(val, true);
            modelDropdownMenu.classList.add('hidden');
            modelPillBtn.classList.remove('active');
        });
    });

    // Close model dropdown when clicking anywhere else
    document.addEventListener('click', (e) => {
        if (!modelPillBtn.contains(e.target) && !modelDropdownMenu.contains(e.target)) {
            modelDropdownMenu.classList.add('hidden');
            modelPillBtn.classList.remove('active');
        }
    });

    // Custom Search Mode Dropdown (Local vs Web)
    const searchModeBtn = document.getElementById('search-mode-btn');
    const searchModeName = document.getElementById('search-mode-name');
    const searchModeIcon = document.getElementById('search-mode-icon');
    const searchModeDropdownMenu = document.getElementById('search-mode-dropdown-menu');

    if (searchModeBtn && searchModeDropdownMenu) {
        searchModeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isHidden = searchModeDropdownMenu.classList.toggle('hidden');
            searchModeBtn.classList.toggle('active', !isHidden);
        });

        document.querySelectorAll('#search-mode-dropdown-menu .dropdown-item').forEach(item => {
            item.addEventListener('click', () => {
                const mode = item.getAttribute('data-search-mode');
                selectSearchMode(mode);
                searchModeDropdownMenu.classList.add('hidden');
                searchModeBtn.classList.remove('active');
            });
        });

        document.addEventListener('click', (e) => {
            if (!searchModeBtn.contains(e.target) && !searchModeDropdownMenu.contains(e.target)) {
                searchModeDropdownMenu.classList.add('hidden');
                searchModeBtn.classList.remove('active');
            }
        });
    }

    function selectSearchMode(mode) {
        state.searchMode = mode;
        document.querySelectorAll('#search-mode-dropdown-menu .dropdown-item').forEach(item => {
            const isMatch = item.getAttribute('data-search-mode') === mode;
            item.classList.toggle('active', isMatch);
        });
        
        if (mode === 'web') {
            if (searchModeName) searchModeName.textContent = 'Web';
            if (searchModeIcon) {
                searchModeIcon.outerHTML = `<span id="search-mode-icon" style="display:inline-flex;align-items:center;margin-right:2px;">${getGoogleGSVG(13)}</span>`;
            }
            showToast('Search Mode: Web (Google Live Search enabled for prompts)');
        } else {
            if (searchModeName) searchModeName.textContent = 'Local';
            const currentIcon = document.getElementById('search-mode-icon');
            if (currentIcon) {
                currentIcon.outerHTML = `<i data-lucide="database" id="search-mode-icon" style="width:13px;height:13px;color:var(--accent-purple,#8b5cf6);"></i>`;
            }
            showToast('Search Mode: Local (Vector Knowledge Base enabled)');
        }
        initIcons();
    }

    // Textarea input auto-grow
    promptTextarea.addEventListener('input', () => {
        autoGrowTextarea();
        toggleSendButton();
    });

    // Handle Enter to send, Shift+Enter for new line
    promptTextarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // File attachments buttons
    attachBtn.addEventListener('click', () => hiddenFileInput.click());
    hiddenFileInput.addEventListener('change', handleFilePicker);

    // Clipboard Paste event inside textarea
    promptTextarea.addEventListener('paste', handleClipboardPaste);

    // Global Drag & Drop for Chat Area
    window.addEventListener('dragenter', handleWindowDragEnter);
    dragDropOverlay.addEventListener('dragover', (e) => e.preventDefault());
    dragDropOverlay.addEventListener('dragleave', handleWindowDragLeave);
    dragDropOverlay.addEventListener('drop', handleWindowDrop);

    // Database Panel Upload Zone
    dbUploadZone.addEventListener('click', () => dbFileInput.click());
    dbFileInput.addEventListener('change', handleDBFilePicker);
    dbUploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dbUploadZone.classList.add('dragover');
    });
    dbUploadZone.addEventListener('dragleave', () => {
        dbUploadZone.classList.remove('dragover');
    });
    dbUploadZone.addEventListener('drop', handleDBDrop);

    // Parameter sliders
    paramTopK.addEventListener('input', (e) => {
        state.ragSettings.topK = parseInt(e.target.value);
        valTopK.textContent = state.ragSettings.topK;
        localStorage.setItem('antigravity_rag_settings', JSON.stringify(state.ragSettings));
    });
    paramSimilarity.addEventListener('input', (e) => {
        state.ragSettings.similarity = parseFloat(e.target.value);
        valSimilarity.textContent = state.ragSettings.similarity.toFixed(2);
        localStorage.setItem('antigravity_rag_settings', JSON.stringify(state.ragSettings));
    });
    paramTemperature.addEventListener('input', (e) => {
        state.ragSettings.temperature = parseFloat(e.target.value);
        valTemperature.textContent = state.ragSettings.temperature.toFixed(1);
        localStorage.setItem('antigravity_rag_settings', JSON.stringify(state.ragSettings));
    });

    // Welcome Suggestions
    document.querySelectorAll('.suggestion-card').forEach(card => {
        card.addEventListener('click', () => {
            promptTextarea.value = card.getAttribute('data-prompt');
            autoGrowTextarea();
            toggleSendButton();
            promptTextarea.focus();
        });
    });

    // Send Button click
    sendBtn.addEventListener('click', () => {
        if (sendBtn.classList.contains('stop-mode')) {
            if (activeAbortController) {
                activeAbortController.abort();
                showToast("Generation stopped.");
            }
        } else {
            sendMessage();
        }
    });

    // Viewport Scroll Listener
    chatViewport.addEventListener('scroll', handleViewportScroll);

    // Scroll Down Button Click
    scrollDownBtn.addEventListener('click', () => {
        chatViewport.scrollTo({ top: chatViewport.scrollHeight, behavior: 'smooth' });
        scrollDownBtn.classList.add('hidden');
    });

    // Copy Prompt Button
    const copyPromptBtn = document.getElementById('copy-prompt-btn');
    if (copyPromptBtn) {
        copyPromptBtn.addEventListener('click', () => {
            const text = promptTextarea.value.trim();
            if (text) {
                copyToClipboard(text).then(() => {
                    copyPromptBtn.innerHTML = '<i data-lucide="check"></i>';
                    initIcons();
                    showToast('Prompt copied!');
                    setTimeout(() => {
                        copyPromptBtn.innerHTML = '<i data-lucide="clipboard"></i>';
                        initIcons();
                    }, 2000);
                }).catch(() => showToast('Failed to copy prompt'));
            } else {
                showToast('Nothing to copy — prompt is empty.');
            }
        });
    }

    // VectorDB Refresh Button
    const vectordbRefreshBtn = document.getElementById('vectordb-refresh-btn');
    if (vectordbRefreshBtn) {
        vectordbRefreshBtn.addEventListener('click', async () => {
            vectordbRefreshBtn.classList.add('spinning');
            vectordbRefreshBtn.disabled = true;
            try {
                const resp = await fetch('/api/documents/sync', { method: 'POST' });
                if (resp.ok) {
                    const data = await resp.json();
                    await fetchIndexedDocs();
                    const msg = data.synced > 0
                        ? `✅ Synced ${data.synced} new document(s) into Vector DB!`
                        : '✅ Vector DB data updated & synced!';
                    showToast(msg);
                } else {
                    showToast('⚠️ Refresh failed. Check backend logs.');
                }
            } catch (err) {
                showToast('❌ Could not reach backend.');
            } finally {
                setTimeout(() => {
                    vectordbRefreshBtn.classList.remove('spinning');
                    vectordbRefreshBtn.disabled = false;
                }, 1500);
            }
        });
    }
}

// Knowledge Source Tab Switcher
window.switchKBSource = function(sourceType) {
    document.querySelectorAll('.kb-source-selector .source-radio-btn').forEach(btn => {
        if (btn.getAttribute('data-source') === sourceType) {
            btn.classList.add('active');
            const radio = btn.querySelector('input');
            if (radio) radio.checked = true;
        } else {
            btn.classList.remove('active');
        }
    });

    document.querySelectorAll('.source-pane').forEach(pane => {
        if (pane.id === `source-pane-${sourceType}`) {
            pane.classList.remove('hidden');
            pane.classList.add('active');
        } else {
            pane.classList.add('hidden');
            pane.classList.remove('active');
        }
    });
};

// Website URL Loader Handler
window.loadWebsiteURL = async function() {
    const urlInput = document.getElementById('kb-url-input');
    const loadBtn = document.getElementById('load-url-btn');
    const statsBanner = document.getElementById('url-ingest-stats');
    const statPages = document.getElementById('stat-pages');
    const statChunks = document.getElementById('stat-chunks');
    const statTime = document.getElementById('stat-time');
    const statStatus = document.getElementById('stat-status');

    if (!urlInput) return;
    const url = urlInput.value.trim();
    if (!url) {
        showToast('Please enter a valid website URL.');
        urlInput.focus();
        return;
    }

    loadBtn.disabled = true;
    loadBtn.innerHTML = '<i data-lucide="loader" class="spinning" style="width:14px;height:14px;"></i> <span>Loading Website...</span>';
    initIcons();

    if (statsBanner) statsBanner.classList.add('hidden');

    try {
        const resp = await fetch('/api/documents/url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        const result = await resp.json();

        if (resp.ok && result.status === 'success') {
            showToast(`✅ Loaded '${result.page_title}' (${result.chunks_created} chunks)!`);
            urlInput.value = '';

            if (statsBanner && statPages && statChunks && statTime && statStatus) {
                statPages.textContent = result.pages_loaded || 1;
                statChunks.textContent = result.chunks_created || 0;
                statTime.textContent = `${result.processing_time_ms || 0} ms`;
                statStatus.textContent = "Indexed ✅";
                statStatus.className = "url-stat-value text-emerald";
                statsBanner.classList.remove('hidden');
            }
            await fetchIndexedDocs();
        } else {
            const errorMsg = result.detail || result.message || 'Failed to process website URL.';
            showToast(`⚠️ ${errorMsg}`);
            if (statsBanner && statStatus) {
                statStatus.textContent = "Failed ❌";
                statStatus.className = "url-stat-value text-rose";
                statsBanner.classList.remove('hidden');
            }
        }
    } catch (err) {
        console.error("URL Ingestion Error:", err);
        showToast("❌ Network error connecting to URL loader service.");
    } finally {
        loadBtn.disabled = false;
        loadBtn.innerHTML = '<i data-lucide="download-cloud" style="width:14px;height:14px;"></i> <span>Load Website</span>';
        initIcons();
    }
};

// Plain Text Paste Loader Handler
window.loadPastedText = async function() {
    const titleInput = document.getElementById('kb-paste-title');
    const contentInput = document.getElementById('kb-paste-content');
    if (!titleInput || !contentInput) return;

    const title = titleInput.value.trim() || 'Untitled Paste';
    const content = contentInput.value.trim();
    if (!content) {
        showToast('Please enter text content to index.');
        contentInput.focus();
        return;
    }

    try {
        const resp = await fetch('/api/documents/paste', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content })
        });
        if (resp.ok) {
            showToast(`✅ Indexed pasted document '${title}'!`);
            titleInput.value = '';
            contentInput.value = '';
            await fetchIndexedDocs();
        } else {
            showToast('⚠️ Failed to index pasted text.');
        }
    } catch (err) {
        showToast('❌ Failed to reach server.');
    }
};

// Toggle scroll-to-bottom arrow button
function handleViewportScroll() {
    // Show only if chat has messages and user scrolled up
    const hasMessages = !messagesContainer.classList.contains('hidden');
    if (!hasMessages) {
        scrollDownBtn.classList.add('hidden');
        return;
    }

    const threshold = 180; // Show if scrolled up by 180px or more
    const isScrolledUp = chatViewport.scrollHeight - chatViewport.scrollTop - chatViewport.clientHeight > threshold;

    if (isScrolledUp) {
        scrollDownBtn.classList.remove('hidden');
    } else {
        scrollDownBtn.classList.add('hidden');
    }
}

// Centralized Select Active Model Utility (Two-Way Synchronization & Persistence)
async function selectModel(modelValue, saveToBackend = true, showNotify = true) {
    if (!modelValue) return;
    if (LEGACY_MODEL_MAP[modelValue]) {
        modelValue = LEGACY_MODEL_MAP[modelValue];
    }
    
    state.selectedModel = modelValue;
    const providerKey = getProviderFromModel(modelValue);
    state.selectedProvider = providerKey;

    // 1. Update Prompt Space LLM Pill Button Display
    const labelText = modelLabels[modelValue] || modelValue;
    if (modelPillName) {
        modelPillName.textContent = labelText;
    }

    // 2. Toggle active markers in Prompt Space LLM Dropdown Menu
    document.querySelectorAll('.model-dropdown-menu .dropdown-item').forEach(item => {
        if (item.getAttribute('data-value') === modelValue) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // 3. Two-Way Synchronization: Update Settings Modal Dropdowns
    const providerSelect = document.getElementById('api-provider-select');
    const submodelSelect = document.getElementById('api-submodel-select');
    if (providerSelect) {
        if (providerSelect.value !== providerKey) {
            providerSelect.value = providerKey;
            updateAPITabUI();
        }
        if (submodelSelect) {
            const hasOption = Array.from(submodelSelect.options).some(opt => opt.value === modelValue);
            if (hasOption) {
                submodelSelect.value = modelValue;
            }
        }
    }

    // 4. Update Client Caches
    localStorage.setItem('antigravity_rag_selected_model', state.selectedModel);
    localStorage.setItem('antigravity_rag_selected_provider', state.selectedProvider);
    cachedApiKeys.default_cloud_model = state.selectedModel;

    // 5. Update Active Chat Session Model if user explicitly changes model while in chat
    if (saveToBackend && state.activeChatId) {
        const chat = state.chats.find(c => c.id === state.activeChatId);
        if (chat) {
            chat.model = modelValue;
            fetch(`/api/chats/${state.activeChatId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ title: chat.title, model: modelValue })
            }).catch(err => console.error(err));
        }
    }

    // 6. Centralized Backend Persistence (PUT /api/settings)
    if (saveToBackend) {
        try {
            await fetch('/api/settings', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    active_provider: providerKey,
                    active_model: modelValue
                })
            });
        } catch (err) {
            console.error("[Settings Service] Model sync error:", err);
        }
    }

    if (showNotify) {
        showToast(`Switched active inference model to ${modelValue}`);
    }
}

// Adjust Textarea Height
function autoGrowTextarea() {
    promptTextarea.style.height = 'auto';
    promptTextarea.style.height = promptTextarea.scrollHeight + 'px';
}

// Toggle Send Button Activity
function toggleSendButton() {
    const hasText = promptTextarea.value.trim().length > 0;
    const hasStaged = state.stagedFiles.length > 0;
    sendBtn.disabled = !(hasText || hasStaged);
}

// File Attachment Logic
function addStagedFile(file) {
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const fileObj = {
                id: 'staged-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9),
                name: file.name,
                size: formatBytes(file.size),
                type: file.type,
                dataUrl: e.target.result,
                textContent: null
            };
            state.stagedFiles.push(fileObj);
            renderStagedFiles();
            toggleSendButton();
        };
        reader.readAsDataURL(file);
    } else if (file.type.startsWith('text/') || ['.py', '.js', '.css', '.html', '.json', '.csv', '.md'].some(ext => file.name.endsWith(ext))) {
        const textReader = new FileReader();
        textReader.onload = (e) => {
            const fileObj = {
                id: 'staged-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9),
                name: file.name,
                size: formatBytes(file.size),
                type: file.type,
                dataUrl: null,
                textContent: e.target.result
            };
            state.stagedFiles.push(fileObj);
            renderStagedFiles();
            toggleSendButton();
        };
        textReader.readAsText(file);
    } else if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
        const pdfReader = new FileReader();
        pdfReader.onload = (e) => {
            const fileObj = {
                id: 'staged-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9),
                name: file.name,
                size: formatBytes(file.size),
                type: file.type,
                dataUrl: e.target.result,
                textContent: null
            };
            state.stagedFiles.push(fileObj);
            renderStagedFiles();
            toggleSendButton();
        };
        pdfReader.readAsDataURL(file);
    } else {
        // Fallback for binary / office files (DOCX, XLSX, PPTX, etc.) -> Read as DataURL
        const binReader = new FileReader();
        binReader.onload = (e) => {
            const fileObj = {
                id: 'staged-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9),
                name: file.name,
                size: formatBytes(file.size),
                type: file.type || 'application/octet-stream',
                dataUrl: e.target.result,
                textContent: null
            };
            state.stagedFiles.push(fileObj);
            renderStagedFiles();
            toggleSendButton();
        };
        binReader.readAsDataURL(file);
    }
}

function handleFilePicker(e) {
    const files = Array.from(e.target.files);
    files.forEach(addStagedFile);
    hiddenFileInput.value = ''; // Reset input
}

// Clipboard Paste handler (Antigravity-like paste)
function handleClipboardPaste(e) {
    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
    let fileFound = false;

    for (let i = 0; i < items.length; i++) {
        if (items[i].kind === 'file') {
            const file = items[i].getAsFile();
            addStagedFile(file);
            fileFound = true;
        }
    }

    if (fileFound) {
        showToast("File pasted from clipboard!");
        setTimeout(() => promptTextarea.focus(), 50);
    }
}

// Render Staged Files Above Textarea
function renderStagedFiles() {
    if (state.stagedFiles.length === 0) {
        stagedPreview.classList.add('hidden');
        stagedPreview.innerHTML = '';
        return;
    }

    stagedPreview.classList.remove('hidden');
    stagedPreview.innerHTML = '';

    state.stagedFiles.forEach(file => {
        const chip = document.createElement('div');
        chip.className = 'attachment-chip';

        // Only render image thumbnail if it's actually an image type and not a document
        const isRealImage = file.type && file.type.startsWith('image/') && !['.pdf', '.docx', '.xlsx', '.pptx', '.csv', '.txt'].some(ext => file.name.toLowerCase().endsWith(ext));
        
        if (isRealImage && file.dataUrl) {
            const img = document.createElement('img');
            img.src = file.dataUrl;
            img.className = 'attachment-chip-img';
            chip.appendChild(img);
        } else {
            // Show appropriate file icon for PDFs, TXT, CSV, etc.
            const icon = document.createElement('i');
            icon.setAttribute('data-lucide', getFileIconName(file.name));
            icon.style.width = '14px';
            icon.style.height = '14px';
            icon.style.marginRight = '4px';
            chip.appendChild(icon);
        }

        const nameSpan = document.createElement('span');
        nameSpan.className = 'attachment-chip-name';
        nameSpan.textContent = file.name;
        nameSpan.title = `${file.name} (${file.size})`;
        chip.appendChild(nameSpan);

        const removeBtn = document.createElement('button');
        removeBtn.className = 'attachment-chip-remove';
        removeBtn.innerHTML = '<i data-lucide="x"></i>';
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            state.stagedFiles = state.stagedFiles.filter(f => f.id !== file.id);
            renderStagedFiles();
            toggleSendButton();
        });
        chip.appendChild(removeBtn);

        stagedPreview.appendChild(chip);
    });

    initIcons();
}

// Utilities for File Icons
function getFileIconName(filename) {
    if (!filename || typeof filename !== 'string') return 'file';
    const ext = filename.split('.').pop().toLowerCase();
    if (ext === 'pdf') return 'file-text';
    if (ext === 'csv') return 'table';
    if (ext === 'txt') return 'file-text';
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)) return 'image';
    return 'file';
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Global Drag & Drop Overlay Logic
let dragCounter = 0;
function handleWindowDragEnter(e) {
    e.preventDefault();
    dragCounter++;
    if (dragCounter === 1) {
        dragDropOverlay.classList.add('active');
    }
}

function handleWindowDragLeave(e) {
    e.preventDefault();
    dragCounter--;
    if (dragCounter === 0) {
        dragDropOverlay.classList.remove('active');
    }
}

function handleWindowDrop(e) {
    e.preventDefault();
    dragCounter = 0;
    dragDropOverlay.classList.remove('active');
    
    if (e.dataTransfer.files.length > 0) {
        Array.from(e.dataTransfer.files).forEach(addStagedFile);
        showToast(`Attached ${e.dataTransfer.files.length} drop files!`);
    }
}

// RAG Vector DB Document Upload Management
async function handleDBFilePicker(e) {
    const files = Array.from(e.target.files);
    await uploadDBDocuments(files);
    dbFileInput.value = '';
}

async function handleDBDrop(e) {
    e.preventDefault();
    dbUploadZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        await uploadDBDocuments(Array.from(e.dataTransfer.files));
    }
}

async function uploadDBDocuments(files) {
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    formData.append('chunk_size', 500);
    formData.append('chunk_overlap', 100);
    
    showToast(`Uploading & indexing ${files.length} document(s)...`);
    
    try {
        const response = await fetch('/api/documents/upload', {
            method: 'POST',
            body: formData
        });
        const results = await response.json();
        await fetchIndexedDocs();
        
        const successCount = results.filter(r => r.status === 'indexed').length;
        showToast(`✅ Successfully indexed ${successCount} document(s) into knowledge base!`);
    } catch (e) {
        console.error(e);
        showToast('❌ Error uploading documents.');
    }
}

async function syncKnowledgeBase() {
    const syncBtn = document.getElementById('sync-kb-btn');
    if (syncBtn) {
        syncBtn.disabled = true;
        syncBtn.innerHTML = '<i data-lucide="loader-2" style="width:14px;height:14px;animation:spin 1s linear infinite;"></i> Syncing...';
        initIcons();
    }
    showToast('🔄 Scanning backend/data/ folder...');
    try {
        const response = await fetch('/api/documents/sync', { method: 'POST' });
        const result = await response.json();
        await fetchIndexedDocs();
        const msg = result.synced > 0
            ? `✅ Synced ${result.synced} new file(s): ${result.files.join(', ')}`
            : '✅ Knowledge base is already up to date.';
        showToast(msg);
        if (result.errors && result.errors.length > 0) {
            console.warn('Sync errors:', result.errors);
        }
    } catch (e) {
        console.error(e);
        showToast('❌ Sync failed. Check server logs.');
    } finally {
        if (syncBtn) {
            syncBtn.disabled = false;
            syncBtn.innerHTML = '<i data-lucide="refresh-cw" style="width:14px;height:14px;"></i> Sync from data/';
            initIcons();
        }
    }
}

async function clearEntireVectorDb() {
    if (!confirm('Are you absolutely sure you want to delete the entire vector database, including all documents, collections, local uploaded cache files, and crawler registries? This action cannot be undone.')) {
        return;
    }
    
    const clearBtn = document.getElementById('clear-vdb-btn');
    if (clearBtn) {
        clearBtn.disabled = true;
        clearBtn.innerHTML = '<i data-lucide="loader-2" style="width:14px;height:14px;animation:spin 1s linear infinite;"></i> Clearing...';
        initIcons();
    }
    
    showToast('🗑️ Purging entire database...');
    try {
        const response = await fetch('/api/documents', { method: 'DELETE' });
        if (response.ok) {
            const result = await response.json();
            showToast('✅ Vector database successfully cleared!');
            await fetchIndexedDocs();
        } else {
            const err = await response.json();
            showToast(`❌ Failed to clear database: ${err.detail || 'Internal server error'}`);
        }
    } catch (e) {
        console.error(e);
        showToast('❌ Clear failed. Check server logs.');
    } finally {
        if (clearBtn) {
            clearBtn.disabled = false;
            clearBtn.innerHTML = '<i data-lucide="trash-2" style="width:14px;height:14px;"></i> Clear Entire Vector DB';
            initIcons();
        }
    }
}


function renderIndexedDocsList() {
    indexedDocsList.innerHTML = '';
    indexedCountLabel.textContent = state.indexedDocuments.length;
    
    state.indexedDocuments.forEach(doc => {
        const li = document.createElement('li');
        li.className = 'indexed-doc-item';
        
        const infoDiv = document.createElement('div');
        infoDiv.className = 'indexed-doc-info';
        
        const icon = document.createElement('i');
        icon.setAttribute('data-lucide', getFileIconName(doc.name));
        infoDiv.appendChild(icon);
        
        const nameSpan = document.createElement('span');
        nameSpan.className = 'indexed-doc-name';
        nameSpan.textContent = doc.name;
        nameSpan.title = doc.name;
        infoDiv.appendChild(nameSpan);
        
        li.appendChild(infoDiv);
        
        const sizeSpan = document.createElement('span');
        sizeSpan.className = 'indexed-doc-size';
        sizeSpan.textContent = doc.size;
        li.appendChild(sizeSpan);
        
        const delBtn = document.createElement('button');
        delBtn.className = 'indexed-doc-delete';
        delBtn.innerHTML = '<i data-lucide="trash-2"></i>';
        delBtn.title = 'Delete and purge vector indexes';
        delBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            try {
                await fetch(`/api/documents/${doc.id}`, { method: 'DELETE' });
                await fetchIndexedDocs();
                showToast(`Purged vector indexes for ${doc.name}`);
            } catch (err) {
                console.error(err);
                showToast("Failed to delete document.");
            }
        });
        li.appendChild(delBtn);
        
        indexedDocsList.appendChild(li);
    });
    
    initIcons();
}

function updateDBBadges() {
    const count = state.indexedDocuments.length;
    dbDocCount.textContent = `${count} Document${count !== 1 ? 's' : ''} Indexed`;
}

// Chat Persistence & State UI
async function loadChat(chatId) {
    state.activeChatId = chatId;
    localStorage.setItem('antigravity_rag_active_id', chatId);

    // Toggle active state in sidebar UI
    document.querySelectorAll('.chat-item').forEach(item => {
        if (item.getAttribute('data-id') === chatId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    const chat = state.chats.find(c => c.id === chatId);
    if (!chat) return;

    // Ensure active chat uses current user-selected model
    if (state.selectedModel) {
        chat.model = state.selectedModel;
    }

    try {
        const response = await fetch(`/api/chats/${chatId}/messages`);
        if (!response.ok) {
            if (response.status === 404) {
                // Stale active chat -> clear it and refresh chat list
                showWelcomeView();
                await fetchChats();
                return;
            }
            throw new Error(`Failed to load messages (${response.status})`);
        }
        const messages = await response.json();
        
        // Render Messages
        if (!Array.isArray(messages) || messages.length === 0) {
            showWelcomeView();
        } else {
            welcomeView.classList.add('hidden');
            messagesContainer.classList.remove('hidden');
            messagesContainer.innerHTML = '';
            
            messages.forEach(msg => {
                renderMessageBubble(msg);
            });
            scrollToBottom();
        }
    } catch (e) {
        console.error(e);
    }
}

function showWelcomeView() {
    welcomeView.classList.remove('hidden');
    messagesContainer.classList.add('hidden');
    messagesContainer.innerHTML = '';
    state.activeChatId = null;
    localStorage.removeItem('antigravity_rag_active_id');
    document.querySelectorAll('.chat-item').forEach(item => item.classList.remove('active'));
}

async function createNewChat() {
    try {
        const response = await fetch('/api/chats', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                title: 'Untitled Chat',
                model: state.selectedModel
            })
        });
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            showToast(errData.detail || "Failed to create new chat");
            return;
        }
        const newChat = await response.json();
        if (!newChat || !newChat.id) {
            showToast("Failed to create new chat: invalid server response");
            return;
        }
        
        state.chats.unshift(newChat);
        state.activeChatId = newChat.id;
        localStorage.setItem('antigravity_rag_active_id', newChat.id);
        
        renderRecentChatsList();
        await loadChat(newChat.id);
        
        showToast("Created a new conversation panel");
        promptTextarea.focus();
    } catch (e) {
        console.error(e);
        showToast("Error creating chat");
    }
}

async function deleteChat(chatId, e) {
    if (e) e.stopPropagation();
    
    try {
        await fetch(`/api/chats/${chatId}`, { method: 'DELETE' });
        await fetchChats();
        
        if (state.activeChatId === chatId) {
            if (state.chats.length > 0) {
                loadChat(state.chats[0].id);
            } else {
                showWelcomeView();
            }
        }
        showToast("Deleted chat from history");
    } catch (err) {
        console.error(err);
    }
}

async function renameChat(chatId, newTitle) {
    if (newTitle.trim().length === 0) return;
    
    try {
        await fetch(`/api/chats/${chatId}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ title: newTitle.trim() })
        });
        await fetchChats();
    } catch (err) {
        console.error(err);
    }
}

function renderRecentChatsList() {
    sidebarList.innerHTML = '';
    
    if (state.chats.length === 0) {
        const emptyState = document.createElement('div');
        emptyState.className = 'recent-chats-empty';
        emptyState.style.padding = '16px 12px';
        emptyState.style.fontSize = '13px';
        emptyState.style.color = 'var(--text-muted)';
        emptyState.style.textAlign = 'center';
        emptyState.textContent = 'No chat history yet';
        sidebarList.appendChild(emptyState);
        return;
    }

    state.chats.forEach(chat => {
        const item = document.createElement('div');
        item.className = 'chat-item';
        item.setAttribute('data-id', chat.id);
        if (chat.id === state.activeChatId) {
            item.classList.add('active');
        }

        const msgIcon = document.createElement('i');
        msgIcon.setAttribute('data-lucide', 'message-square');
        msgIcon.className = 'chat-item-icon';
        item.appendChild(msgIcon);

        const textWrapper = document.createElement('div');
        textWrapper.className = 'chat-item-text-wrapper';
        
        const titleSpan = document.createElement('span');
        titleSpan.className = 'chat-item-title';
        titleSpan.textContent = chat.title;
        titleSpan.title = chat.title;
        textWrapper.appendChild(titleSpan);
        item.appendChild(textWrapper);

        // Hover Action tools (Rename & Delete)
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'chat-item-actions';
        
        const editBtn = document.createElement('button');
        editBtn.className = 'chat-action-btn edit-btn';
        editBtn.title = "Rename chat";
        editBtn.innerHTML = '<i data-lucide="pencil" style="width:13px;height:13px;"></i>';
        editBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleRenameMode(chat.id, item, textWrapper, titleSpan, actionsDiv);
        });
        actionsDiv.appendChild(editBtn);

        const delBtn = document.createElement('button');
        delBtn.className = 'chat-action-btn delete-btn';
        delBtn.title = "Delete chat";
        delBtn.innerHTML = '<i data-lucide="trash-2" style="width:13px;height:13px;"></i>';
        delBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteChat(chat.id, e);
        });
        actionsDiv.appendChild(delBtn);

        item.appendChild(actionsDiv);

        // Double-click to rename
        item.addEventListener('dblclick', (e) => {
            e.stopPropagation();
            toggleRenameMode(chat.id, item, textWrapper, titleSpan, actionsDiv);
        });

        item.addEventListener('click', () => {
            if (!item.classList.contains('editing')) {
                loadChat(chat.id);
            }
        });

        sidebarList.appendChild(item);
    });

    initIcons();
}

function toggleRenameMode(chatId, item, wrapper, span, actionsDiv) {
    if (item.classList.contains('editing')) return;
    item.classList.add('editing');
    
    const currentText = span.textContent;
    wrapper.innerHTML = '';
    if (actionsDiv) actionsDiv.style.display = 'none';
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'chat-title-input';
    input.value = currentText;
    wrapper.appendChild(input);
    
    const editActions = document.createElement('div');
    editActions.style.display = 'flex';
    editActions.style.alignItems = 'center';
    editActions.style.gap = '4px';
    editActions.style.marginLeft = '4px';

    const checkBtn = document.createElement('button');
    checkBtn.className = 'chat-action-btn edit-btn';
    checkBtn.title = "Save title";
    checkBtn.innerHTML = '<i data-lucide="check" style="width:13px;height:13px;color:#10b981;"></i>';

    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'chat-action-btn delete-btn';
    cancelBtn.title = "Cancel";
    cancelBtn.innerHTML = '<i data-lucide="x" style="width:13px;height:13px;color:#ef4444;"></i>';

    editActions.appendChild(checkBtn);
    editActions.appendChild(cancelBtn);
    item.appendChild(editActions);

    if (window.lucide) window.lucide.createIcons();
    input.focus();
    input.select();

    let isFinished = false;
    const saveRename = async () => {
        if (isFinished) return;
        isFinished = true;
        const val = input.value.trim();
        if (val.length > 0 && val !== currentText) {
            await renameChat(chatId, val);
        } else {
            renderRecentChatsList();
        }
    };

    const cancelRename = () => {
        if (isFinished) return;
        isFinished = true;
        renderRecentChatsList();
    };

    checkBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        saveRename();
    });

    cancelBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        cancelRename();
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveRename();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            cancelRename();
        }
    });

    input.addEventListener('blur', (e) => {
        setTimeout(() => {
            if (!isFinished) saveRename();
        }, 150);
    });
}

function scrollToBottom() {
    chatViewport.scrollTop = chatViewport.scrollHeight;
}

// Render Messages inside the Viewport container
function renderMessageBubble(msg) {
    const isUser = msg.sender === 'user';
    
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user-msg' : 'assistant-msg'}`;
    if (msg.id) {
        msgDiv.id = msg.id;
    }
    
    const avatarContainer = document.createElement('div');
    avatarContainer.className = 'message-avatar-container';
    
    const avatar = document.createElement('div');
    avatar.className = `msg-avatar ${isUser ? 'user' : 'assistant'}`;
    avatar.textContent = isUser ? 'K' : 'AI';
    
    if (isUser) {
        const img = document.createElement('img');
        img.src = 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=100&q=80';
        img.className = 'msg-avatar';
        avatarContainer.appendChild(img);
    } else {
        avatarContainer.appendChild(avatar);
    }
    
    msgDiv.appendChild(avatarContainer);
    
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'message-content-wrapper';
    
    const isWebSearch = !isUser && msg.text && (msg.text.includes('Web Search Results') || msg.text.includes('Google Search'));
    const senderSpan = document.createElement('span');
    senderSpan.className = 'message-sender';
    if (isUser) {
        senderSpan.textContent = 'You';
    } else if (isWebSearch) {
        senderSpan.style.color = '#4285f4';
        senderSpan.style.fontWeight = '600';
        senderSpan.innerHTML = '<i data-lucide="globe" style="width:13px;height:13px;color:#4285f4;margin-right:4px;"></i> Google Live Search Engine';
    } else {
        senderSpan.textContent = 'AI Assistant';
    }
    contentWrapper.appendChild(senderSpan);
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = renderMarkdown(msg.text);
    contentWrapper.appendChild(bubble);

    // Add Action Bar (Edit, Copy, Re-search Web for User & Assistant)
    const actionDiv = document.createElement('div');
    actionDiv.className = 'msg-actions';
    
    if (isUser) {
        const editBtn = document.createElement('button');
        editBtn.className = 'action-btn edit-msg-btn';
        editBtn.innerHTML = '<i data-lucide="pencil" style="width:13px;height:13px;"></i>';
        editBtn.title = "Edit message";
        actionDiv.appendChild(editBtn);

        // Copy user prompt button
        const copyUserBtn = document.createElement('button');
        copyUserBtn.className = 'action-btn';
        copyUserBtn.innerHTML = '<i data-lucide="copy" style="width:13px;height:13px;"></i>';
        copyUserBtn.title = "Copy message";
        actionDiv.appendChild(copyUserBtn);

        // Google / Web Search prompt button
        const searchWebBtn = document.createElement('button');
        searchWebBtn.className = 'action-btn search-web-btn';
        searchWebBtn.innerHTML = getGoogleGSVG(13);
        searchWebBtn.title = "Search Google / Web for this prompt";
        actionDiv.appendChild(searchWebBtn);

        searchWebBtn.addEventListener('click', () => {
            executeWebSearch(msg.text);
        });

        copyUserBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            copyToClipboard(msg.text).then(() => {
                copyUserBtn.innerHTML = '<i data-lucide="check" style="width:13px;height:13px;color:var(--accent-emerald,#10b981);"></i>';
                initIcons();
                showToast('Prompt copied!');
                setTimeout(() => {
                    copyUserBtn.innerHTML = '<i data-lucide="copy" style="width:13px;height:13px;"></i>';
                    initIcons();
                }, 2000);
            }).catch(err => {
                console.error("Copy prompt error:", err);
                showToast('Failed to copy text');
            });
        });
        
        editBtn.addEventListener('click', () => {
            const originalText = msg.text;
            bubble.innerHTML = `
                <div class="edit-msg-form">
                    <textarea class="edit-msg-textarea" rows="3">${originalText}</textarea>
                    <div class="edit-msg-buttons">
                        <button class="btn btn-primary btn-save">Save & Submit</button>
                        <button class="btn btn-secondary btn-cancel">Cancel</button>
                    </div>
                </div>
            `;
            actionDiv.style.display = 'none';
            
            bubble.querySelector('.btn-cancel').addEventListener('click', () => {
                bubble.innerHTML = renderMarkdown(originalText);
                actionDiv.style.display = 'block';
                initIcons();
            });
            
            bubble.querySelector('.btn-save').addEventListener('click', async () => {
                const newText = bubble.querySelector('.edit-msg-textarea').value.trim();
                if (newText.length === 0) return;
                
                const currentMsgId = msgDiv.id;
                if (!currentMsgId || currentMsgId.startsWith('temp-user')) {
                    showToast("Please wait for response to finish before editing.");
                    return;
                }
                
                try {
                    const response = await fetch(`/api/chats/${state.activeChatId}/messages/truncate/${currentMsgId}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        promptTextarea.value = newText;
                        await loadChat(state.activeChatId);
                        sendMessage();
                    } else {
                        showToast("Failed to edit prompt: message truncate failed.");
                    }
                } catch (err) {
                    console.error(err);
                    showToast("Failed to edit prompt.");
                }
            });
        });
    } else {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'action-btn copy-msg-btn';
        copyBtn.innerHTML = '<i data-lucide="copy" style="width:13px;height:13px;"></i>';
        copyBtn.title = "Copy response";

        const editSearchBtn = document.createElement('button');
        editSearchBtn.className = 'action-btn edit-msg-btn';
        editSearchBtn.innerHTML = '<i data-lucide="pencil" style="width:13px;height:13px;color:#a78bfa;"></i>';
        editSearchBtn.title = "Edit & Re-search Google Web";

        const replyBtn = document.createElement('button');
        replyBtn.className = 'action-btn reply-msg-btn';
        replyBtn.innerHTML = '<i data-lucide="corner-up-left" style="width:13px;height:13px;"></i>';
        replyBtn.title = "Reply/Quote";

        const searchWebBtn = document.createElement('button');
        searchWebBtn.className = 'action-btn search-web-btn';
        searchWebBtn.innerHTML = getGoogleGSVG(13);
        searchWebBtn.title = "Re-search Google / Web for updated info";

        const thumbsUpBtn = document.createElement('button');
        thumbsUpBtn.className = 'action-btn thumbs-up-btn';
        thumbsUpBtn.innerHTML = '<i data-lucide="thumbs-up" style="width:13px;height:13px;"></i>';
        thumbsUpBtn.title = "Positive Feedback (Thumbs Up)";

        const thumbsDownBtn = document.createElement('button');
        thumbsDownBtn.className = 'action-btn thumbs-down-btn';
        thumbsDownBtn.innerHTML = '<i data-lucide="thumbs-down" style="width:13px;height:13px;"></i>';
        thumbsDownBtn.title = "Negative Feedback (Thumbs Down)";

        actionDiv.appendChild(copyBtn);
        actionDiv.appendChild(thumbsUpBtn);
        actionDiv.appendChild(thumbsDownBtn);
        actionDiv.appendChild(editSearchBtn);
        actionDiv.appendChild(replyBtn);
        actionDiv.appendChild(searchWebBtn);

        const targetId = msg.interaction_id || msg.id;

        thumbsUpBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            try {
                const resp = await fetch('/api/dataset/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ interaction_id: targetId, feedback: 'positive' })
                });
                if (resp.ok) {
                    thumbsUpBtn.style.color = '#10b981';
                    thumbsDownBtn.style.color = '';
                    showToast('👍 Positive feedback saved to dataset!');
                }
            } catch (err) {
                console.error("Feedback submission error:", err);
            }
        });

        thumbsDownBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            try {
                const resp = await fetch('/api/dataset/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ interaction_id: targetId, feedback: 'negative' })
                });
                if (resp.ok) {
                    thumbsDownBtn.style.color = '#ef4444';
                    thumbsUpBtn.style.color = '';
                    showToast('👎 Negative feedback saved to dataset!');
                }
            } catch (err) {
                console.error("Feedback submission error:", err);
            }
        });


        // Extract original query if available in text or fallback
        const queryMatch = msg.text ? msg.text.match(/\*"?([^"*]+)"?\*/) : null;
        const searchQuery = queryMatch ? queryMatch[1] : msg.text.substring(0, 100);

        searchWebBtn.addEventListener('click', () => {
            executeWebSearch(searchQuery);
        });

        editSearchBtn.addEventListener('click', () => {
            const currentText = searchQuery;
            bubble.innerHTML = `
                <div class="edit-msg-form">
                    <label style="font-size:11px;color:#a78bfa;font-weight:600;display:block;margin-bottom:4px;">Edit Search Query for Google Web:</label>
                    <textarea class="edit-msg-textarea" rows="2">${currentText}</textarea>
                    <div class="edit-msg-buttons" style="margin-top:8px;">
                        <button class="btn btn-primary btn-save" style="background:#4285f4;border-color:#4285f4;display:inline-flex;align-items:center;gap:4px;">${getGoogleGSVG(12)} Re-search Web</button>
                        <button class="btn btn-secondary btn-cancel">Cancel</button>
                    </div>
                </div>
            `;
            initIcons();
            actionDiv.style.display = 'none';

            bubble.querySelector('.btn-cancel').addEventListener('click', () => {
                bubble.innerHTML = renderMarkdown(msg.text);
                actionDiv.style.display = 'block';
                initIcons();
            });

            bubble.querySelector('.btn-save').addEventListener('click', () => {
                const newQuery = bubble.querySelector('.edit-msg-textarea').value.trim();
                if (newQuery.length > 0) {
                    executeWebSearch(newQuery);
                }
            });
        });
        
        copyBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            copyToClipboard(msg.text).then(() => {
                copyBtn.innerHTML = '<i data-lucide="check" style="width:13px;height:13px;color:var(--accent-emerald);"></i>';
                initIcons();
                showToast('Response copied!');
                setTimeout(() => {
                    copyBtn.innerHTML = '<i data-lucide="copy" style="width:13px;height:13px;"></i>';
                    initIcons();
                }, 1500);
            }).catch(err => {
                console.error("Copy response error:", err);
                showToast('Failed to copy response');
            });
        });

        replyBtn.addEventListener('click', () => {
            const formattedQuote = `> "${msg.text.substring(0, 100)}${msg.text.length > 100 ? '...' : ''}"\n\n`;
            promptTextarea.value = formattedQuote + promptTextarea.value;
            promptTextarea.focus();
            autoGrowTextarea();
            toggleSendButton();
        });
    }

    contentWrapper.appendChild(actionDiv);

    // Staged attachments rendering in bubbles
    if (isUser && msg.attachments && msg.attachments.length > 0) {
        const attachContainer = document.createElement('div');
        attachContainer.className = 'bubble-attachments';
        
        msg.attachments.forEach(file => {
            const isImage = file.type && file.type.startsWith('image/') && !['.pdf', '.docx', '.xlsx', '.pptx', '.csv', '.txt'].some(ext => file.name.toLowerCase().endsWith(ext));
            if (file.dataUrl && isImage) {
                const imgCard = document.createElement('div');
                imgCard.className = 'bubble-attachment-image-card';
                imgCard.innerHTML = `
                    <img src="${file.dataUrl}" alt="${file.name}" class="bubble-attached-image" />
                    <div class="image-card-overlay">
                        <span>${file.name}</span>
                    </div>
                `;
                imgCard.addEventListener('click', () => {
                    openLightbox(file.dataUrl, file.name);
                });
                attachContainer.appendChild(imgCard);
            } else {
                const pill = document.createElement('div');
                pill.className = 'bubble-attachment-pill';
                
                const icon = document.createElement('i');
                icon.setAttribute('data-lucide', getFileIconName(file.name));
                pill.appendChild(icon);
                
                const name = document.createElement('span');
                name.className = 'bubble-attachment-name';
                name.textContent = file.name;
                name.title = `${file.name} (${file.size})`;
                pill.appendChild(name);
                
                attachContainer.appendChild(pill);
            }
        });
        
        contentWrapper.appendChild(attachContainer);
    }

    // RAG source citations rendering in assistant message bubbles
    if (!isUser && msg.citations && msg.citations.length > 0) {
        const citationsWrapper = document.createElement('div');
        citationsWrapper.className = 'citations-wrapper';
        
        const header = document.createElement('div');
        header.className = 'citations-header';
        header.innerHTML = `
            <span><i data-lucide="shield-check" style="width:14px;height:14px;vertical-align:text-bottom;margin-right:6px;color:var(--accent-emerald);"></i>Retrieved RAG Sources (${msg.citations.length})</span>
            <i data-lucide="chevron-down" class="citations-toggle-icon" style="width:14px;height:14px;"></i>
        `;
        citationsWrapper.appendChild(header);
        
        const content = document.createElement('div');
        content.className = 'citations-content';
        
        msg.citations.forEach((source, idx) => {
            const fileName = source.name || source.source || `Source ${idx + 1}`;
            const scoreVal = typeof source.score === 'number' ? source.score.toFixed(2) : (source.score || '--');
            const card = document.createElement('div');
            card.className = 'citation-card';
            card.innerHTML = `
                <div class="citation-card-meta">
                    <span class="citation-card-filename">
                        <i data-lucide="${getFileIconName(fileName)}" style="width:12px;height:12px;"></i>
                        [Source ${idx + 1}] ${escapeHTML(fileName)}
                    </span>
                    <span class="citation-card-score">Score: ${scoreVal}</span>
                </div>
                <div class="citation-card-snippet">"${escapeHTML(source.snippet || '')}"</div>
            `;
            content.appendChild(card);
        });
        
        citationsWrapper.appendChild(content);
        
        header.addEventListener('click', () => {
            citationsWrapper.classList.toggle('open');
        });
        
        contentWrapper.appendChild(citationsWrapper);
    }

    // --- RAG Metrics Card (Correctness, Faithfulness, Groundedness, Confidence, Time, Cost) ---
    if (!isUser && msg.metrics) {
        const m = msg.metrics;
        const metricsCard = document.createElement('div');
        metricsCard.className = 'rag-metrics-card';

        function metricColor(val) {
            if (val >= 80) return '#10b981';
            if (val >= 60) return '#f59e0b';
            return '#ef4444';
        }
        function metricBar(val) {
            const color = metricColor(val);
            return `<div class="metric-bar-bg"><div class="metric-bar-fill" style="width:${val}%;background:${color};"></div></div>`;
        }

        metricsCard.innerHTML = `
            <div class="rag-metrics-header">
                <span><i data-lucide="bar-chart-2" style="width:13px;height:13px;vertical-align:text-bottom;margin-right:5px;color:#a78bfa;"></i>Response Metrics</span>
                <i data-lucide="chevron-down" class="metrics-toggle-icon" style="width:13px;height:13px;"></i>
            </div>
            <div class="rag-metrics-body">
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Correctness</span>
                        ${metricBar(m.correctness ?? 0)}
                        <span class="metric-value" style="color:${metricColor(m.correctness ?? 0)}">${m.correctness ?? 0}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Faithfulness</span>
                        ${metricBar(m.faithfulness ?? 0)}
                        <span class="metric-value" style="color:${metricColor(m.faithfulness ?? 0)}">${m.faithfulness ?? 0}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Groundedness</span>
                        ${metricBar(m.groundedness ?? 0)}
                        <span class="metric-value" style="color:${metricColor(m.groundedness ?? 0)}">${m.groundedness ?? 0}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Confidence</span>
                        ${metricBar(m.confidence ?? 0)}
                        <span class="metric-value" style="color:${metricColor(m.confidence ?? 0)}">${m.confidence ?? 0}%</span>
                    </div>
                </div>
                <div class="metrics-row-secondary">
                    <div class="metric-secondary-item">
                        <i data-lucide="clock" style="width:11px;height:11px;color:#94a3b8;margin-right:4px;"></i>
                        <span class="metric-secondary-label">Time Taken</span>
                        <span class="metric-secondary-value">${m.time_taken_s ?? '--'}s</span>
                    </div>
                    <div class="metric-secondary-item">
                        <i data-lucide="coins" style="width:11px;height:11px;color:#94a3b8;margin-right:4px;"></i>
                        <span class="metric-secondary-label">Token Cost</span>
                        <span class="metric-secondary-value">${m.token_cost ?? '--'}</span>
                    </div>
                </div>
            </div>
        `;

        const metricsHeader = metricsCard.querySelector('.rag-metrics-header');
        metricsHeader.addEventListener('click', () => {
            metricsCard.classList.toggle('open');
        });

        contentWrapper.appendChild(metricsCard);
    }
    
    // --- Suggestion Chips (ChatGPT-style follow-up suggestions & Google Search) ---
    if (!isUser && msg.suggestions && msg.suggestions.length > 0) {
        const suggestionsWrapper = document.createElement('div');
        suggestionsWrapper.className = 'suggestions-wrapper';
        
        msg.suggestions.forEach(suggestion => {
            const chip = document.createElement('button');
            const isGoogleSearch = suggestion.includes('Search Google') || suggestion.includes('Search Web') || suggestion.startsWith('🌐');
            chip.className = `suggestion-chip ${isGoogleSearch ? 'google-search-chip' : ''}`;
            
            let cleanText = suggestion.replace(/^🌐\s*/, '').replace(/^Search Google:\s*/i, '');
            if (isGoogleSearch) {
                chip.innerHTML = `${getGoogleGSVG(13)} <span>Search Google: ${escapeHTML(cleanText)}</span>`;
            } else {
                chip.innerHTML = `<span style="opacity:0.75; font-size:11px; font-weight:700;">↗</span> <span>${escapeHTML(suggestion)}</span>`;
            }
            
            chip.addEventListener('click', () => {
                if (isGoogleSearch) {
                    executeWebSearch(suggestion);
                } else {
                    const textarea = document.getElementById('prompt-textarea');
                    if (textarea) {
                        textarea.value = suggestion;
                        textarea.dispatchEvent(new Event('input'));
                        textarea.focus();
                        const btn = document.getElementById('send-btn');
                        if (btn && !btn.disabled) btn.click();
                    }
                }
            });
            suggestionsWrapper.appendChild(chip);
        });
        
        contentWrapper.appendChild(suggestionsWrapper);
    }
    
    msgDiv.appendChild(contentWrapper);
    messagesContainer.appendChild(msgDiv);
    
    initIcons();
}

window.copyCodeBlock = function(id) {
    const codeElem = document.getElementById(id);
    if (codeElem) {
        const text = codeElem.textContent;
        copyToClipboard(text).then(() => {
            const btn = document.querySelector(`[data-code-id="${id}"]`);
            if (btn) {
                btn.innerHTML = '<i data-lucide="check" style="width:12px;height:12px;margin-right:4px;color:var(--accent-emerald);"></i> Copied';
                initIcons();
                setTimeout(() => {
                    btn.innerHTML = '<i data-lucide="copy" style="width:12px;height:12px;margin-right:4px;"></i> Copy code';
                    initIcons();
                }, 2000);
            }
        });
    }
};

// Markdown parser mockup (supports headers, strong, bullet points, and codeblocks)
// ─────────────────────────────────────────────────────────────
// Self-contained VS Code-style Syntax Highlighter
// Supports: python, sql, javascript/js/ts, bash/shell, json, html, css
// ─────────────────────────────────────────────────────────────
function syntaxHighlight(code, lang) {
    // Escape HTML entities first
    let escaped = escapeHTML(code);

    const spanStore = [];
    const spanPlaceholder = (i) => `\x00SPAN${i}\x00`;
    const wrap = (cls, text) => {
        spanStore.push(`<span class="${cls}">${text}</span>`);
        return spanPlaceholder(spanStore.length - 1);
    };

    const C = {
        keyword:   (t) => wrap('hl-kw', t),
        string:    (t) => wrap('hl-str', t),
        comment:   (t) => wrap('hl-com', t),
        number:    (t) => wrap('hl-num', t),
        func:      (t) => wrap('hl-fn', t),
        decorator: (t) => wrap('hl-dec', t),
        builtin:   (t) => wrap('hl-bi', t),
        operator:  (t) => wrap('hl-op', t),
        tag:       (t) => wrap('hl-tag', t),
        attr:      (t) => wrap('hl-attr', t),
        variable:  (t) => wrap('hl-var', t),
    };

    // Apply string literals first using protected placeholders
    const strStore = [];
    const strPlaceholder = (i) => `\x00STR${i}\x00`;

    // Triple-quoted strings (Python)
    escaped = escaped.replace(/(&quot;&quot;&quot;[\s\S]*?&quot;&quot;&quot;|&#39;&#39;&#39;[\s\S]*?&#39;&#39;&#39;)/g, (m) => {
        strStore.push(C.string(m)); return strPlaceholder(strStore.length - 1);
    });
    // Double-quoted strings
    escaped = escaped.replace(/(&quot;(?:[^&]|&(?!quot;))*?&quot;)/g, (m) => {
        strStore.push(C.string(m)); return strPlaceholder(strStore.length - 1);
    });
    // Single-quoted strings
    escaped = escaped.replace(/(&#39;(?:[^&]|&(?!#39;))*?&#39;)/g, (m) => {
        strStore.push(C.string(m)); return strPlaceholder(strStore.length - 1);
    });

    const isPython = ['python', 'py'].includes(lang);
    const isSql    = ['sql'].includes(lang);
    const isJs     = ['javascript', 'js', 'typescript', 'ts', 'jsx', 'tsx'].includes(lang);
    const isBash   = ['bash', 'shell', 'sh', 'zsh'].includes(lang);
    const isJson   = ['json'].includes(lang);

    if (isPython) {
        // Decorators
        escaped = escaped.replace(/(^|\n)(@\w+)/gm, (m, p1, p2) => p1 + C.decorator(p2));
        // Comments
        escaped = escaped.replace(/(#[^\n]*)/g, (m) => {
            strStore.push(C.comment(m)); return strPlaceholder(strStore.length - 1);
        });
        // Keywords
        const kwds = /\b(def|class|import|from|return|if|elif|else|for|while|in|not|and|or|is|None|True|False|try|except|finally|with|as|pass|break|continue|raise|yield|lambda|global|nonlocal|del|assert|async|await)\b/g;
        escaped = escaped.replace(kwds, (m) => C.keyword(m));
        // Built-ins
        const builtins = /\b(print|len|range|int|str|float|list|dict|set|tuple|type|isinstance|enumerate|zip|map|filter|sorted|reversed|open|input|super|self|cls|any|all|min|max|sum|abs|round)\b/g;
        escaped = escaped.replace(builtins, (m) => C.builtin(m));
        // Function definitions
        escaped = escaped.replace(/\b(def|class)\s+(\w+)/g, (m, kw, name) => C.keyword(kw) + ' ' + C.func(name));
        // Numbers
        escaped = escaped.replace(/\b(\d+\.?\d*)\b/g, (m) => C.number(m));

    } else if (isSql) {
        // SQL keywords (case-insensitive)
        const sqlKwds = /\b(SELECT|FROM|WHERE|AND|OR|NOT|INSERT|INTO|UPDATE|SET|DELETE|CREATE|TABLE|DROP|ALTER|INDEX|JOIN|LEFT|RIGHT|INNER|OUTER|ON|AS|DISTINCT|ORDER|BY|GROUP|HAVING|LIMIT|OFFSET|UNION|ALL|IN|IS|NULL|LIKE|BETWEEN|EXISTS|CASE|WHEN|THEN|ELSE|END|PRIMARY|KEY|FOREIGN|REFERENCES|UNIQUE|DEFAULT|AUTO_INCREMENT|CONSTRAINT|BEGIN|COMMIT|ROLLBACK)\b/gi;
        escaped = escaped.replace(sqlKwds, (m) => C.keyword(m.toUpperCase()));
        // SQL functions
        const sqlFuncs = /\b(COUNT|SUM|AVG|MAX|MIN|COALESCE|NULLIF|CAST|CONVERT|NOW|DATE|YEAR|MONTH|DAY|TRIM|UPPER|LOWER|LENGTH|CONCAT|SUBSTRING|REPLACE|ROUND|FLOOR|CEIL|ABS|IIF|IF)\b/gi;
        escaped = escaped.replace(sqlFuncs, (m) => C.func(m.toUpperCase()));
        // Numbers
        escaped = escaped.replace(/\b(\d+\.?\d*)\b/g, (m) => C.number(m));
        // Comments
        escaped = escaped.replace(/(--[^\n]*)/g, (m) => {
            strStore.push(C.comment(m)); return strPlaceholder(strStore.length - 1);
        });

    } else if (isJs) {
        // Comments
        escaped = escaped.replace(/(\/\/[^\n]*)/g, (m) => {
            strStore.push(C.comment(m)); return strPlaceholder(strStore.length - 1);
        });
        const kwds = /\b(const|let|var|function|return|if|else|for|while|do|switch|case|break|continue|new|typeof|instanceof|this|class|extends|import|export|default|from|async|await|try|catch|finally|throw|true|false|null|undefined|void|delete|in|of|yield|static|get|set|super)\b/g;
        escaped = escaped.replace(kwds, (m) => C.keyword(m));
        // Function calls
        escaped = escaped.replace(/\b(\w+)(?=\s*\()/g, (m) => C.func(m));
        // Numbers
        escaped = escaped.replace(/\b(\d+\.?\d*)\b/g, (m) => C.number(m));

    } else if (isBash) {
        // Comments
        escaped = escaped.replace(/(#[^\n]*)/g, (m) => {
            strStore.push(C.comment(m)); return strPlaceholder(strStore.length - 1);
        });
        const kwds = /\b(if|then|else|elif|fi|for|do|done|while|case|esac|in|function|return|export|local|echo|cd|ls|mkdir|rm|cp|mv|cat|grep|sed|awk|chmod|sudo|apt|pip|npm|yarn|source)\b/g;
        escaped = escaped.replace(kwds, (m) => C.keyword(m));
        escaped = escaped.replace(/\$\w+/g, (m) => C.variable(m));
        escaped = escaped.replace(/\b(\d+)\b/g, (m) => C.number(m));

    } else if (isJson) {
        // JSON keys
        escaped = escaped.replace(/(&quot;[^&]*?&quot;)\s*:/g, (m, key) => C.attr(key) + m.slice(key.length));
        escaped = escaped.replace(/\b(true|false|null)\b/g, (m) => C.keyword(m));
        escaped = escaped.replace(/\b(\d+\.?\d*)\b/g, (m) => C.number(m));

    } else {
        // Generic: highlight obvious numbers and common keywords
        escaped = escaped.replace(/\b(\d+\.?\d*)\b/g, (m) => C.number(m));
    }

    // 1. Restore string placeholders
    strStore.forEach((val, i) => {
        escaped = escaped.replace(strPlaceholder(i), val);
    });

    // 2. Restore span placeholders
    spanStore.forEach((val, i) => {
        escaped = escaped.replace(spanPlaceholder(i), val);
    });

    return escaped;
}

function cleanMarkdownArtifacts(str) {
    if (!str) return '';
    return str
        .replace(/^#+\s+/gm, '')           // Strip leading hashes on headers
        .replace(/\*\*([^*]+)\*\*/g, '$1') // Strip double asterisks
        .replace(/__([^_]+)__/g, '$1')     // Strip double underscores
        .replace(/\*([^*]+)\*/g, '$1')     // Strip single asterisks
        .replace(/_([^_]+)_/g, '$1')       // Strip single underscores
        .replace(/(^|\s)\*(\s|$)/g, '$1$2') // Strip stray asterisks
        .replace(/(^|\s)#(\s|$)/g, '$1$2');  // Strip stray hashes
}

function renderMarkdown(text) {
    if (!text) return '';
    let html = text;
    
    // 1. Preserve and replace pre-formatted code block markup ```lang ... ```
    const codeBlocks = [];
    html = html.replace(/```([a-zA-Z0-9+#._-]*)\n?([\s\S]*?)```/g, (match, lang, code) => {
        const uniqueId = 'code-' + Math.random().toString(36).substr(2, 9);
        const displayLang = (lang || 'code').trim().toLowerCase();
        const highlighted = syntaxHighlight(code.trim(), displayLang);
        const codeHTML = `
            <div class="code-block-wrapper">
                <div class="code-block-header">
                    <span class="code-block-lang">${displayLang}</span>
                    <button class="code-block-copy-btn" onclick="copyCodeBlock('${uniqueId}')" data-code-id="${uniqueId}">
                        <i data-lucide="copy" style="width:12px;height:12px;margin-right:4px;"></i> Copy code
                    </button>
                </div>
                <pre><code id="${uniqueId}" class="code-highlighted">${highlighted}</code></pre>
            </div>
        `;
        codeBlocks.push(codeHTML);
        return `CBTOKENBLOCK${codeBlocks.length - 1}ENDCBTOKEN`;
    });

    // 2. Detect & format Question: & Context: prompt blocks
    html = html.replace(/(?:The LLM receives:)?\s*Question:\s*([\s\S]*?)\s*Context:\s*([\s\S]*?)(?=\n\s*(?:Then generates:|$))/gi, (match, q, c) => {
        const cleanQ = cleanMarkdownArtifacts(q.trim());
        const cleanC = cleanMarkdownArtifacts(c.trim());
        const cardText = `Question:\n${cleanQ}\n\nContext:\n${cleanC}`;
        const encodedText = escapeHTML(cardText).replace(/'/g, "\\'");
        return `
            <div class="msg-sublabel">The LLM receives:</div>
            <div class="prompt-context-card">
                <button class="card-copy-btn" onclick="copyToClipboard('${encodedText}').then(() => showToast('Copied context to clipboard!'))" title="Copy context">
                    <i data-lucide="copy" style="width:13px;height:13px;"></i>
                </button>
                <div class="card-section-label">Question:</div>
                <div class="card-section-body">${escapeHTML(cleanQ)}</div>
                <div class="card-section-label">Context:</div>
                <div class="card-section-body">${escapeHTML(cleanC)}</div>
            </div>
            <div class="msg-sublabel">Then generates:</div>
        `;
    });

    // 3. Parse Markdown Tables (| Header 1 | Header 2 |)
    html = html.replace(/((?:\|[^\n]+\|\r?\n)+)/g, (tableMatch) => {
        const lines = tableMatch.trim().split('\n').map(l => l.trim()).filter(Boolean);
        if (lines.length < 2) return tableMatch;

        const isDivider = /^\|?[\s:-]+(?:\|[\s:-]+)+\|?$/.test(lines[1]);
        const dataLines = isDivider ? [lines[0], ...lines.slice(2)] : lines;

        let tableHTML = `<div class="table-responsive-wrapper"><table class="markdown-rendered-table">`;
        dataLines.forEach((line, idx) => {
            const rawCells = line.split('|');
            const cells = rawCells.slice(1, rawCells.length - 1).map(c => c.trim());
            if (idx === 0) {
                tableHTML += `<thead><tr>${cells.map(c => `<th>${c}</th>`).join('')}</tr></thead><tbody>`;
            } else {
                tableHTML += `<tr>${cells.map(c => `<td>${c}</td>`).join('')}</tr>`;
            }
        });
        tableHTML += `</tbody></table></div>`;
        return tableHTML;
    });

    // 4. Inline code `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // 5. Convert Markdown Headings (#, ##, ###, ####)
    html = html.replace(/^####\s+(.*$)/gim, '<h4 class="msg-h4">$1</h4>');
    html = html.replace(/^###\s+(.*$)/gim, '<h3 class="msg-h3">$1</h3>');
    html = html.replace(/^##\s+(.*$)/gim, '<h2 class="msg-h2">$1</h2>');
    html = html.replace(/^#\s+(.*$)/gim, '<h1 class="msg-h1">$1</h1>');

    // 6. Convert Bold / Italics
    html = html.replace(/\*\*\*([^*]+)\*\*\*/g, '<strong><em>$1</em></strong>');
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    html = html.replace(/_([^_]+)_/g, '<em>$1</em>');

    // 7. Executive Briefing Callout / Quotes
    html = html.replace(/^(?:>\s*|\*\*Executive Briefing:\*\*|\*\*Briefing:\*\*)\s*(.*$)/gim, (m, content) => {
        return `<div class="executive-briefing-box"><div class="briefing-header"><i data-lucide="sparkles" style="width:13px;height:13px;color:#a78bfa;margin-right:6px;"></i> Executive Briefing</div><div class="briefing-content">${content}</div></div>`;
    });

    // 8. Split into paragraphs, bullet lists, and numbered lists
    const blocks = html.split('\n\n');
    html = blocks.map(p => {
        const trimmed = p.trim();
        if (trimmed.startsWith('CBTOKENBLOCK') || 
            trimmed.startsWith('<div class=') || 
            trimmed.startsWith('<table') || 
            trimmed.startsWith('<h1') || 
            trimmed.startsWith('<h2') || 
            trimmed.startsWith('<h3') || 
            trimmed.startsWith('<h4')) {
            return p;
        }
        
        // Bullet list
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            const items = trimmed.split(/\n[-*]\s+/).filter(Boolean).map(i => {
                const cleanItem = i.replace(/^[-*]\s+/, '');
                return `<li>${cleanItem}</li>`;
            }).join('');
            return `<ul class="styled-bullet-list">${items}</ul>`;
        }

        // Numbered list
        if (/^\d+\.\s+/.test(trimmed)) {
            const items = trimmed.split(/\n\d+\.\s+/).filter(Boolean).map(i => {
                const cleanItem = i.replace(/^\d+\.\s+/, '');
                return `<li>${cleanItem}</li>`;
            }).join('');
            return `<ol class="styled-numbered-list">${items}</ol>`;
        }
        
        const content = p.replace(/\n/g, '<br>');
        return `<p>${content}</p>`;
    }).join('');

    // 9. Restore Code Block Placeholders
    codeBlocks.forEach((blockHTML, idx) => {
        html = html.replace(`CBTOKENBLOCK${idx}ENDCBTOKEN`, blockHTML);
    });

    return html;
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}

// Execute Google / Web Search and render result directly in chat environment
async function executeWebSearch(rawQuery, attachments = [], tempId = null) {
    if (!rawQuery) return;
    
    // Clean query text (strip leading prefixes like '🌐 Search Google:', 'Search Web:', etc.)
    let query = rawQuery.replace(/^(🌐|🔍)?\s*(Search Google:|Search Web:)?\s*/i, '').trim();
    if (!query) query = rawQuery;

    // Verify or create an active chat if none exists
    if (!state.activeChatId) {
        try {
            const defaultTitle = 'Web Search: ' + query.substring(0, 20);
            const response = await fetch('/api/chats', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    title: defaultTitle,
                    model: state.selectedModel
                })
            });
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                showToast(errData.detail || "Failed to initialize web search session");
                return;
            }
            const newChat = await response.json();
            if (!newChat || !newChat.id) {
                showToast("Invalid chat response from server");
                return;
            }
            state.chats.unshift(newChat);
            state.activeChatId = newChat.id;
            localStorage.setItem('antigravity_rag_active_id', newChat.id);
            renderRecentChatsList();
        } catch (err) {
            console.error(err);
            showToast("Failed to connect to backend server");
            return;
        }
    }

    // Toggle viewport container display
    welcomeView.classList.add('hidden');
    messagesContainer.classList.remove('hidden');

    // Show Google Live Search status indicator in UI
    const searchBubbleId = 'search-loading-' + Date.now();
    const assistantDiv = document.createElement('div');
    assistantDiv.id = searchBubbleId;
    assistantDiv.className = 'message assistant-msg';
    assistantDiv.innerHTML = `
        <div class="message-avatar-container">
            <div class="msg-avatar assistant google-avatar" style="background:#ffffff; border:1px solid rgba(66,133,244,0.3); display:flex; align-items:center; justify-content:center; border-radius:8px;">${getGoogleGSVG(18)}</div>
        </div>
        <div class="message-content-wrapper">
            <span class="message-sender google-status-sender" style="color:#4285f4; font-weight:600; display:inline-flex; align-items:center; gap:4px;">
                ${getGoogleGSVG(13)} Google Live Search Engine
            </span>
            <div class="message-bubble google-search-loading-bubble">
                <div class="google-search-status-box">
                    <div class="google-search-status-header">
                        <div class="google-pulse-dot"></div>
                        <span id="${searchBubbleId}-status-text">Connecting to Google Search for <strong>"${escapeHTML(query)}"</strong>...</span>
                    </div>
                    <div class="google-search-loader-bar">
                        <div class="google-search-loader-progress"></div>
                    </div>
                    <div class="streaming-loader google-dots">
                        <span class="streaming-dot google-blue"></span>
                        <span class="streaming-dot google-red"></span>
                        <span class="streaming-dot google-yellow"></span>
                        <span class="streaming-dot google-green"></span>
                    </div>
                </div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(assistantDiv);
    initIcons();
    scrollToBottom();

    // Step-by-step status progress text updates
    const statusTextElem = document.getElementById(`${searchBubbleId}-status-text`);
    const timer1 = setTimeout(() => {
        if (statusTextElem) {
            statusTextElem.innerHTML = `Retrieving live web pages for <strong>"${escapeHTML(query)}"</strong>...`;
        }
    }, 700);

    const timer2 = setTimeout(() => {
        if (statusTextElem) {
            statusTextElem.innerHTML = `Synthesizing web search answer with <strong>${escapeHTML(state.selectedModel)}</strong>...`;
        }
    }, 2200);

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                model: state.selectedModel,
                chat_id: state.activeChatId
            })
        });

        clearTimeout(timer1);
        clearTimeout(timer2);

        const loadElem = document.getElementById(searchBubbleId);
        if (loadElem) loadElem.remove();

        if (response.ok) {
            const data = await response.json();
            if (tempId && data.user_message_id) {
                const userMsgDiv = document.getElementById(tempId);
                if (userMsgDiv) userMsgDiv.id = data.user_message_id;
            }
            if (data.message && data.message.text && data.message.text.length > 20) {
                renderMessageBubble(data.message);
            } else if (data.synthesis) {
                const searchMsg = {
                    sender: 'assistant',
                    text: data.synthesis.startsWith('🌐') ? data.synthesis : `🌐 **Web Search Results for:** *"${escapeHTML(query)}"* \n\n${data.synthesis}`,
                    citations: (data.results || []).map(r => ({ name: r.title, source: r.url, snippet: r.snippet, score: 1.0 })),
                    suggestions: [
                        `🌐 Search Google: ${query} latest updates`,
                        `Explain key takeaways`,
                        `Summarize key facts`
                    ]
                };
                renderMessageBubble(searchMsg);
            }
        } else {
            // Direct GET fallback if POST returned non-200
            try {
                const fallbackResp = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
                if (fallbackResp.ok) {
                    const fbData = await fallbackResp.json();
                    if (tempId && fbData.user_message_id) {
                        const userMsgDiv = document.getElementById(tempId);
                        if (userMsgDiv) userMsgDiv.id = fbData.user_message_id;
                    }
                    renderMessageBubble(fbData.message || {
                        sender: 'assistant',
                        text: fbData.synthesis || `🌐 Live web search completed for *"${escapeHTML(query)}"*.`,
                        citations: (fbData.results || []).map(r => ({ name: r.title, source: r.url, snippet: r.snippet, score: 1.0 }))
                    });
                    scrollToBottom();
                    return;
                }
            } catch (fbErr) {
                console.error("Fallback search failed:", fbErr);
            }
        }
    } catch (err) {
        console.error(err);
        const loadElem = document.getElementById(searchBubbleId);
        if (loadElem) loadElem.remove();
        try {
            const fallbackResp = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
            if (fallbackResp.ok) {
                const fbData = await fallbackResp.json();
                if (tempId && fbData.user_message_id) {
                    const userMsgDiv = document.getElementById(tempId);
                    if (userMsgDiv) userMsgDiv.id = fbData.user_message_id;
                }
                renderMessageBubble(fbData.message || {
                    sender: 'assistant',
                    text: fbData.synthesis || `🌐 Live web search completed for *"${escapeHTML(query)}"*.`,
                    citations: (fbData.results || []).map(r => ({ name: r.title, source: r.url, snippet: r.snippet, score: 1.0 }))
                });
                scrollToBottom();
                return;
            }
        } catch (e2) {}
    }
    scrollToBottom();
}

// ===== Pipeline Trace Panel Management =====

const pipelineTracePanel = document.getElementById('pipeline-trace-panel');
const pipelineTraceBody = document.getElementById('pipeline-trace-body');
const pipelineTraceSteps = document.getElementById('pipeline-trace-steps');
const pipelineTraceToggle = document.getElementById('pipeline-trace-toggle');
const pipelineTraceStatus = document.getElementById('pipeline-trace-status');
const pipelineCloseBtn = document.getElementById('pipeline-close-btn');

function showPipelinePanel() {
    if (!pipelineTracePanel) return;
    pipelineTracePanel.classList.remove('hidden');
    pipelineTracePanel.classList.add('expanded');
    updatePipelineChevron(true);
}

function hidePipelinePanel() {
    if (!pipelineTracePanel) return;
    pipelineTracePanel.classList.add('hidden');
    pipelineTracePanel.classList.remove('expanded');
}

function updatePipelineChevron(expanded) {
    const chevron = pipelineTracePanel ? pipelineTracePanel.querySelector('.pipeline-chevron-icon') : null;
    if (chevron) {
        chevron.setAttribute('data-lucide', expanded ? 'chevron-down' : 'chevron-up');
        if (window.lucide) window.lucide.createIcons();
    }
}

function setPipelineTracePlaceholder(text) {
    if (!pipelineTraceSteps) return;
    pipelineTraceSteps.innerHTML = `<div class="pipeline-placeholder">${text}</div>`;
}

function renderPipelineSteps(steps) {
    if (!pipelineTraceSteps || !steps) return;
    const statusIcon = {
        done: '<i data-lucide="check-circle" style="width:13px;height:13px;color:#10b981;flex-shrink:0;"></i>',
        running: '<i data-lucide="loader" style="width:13px;height:13px;color:#a78bfa;flex-shrink:0;animation:spin 1s linear infinite;"></i>',
        error: '<i data-lucide="alert-circle" style="width:13px;height:13px;color:#ef4444;flex-shrink:0;"></i>',
        skipped: '<i data-lucide="minus-circle" style="width:13px;height:13px;color:#64748b;flex-shrink:0;"></i>'
    };
    
    pipelineTraceSteps.innerHTML = steps.map((s, i) => {
        let rawLabel = cleanMarkdownArtifacts(s.label || '');
        if (s.step && !rawLabel.toLowerCase().startsWith('step')) {
            rawLabel = `Step ${s.step}: ${rawLabel}`;
        }
        
        let detailHTML = '';
        const detailStr = s.detail || '';
        
        if (detailStr.includes('Question:') && detailStr.includes('Context:')) {
            const qMatch = detailStr.match(/Question:\s*([\s\S]*?)\s*Context:\s*([\s\S]*?)$/i);
            if (qMatch) {
                const qText = cleanMarkdownArtifacts(qMatch[1].trim());
                const cText = cleanMarkdownArtifacts(qMatch[2].trim());
                const cardContent = `Question:\n${qText}\n\nContext:\n${cText}`;
                const encodedCard = escapeHTML(cardContent).replace(/'/g, "\\'");
                detailHTML = `
                    <div class="msg-sublabel" style="font-size:12px;margin:6px 0 4px 0;">The LLM receives:</div>
                    <div class="prompt-context-card" style="margin:6px 0;padding:12px 14px;">
                        <button class="card-copy-btn" onclick="copyToClipboard('${encodedCard}').then(() => showToast('Copied context to clipboard!'))" title="Copy context" style="top:8px;right:8px;">
                            <i data-lucide="copy" style="width:12px;height:12px;"></i>
                        </button>
                        <div class="card-section-label" style="font-size:11px;">Question:</div>
                        <div class="card-section-body" style="font-size:12px;margin-bottom:8px;">${escapeHTML(qText)}</div>
                        <div class="card-section-label" style="font-size:11px;">Context:</div>
                        <div class="card-section-body" style="font-size:12px;">${escapeHTML(cText)}</div>
                    </div>
                    <div class="msg-sublabel" style="font-size:12px;margin:6px 0 4px 0;">Then generates:</div>
                `;
            } else {
                detailHTML = escapeHTML(cleanMarkdownArtifacts(detailStr));
            }
        } else {
            detailHTML = escapeHTML(cleanMarkdownArtifacts(detailStr));
        }

        return `
            <div class="pipeline-step pipeline-step-${s.status || 'done'}">
                <div class="pipeline-step-connector ${i === 0 ? 'first' : ''}"></div>
                <div class="pipeline-step-icon">${statusIcon[s.status] || statusIcon.done}</div>
                <div class="pipeline-step-content">
                    <div class="pipeline-step-label">${escapeHTML(rawLabel)}</div>
                    <div class="pipeline-step-detail">${detailHTML}</div>
                </div>
            </div>
        `;
    }).join('');
    if (window.lucide) window.lucide.createIcons();
}

// Toggle pipeline expand/collapse via header click
if (pipelineTraceToggle) {
    pipelineTraceToggle.addEventListener('click', (e) => {
        if (pipelineCloseBtn && pipelineCloseBtn.contains(e.target)) return;
        const isExpanded = pipelineTracePanel.classList.toggle('expanded');
        updatePipelineChevron(isExpanded);
    });
}

// Close pipeline panel via X button
if (pipelineCloseBtn) {
    pipelineCloseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        hidePipelinePanel();
    });
}

// Close pipeline panel when clicking anywhere outside it (same as left/right side panes)
document.addEventListener('click', (e) => {
    if (pipelineTracePanel && 
        !pipelineTracePanel.classList.contains('hidden') &&
        !pipelineTracePanel.contains(e.target) &&
        // Don't close if clicking send button or prompt area (they trigger the panel)
        !sendBtn.contains(e.target) &&
        !promptTextarea.contains(e.target)) {
        hidePipelinePanel();
    }
});

// Send Message execution
async function sendMessage() {
    const text = promptTextarea.value.trim();
    const attachments = [...state.stagedFiles];

    if (text.length === 0 && attachments.length === 0) return;

    // Reset attachments & Textarea UI
    state.stagedFiles = [];
    renderStagedFiles();
    promptTextarea.value = '';
    autoGrowTextarea();
    toggleSendButton();

    // Route to Web Search directly if searchMode is 'web'
    if (state.searchMode === 'web') {
        welcomeView.classList.add('hidden');
        messagesContainer.classList.remove('hidden');
        const tempId = 'temp-user-' + Date.now();
        renderMessageBubble({ sender: 'user', text: text, attachments: attachments, id: tempId });
        scrollToBottom();
        await executeWebSearch(text, attachments, tempId);
        return;
    }

    // Verify or create an active chat if none exists
    if (!state.activeChatId) {
        try {
            const defaultTitle = text.length > 0 ? (text.substring(0, 24) + (text.length > 24 ? '...' : '')) : 'Untitled Chat';
            const response = await fetch('/api/chats', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    title: defaultTitle,
                    model: state.selectedModel
                })
            });
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                showToast(errData.detail || "Failed to initialize conversation session");
                return;
            }
            const newChat = await response.json();
            if (!newChat || !newChat.id) {
                showToast("Invalid server response when creating chat");
                return;
            }
            state.chats.unshift(newChat);
            state.activeChatId = newChat.id;
            localStorage.setItem('antigravity_rag_active_id', newChat.id);
            renderRecentChatsList();
        } catch (err) {
            console.error(err);
            showToast("Failed to connect to backend server");
            return;
        }
    }

    const chat = state.chats.find(c => c.id === state.activeChatId);
    if (!chat) return;

    // Auto-update default title from first query
    if (chat.title === 'Untitled Chat' && text.length > 0) {
        chat.title = text.substring(0, 24) + (text.length > 24 ? '...' : '');
        await renameChat(chat.id, chat.title);
    }

    // Prepare message payload
    const userMsg = {
        sender: 'user',
        text: text,
        attachments: attachments
    };

    // Toggle viewport container display
    welcomeView.classList.add('hidden');
    messagesContainer.classList.remove('hidden');

    // Render User message immediately on UI
    const userMsgElem = renderMessageBubble({ ...userMsg, id: 'temp-user-id' });
    if (userMsgElem) {
        userMsgElem.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Append loading spinner streaming bubble for Assistant response
    const assistantBubbleId = 'assistant-loading-' + Date.now();
    const assistantDiv = document.createElement('div');
    assistantDiv.id = assistantBubbleId;
    assistantDiv.className = 'message assistant-msg';
    assistantDiv.innerHTML = `
        <div class="message-avatar-container">
            <div class="msg-avatar assistant">AI</div>
        </div>
        <div class="message-content-wrapper">
            <span class="message-sender">Thinking</span>
            <div class="message-bubble">
                <div class="streaming-loader">
                    <span class="streaming-dot"></span>
                    <span class="streaming-dot"></span>
                    <span class="streaming-dot"></span>
                </div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(assistantDiv);

    // Show pipeline trace panel in loading state
    showPipelinePanel();
    if (pipelineTraceStatus) pipelineTraceStatus.textContent = 'Processing...';
    setPipelineTracePlaceholder('<i data-lucide="loader" style="width:12px;height:12px;vertical-align:middle;margin-right:6px;animation:spin 1s linear infinite;"></i> Running pipeline...');
    if (window.lucide) window.lucide.createIcons();

    // Set AbortController and configure send button in stop-mode
    activeAbortController = new AbortController();
    sendBtn.disabled = false;
    sendBtn.classList.add('stop-mode');
    sendBtn.innerHTML = '<i data-lucide="square" style="width:16px;height:16px;"></i>';
    sendBtn.title = "Stop generating";
    initIcons();

    // Trigger API call against the backend Coordinator
    try {
        const response = await fetch(`/api/chats/${state.activeChatId}/messages`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            signal: activeAbortController.signal,
            body: JSON.stringify({
                text: text,
                attachments: attachments,
                model: state.selectedModel,
                settings: state.ragSettings,
                system_prompt: localStorage.getItem('rag_system_prompt')
            })
        });
        
        const loadElem = document.getElementById(assistantBubbleId);
        if (loadElem) loadElem.remove();

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            const errDetail = errData.detail || errData.message || `Server Error (${response.status})`;
            renderMessageBubble({
                sender: 'assistant',
                text: `⚠️ **Failed to receive model response**\n\n*Details:* ${errDetail}\n\nPlease check if your selected model (${state.selectedModel}) is available or if backend services are running.`,
                citations: []
            });
            showToast(`Error: ${errDetail}`);
            return;
        }

        const assistantMsg = await response.json();
        
        const userMsgDiv = document.getElementById('temp-user-id');
        if (userMsgDiv && assistantMsg.user_message_id) {
            userMsgDiv.id = assistantMsg.user_message_id;
        }

        renderMessageBubble(assistantMsg);
        updatePerformanceSidebarStats();

        // Populate pipeline trace panel with actual steps from backend
        if (assistantMsg.pipeline_trace && assistantMsg.pipeline_trace.length > 0) {
            renderPipelineSteps(assistantMsg.pipeline_trace);
            if (pipelineTraceStatus) pipelineTraceStatus.textContent = `${assistantMsg.pipeline_trace.length} steps`;
        } else {
            setPipelineTracePlaceholder('No pipeline trace available for this response.');
            if (pipelineTraceStatus) pipelineTraceStatus.textContent = '';
        }
    } catch (e) {
        const loadElem = document.getElementById(assistantBubbleId);
        if (loadElem) loadElem.remove();

        if (e.name === 'AbortError') {
            console.log("Generation aborted by user.");
            renderMessageBubble({
                sender: 'assistant',
                text: "*(Generation stopped by user)*",
                citations: []
            });
        } else {
            console.error(e);
            renderMessageBubble({
                sender: 'assistant',
                text: `⚠️ **Network / System Error**\n\n${e.message || 'Could not connect to AI backend server.'}`,
                citations: []
            });
            showToast("Failed to receive model response.");
        }
    } finally {
        activeAbortController = null;
        sendBtn.classList.remove('stop-mode');
        sendBtn.innerHTML = '<i data-lucide="arrow-up"></i>';
        sendBtn.title = "Send message";
        toggleSendButton();
        initIcons();
    }
}

// Lightbox modal popup builder for images
function openLightbox(dataUrl, name) {
    const overlay = document.createElement('div');
    overlay.className = 'image-lightbox-overlay';
    overlay.innerHTML = `
        <div class="lightbox-content">
            <img src="${dataUrl}" alt="${name}" />
            <div class="lightbox-caption">${name}</div>
            <button class="lightbox-close"><i data-lucide="x"></i></button>
        </div>
    `;
    document.body.appendChild(overlay);
    initIcons();
    
    overlay.querySelector('.lightbox-close').addEventListener('click', () => overlay.remove());
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay || e.target.closest('.lightbox-close')) {
            overlay.remove();
        }
    });
}

// Fetch performance stats from endpoint and update sidebar elements dynamically
async function updatePerformanceSidebarStats() {
    try {
        const response = await fetch('/api/performance/stats');
        if (response.ok) {
            const data = await response.json();
            
            const perfLatency = document.getElementById('perf-latency');
            const perfRelevance = document.getElementById('perf-relevance');
            const perfFaithfulness = document.getElementById('perf-faithfulness');
            const perfCorrectness = document.getElementById('perf-correctness');
            const perfCost = document.getElementById('perf-cost');
            
            if (data.current && perfLatency && perfRelevance && perfFaithfulness && perfCorrectness && perfCost) {
                const latency = Math.round(data.current.latency_ms || 0);
                const relevance = Math.round((data.current.context_relevance ?? 0) * 100);
                const faithfulness = Math.round((data.current.faithfulness ?? 0) * 100);
                const correctness = Math.round((data.current.answer_relevance ?? 0) * 100);
                
                // Estimate token cost accurately based on model provider
                let costStr = "$0.0000 (Local)";
                const selModel = (state.selectedModel || '').toLowerCase();
                if (selModel.includes('gpt-4o')) {
                    costStr = "$0.0025 (Est.)";
                } else if (selModel.includes('claude')) {
                    costStr = "$0.0030 (Est.)";
                } else if (selModel.includes('gemini')) {
                    costStr = "$0.0001 (Est.)";
                } else if (selModel.includes('groq')) {
                    costStr = "$0.0005 (Est.)";
                } else if (selModel.includes('grok')) {
                    costStr = "$0.0020 (Est.)";
                }
                
                perfLatency.textContent = `${latency} ms`;
                perfRelevance.textContent = `${relevance} %`;
                perfFaithfulness.textContent = `${faithfulness} %`;
                perfCorrectness.textContent = `${correctness} %`;
                perfCost.textContent = costStr;
                
                colorifyMetricText(perfRelevance, relevance);
                colorifyMetricText(perfFaithfulness, faithfulness);
                colorifyMetricText(perfCorrectness, correctness);
            }
        }
    } catch (err) {
        console.error("Failed to update RAG performance sidebar: ", err);
    }
}

function colorifyMetricText(element, value) {
    element.className = 'perf-metric-val';
    if (value >= 80) {
        element.classList.add('text-green');
    } else if (value >= 60) {
        element.classList.add('text-amber');
    } else {
        element.classList.add('text-red');
    }
}

// Floating selection handler for Quote-Reply
let floatingTooltip = null;

function handleTextSelection(e) {
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();
    
    // Remove existing floating tooltip
    if (floatingTooltip) {
        floatingTooltip.remove();
        floatingTooltip = null;
    }
    
    if (selectedText.length === 0) return;
    
    try {
        const range = selection.getRangeAt(0);
        const container = range.commonAncestorContainer;
        const bubbleElement = container.nodeType === 3 ? container.parentNode.closest('.message-bubble') : container.closest('.message-bubble');
        
        if (!bubbleElement || !bubbleElement.closest('.assistant-msg')) return;
        
        const rect = range.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;
        
        floatingTooltip = document.createElement('div');
        floatingTooltip.className = 'selection-tooltip-btn';
        floatingTooltip.innerHTML = `<i data-lucide="corner-up-left" style="width:12px;height:12px;margin-right:4px;"></i> Quote Reply`;
        document.body.appendChild(floatingTooltip);
        initIcons();
        
        floatingTooltip.style.position = 'fixed';
        floatingTooltip.style.left = `${rect.left + (rect.width / 2) - 45}px`;
        floatingTooltip.style.top = `${rect.top - 36}px`;
        floatingTooltip.style.zIndex = '99999';
        
        floatingTooltip.addEventListener('mousedown', (ev) => {
            ev.preventDefault();
            ev.stopPropagation();
            const formattedQuote = `> "${selectedText}"\n\n`;
            promptTextarea.value = formattedQuote + promptTextarea.value;
            promptTextarea.focus();
            autoGrowTextarea();
            toggleSendButton();
            
            selection.removeAllRanges();
            if (floatingTooltip) {
                floatingTooltip.remove();
                floatingTooltip = null;
            }
        });
    } catch (err) {
        // Safe catch for Range API errors
    }
}

document.addEventListener('mouseup', handleTextSelection);
document.addEventListener('selectionchange', handleTextSelection);

// Global Platform Navigation Handler
window.handleNavRoute = async function(route) {
    const navItems = document.querySelectorAll('.nav-item');
    const chatViewport = document.getElementById('chat-viewport');
    const platformViewport = document.getElementById('platform-viewport');
    const chatFooter = document.querySelector('.chat-footer');

    navItems.forEach(i => {
        i.classList.remove('active');
        const span = i.querySelector('span');
        if (span) span.style.color = 'var(--text-secondary, #94a3b8)';
    });

    const activeItem = document.querySelector(`.nav-item[data-nav-route="${route}"]`);
    if (activeItem) {
        activeItem.classList.add('active');
        const activeSpan = activeItem.querySelector('span');
        if (activeSpan) activeSpan.style.color = 'var(--text-primary, #fff)';
    }

    if (route === 'assistant') {
        if (chatViewport) chatViewport.classList.remove('hidden');
        if (chatFooter) chatFooter.classList.remove('hidden');
        if (platformViewport) platformViewport.classList.add('hidden');
    } else {
        if (chatViewport) chatViewport.classList.add('hidden');
        if (chatFooter) chatFooter.classList.add('hidden');
        if (platformViewport) {
            platformViewport.classList.remove('hidden');
            platformViewport.innerHTML = '<div style="padding: 2rem; color: var(--text-muted); font-size: 14px;">Loading platform module...</div>';

            try {
                let renderFn;
                if (route === 'dashboard') renderFn = window.renderDashboardPage;
                else if (route === 'catalog') renderFn = window.renderCatalogPage;
                else if (route === 'upload') renderFn = window.renderUploadCenterPage;
                else if (route === 'reviews') renderFn = window.renderReviewsPage;
                else if (route === 'evaluation') renderFn = window.renderEvaluationPage;
                else if (route === 'recommendations') renderFn = window.renderRecommendationsPage;
                else if (route === 'analytics') renderFn = window.renderAnalyticsPage;
                else if (route === 'users') renderFn = window.renderUsersPage;
                else if (route === 'health') renderFn = window.renderHealthPage;
                else if (route === 'audit') renderFn = window.renderAuditPage;
                else if (route === 'sql') renderFn = window.renderSQLEditorPage;

                if (renderFn) {
                    platformViewport.innerHTML = '';
                    const pageEl = await renderFn({ userRole: 'Super Admin' }, window.handleNavRoute);
                    platformViewport.appendChild(pageEl);
                    if (window.lucide) window.lucide.createIcons();
                } else {
                    platformViewport.innerHTML = `<div style="padding: 2rem; color: var(--status-danger);">View module [${route}] not found.</div>`;
                }
            } catch (err) {
                console.error('Failed to render view:', err);
                platformViewport.innerHTML = `<div style="padding: 2rem; color: var(--status-danger);">Error rendering view: ${err.message}</div>`;
            }
        }
    }
};

// ===== Chat History & Retrieval Analytics Viewport =====
const topHistoryBtn = document.getElementById('top-history-btn');
const backToRagBtn = document.getElementById('back-to-rag-btn');
const historyViewport = document.getElementById('history-viewport');
const historyTableBody = document.getElementById('history-table-body');
const historySearchInput = document.getElementById('history-search-input');
const historyRecordCount = document.getElementById('history-record-count');
const clearHistoryBtn = document.getElementById('clear-history-btn');

let allHistoryRecords = [];

async function loadHistoryAnalyticsView() {
    const chatViewport = document.getElementById('chat-viewport');
    const platformViewport = document.getElementById('platform-viewport');
    const chatFooter = document.querySelector('.chat-footer');

    if (chatViewport) chatViewport.classList.add('hidden');
    if (chatFooter) chatFooter.classList.add('hidden');
    if (platformViewport) platformViewport.classList.add('hidden');
    if (historyViewport) historyViewport.classList.remove('hidden');

    try {
        const response = await fetch('/api/history');
        if (response.ok) {
            allHistoryRecords = await response.json();
            renderHistoryTableRows(allHistoryRecords);
        } else {
            if (historyTableBody) {
                historyTableBody.innerHTML = `<tr><td colspan="12" style="text-align:center;padding:24px;color:var(--text-muted);">Failed to load history records.</td></tr>`;
            }
        }
    } catch (err) {
        console.error("Error loading chat history records:", err);
        if (historyTableBody) {
            historyTableBody.innerHTML = `<tr><td colspan="12" style="text-align:center;padding:24px;color:var(--text-muted);">Error connecting to history database.</td></tr>`;
        }
    }
}

function closeHistoryAnalyticsView() {
    const chatViewport = document.getElementById('chat-viewport');
    const chatFooter = document.querySelector('.chat-footer');

    if (historyViewport) historyViewport.classList.add('hidden');
    if (chatViewport) chatViewport.classList.remove('hidden');
    if (chatFooter) chatFooter.classList.remove('hidden');
    if (topHistoryBtn) topHistoryBtn.classList.remove('active');
}

function renderHistoryTableRows(records) {
    if (!historyTableBody) return;
    historyTableBody.innerHTML = '';

    if (!records || records.length === 0) {
        historyTableBody.innerHTML = `<tr><td colspan="12" style="text-align:center;padding:32px;color:var(--text-muted);font-size:13px;">No history records stored yet. Send a message in the RAG App to populate detailed relational records!</td></tr>`;
        if (historyRecordCount) historyRecordCount.textContent = '0 Records';
        return;
    }

    if (historyRecordCount) historyRecordCount.textContent = `${records.length} Record${records.length === 1 ? '' : 's'}`;

    records.forEach(r => {
        const tr = document.createElement('tr');
        const m = r.response_metrics || {};

        function badgeColor(val) {
            if (val >= 80) return 'color:#10b981;background:rgba(16,185,129,0.1);';
            if (val >= 60) return 'color:#f59e0b;background:rgba(245,158,11,0.1);';
            return 'color:#ef4444;background:rgba(239,68,68,0.1);';
        }

        const metricsHTML = `
            <div class="cell-metrics-badge">
                <span class="metric-pill" style="${badgeColor(m.correctness ?? 0)}" title="Correctness">C:${m.correctness ?? 0}%</span>
                <span class="metric-pill" style="${badgeColor(m.faithfulness ?? 0)}" title="Faithfulness">F:${m.faithfulness ?? 0}%</span>
                <span class="metric-pill" style="${badgeColor(m.groundedness ?? 0)}" title="Groundedness">G:${m.groundedness ?? 0}%</span>
                <span class="metric-pill" style="${badgeColor(m.confidence ?? 0)}" title="Confidence">Conf:${m.confidence ?? 0}%</span>
            </div>
        `;

        let sourceClass = 'source-llm';
        const src = (r.search_source || '').toLowerCase();
        if (src.includes('vector')) sourceClass = 'source-vector';
        else if (src.includes('google') || src.includes('web')) sourceClass = 'source-web';
        else if (src.includes('attachment')) sourceClass = 'source-attach';

        const simScoreVal = (typeof r.similarity_score === 'number') ? r.similarity_score.toFixed(4) : (r.similarity_score || null);

        tr.innerHTML = `
            <td><span class="cell-id">${escapeHTML(r.id || 'NULL')}</span></td>
            <td><span class="cell-timestamp">${escapeHTML(r.timestamp_ist || 'NULL')}</span></td>
            <td><div class="cell-prompt" title="${escapeHTML(r.user_prompt || '')}">${escapeHTML(r.user_prompt || 'NULL')}</div></td>
            <td><div class="cell-response" title="${escapeHTML(r.retrieved_response || '')}">${escapeHTML(r.retrieved_response || 'NULL')}</div></td>
            <td>${metricsHTML}</td>
            <td style="font-family:var(--font-mono);font-size:12px;">${r.timetaken_s !== null ? `${r.timetaken_s}s` : '<span class="cell-null">NULL</span>'}</td>
            <td style="font-family:var(--font-mono);font-size:12px;">${simScoreVal !== null ? simScoreVal : '<span class="cell-null">NULL</span>'}</td>
            <td><span style="color:#a78bfa;font-size:11.5px;font-weight:600;">${escapeHTML(r.llm_model || 'NULL')}</span></td>
            <td>${r.memory_source ? `<span style="font-size:11.5px;">${escapeHTML(r.memory_source)}</span>` : '<span class="cell-null">NULL</span>'}</td>
            <td>${r.files_used ? `<span style="font-size:11.5px;color:#60a5fa;">${escapeHTML(r.files_used)}</span>` : '<span class="cell-null">NULL</span>'}</td>
            <td>${r.chunks_used ? `<span style="font-size:11px;font-family:var(--font-mono);">${escapeHTML(r.chunks_used)}</span>` : '<span class="cell-null">NULL</span>'}</td>
            <td>${r.chunk_metadata ? `<span style="font-size:11px;font-family:var(--font-mono);color:#94a3b8;">${escapeHTML(r.chunk_metadata)}</span>` : '<span class="cell-null">NULL</span>'}</td>
            <td><span class="source-badge ${sourceClass}">${escapeHTML(r.search_source || 'NULL')}</span></td>
        `;
        historyTableBody.appendChild(tr);
    });

    if (window.lucide) window.lucide.createIcons();
}

if (topHistoryBtn) {
    topHistoryBtn.addEventListener('click', () => {
        if (historyViewport && !historyViewport.classList.contains('hidden')) {
            closeHistoryAnalyticsView();
        } else {
            loadHistoryAnalyticsView();
            topHistoryBtn.classList.add('active');
        }
    });
}

if (backToRagBtn) {
    backToRagBtn.addEventListener('click', () => {
        closeHistoryAnalyticsView();
    });
}

if (historySearchInput) {
    historySearchInput.addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase().trim();
        if (!q) {
            renderHistoryTableRows(allHistoryRecords);
            return;
        }
        const filtered = allHistoryRecords.filter(r => 
            (r.user_prompt || '').toLowerCase().includes(q) ||
            (r.retrieved_response || '').toLowerCase().includes(q) ||
            (r.llm_model || '').toLowerCase().includes(q) ||
            (r.files_used || '').toLowerCase().includes(q) ||
            (r.search_source || '').toLowerCase().includes(q) ||
            (r.timestamp_ist || '').toLowerCase().includes(q) ||
            (r.id || '').toLowerCase().includes(q)
        );
        renderHistoryTableRows(filtered);
    });
}

if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener('click', async () => {
        if (!confirm("Are you sure you want to clear all chat history records?")) return;
        try {
            const resp = await fetch('/api/history', { method: 'DELETE' });
            if (resp.ok) {
                allHistoryRecords = [];
                renderHistoryTableRows([]);
                showToast("Cleared all history records");
            }
        } catch (err) {
            console.error("Error clearing history records:", err);
        }
    });
}
