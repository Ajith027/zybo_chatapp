// ------------------------
// Variables
// ------------------------
const container = document.getElementById("chat-container");
const otherUserId = container.dataset.otherUserId;
const selfUserId = Number(container.dataset.selfUserId);
const selfUser = container.dataset.selfUsername;

const chatBox = document.getElementById("chat-box");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const typingIndicator = document.getElementById("typing-indicator");

// Store messages by ID
const messagesMap = {};

// ------------------------
// Map already rendered messages
// ------------------------
document.querySelectorAll("#chat-box .message").forEach(div => {
    const msgId = div.dataset.msgId;
    if (msgId) messagesMap[msgId] = div;

    if (div.classList.contains("you")) {
        const btn = div.querySelector(".delete-btn");
        if (btn) {
            btn.onclick = () => {
                chatSocket.send(JSON.stringify({
                    type: "delete_message",
                    message_id: msgId
                }));
            };
        }
    }
});

// ------------------------
// WebSocket connection
// ------------------------
let wsReady = false;
const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
const chatSocket = new WebSocket(
    `${protocol}${window.location.host}/ws/chat/${otherUserId}/`
);

chatSocket.onopen = () => {
    wsReady = true;
    chatSocket.send(JSON.stringify({ type: "chat_open" }));
};

chatSocket.onmessage = (e) => {
    const data = JSON.parse(e.data);

    if (data.type === "chat_message") {
        const isYou = data.sender === selfUser;
        addMessage(
            data.message_id,
            data.sender,
            data.message,
            isYou,
            new Date().toLocaleString(),
            data.is_read
        );
    } 
    else if (data.type === "read_receipt") {
        markAsRead(data.message_id);
    }
    else if (data.type === "message_deleted") {
        const msgDiv = messagesMap[data.message_id];
        if (msgDiv) {
            msgDiv.remove();
            delete messagesMap[data.message_id];
        }
    }
    else if (data.type === "typing" && data.user_id != selfUserId) {
        typingIndicator.style.display = data.is_typing ? "block" : "none";
    }
};

// ------------------------
// Functions
// ------------------------
function addMessage(id, sender, content, isYou, timestamp, isRead=false) {
    if (messagesMap[id]) return;

    const msgDiv = document.createElement("div");
    msgDiv.className = "message " + (isYou ? "you" : "other");
    msgDiv.dataset.msgId = id;

    let tick = "";
    if (isYou) tick = isRead ? "✅✅ <span style='color:blue'>seen</span>" : "✅";
    let deleteBtn = isYou ? `<button class="delete-btn" data-id="${id}">🗑️</button>` : "";

    msgDiv.innerHTML = `
        <strong>${sender}:</strong> ${content} ${deleteBtn}<br>
        <small>${timestamp} ${tick}</small>
    `;

    chatBox.appendChild(msgDiv);

    // 🔥 Auto-scroll when new message is added
    chatBox.scrollTop = chatBox.scrollHeight;

    messagesMap[id] = msgDiv;

    if (isYou) {
        const btn = msgDiv.querySelector(".delete-btn");
        if (btn) {
            btn.onclick = () => chatSocket.send(
                JSON.stringify({ type:"delete_message", message_id:id })
            );
        }
    }
}

function markAsRead(messageId) {
    const msgDiv = messagesMap[messageId];
    if (msgDiv) {
        const small = msgDiv.querySelector("small");
        if (small) {
            small.innerHTML = small.innerHTML.replace(
                /✅+/,
                "✅✅ <span style='color:blue'>seen</span>"
            );
        }
    }
}

// ------------------------
// Send new message
// ------------------------
sendBtn.onclick = () => {
    const message = input.value.trim();
    if (!message) return;

    if (wsReady) {
        chatSocket.send(JSON.stringify({
            type:"chat_message",
            message:message
        }));
        input.value = "";
    }
};

// ------------------------
// Typing indicator
// ------------------------
let typingTimeout;
input.addEventListener("input", () => {
    if (!wsReady) return;

    chatSocket.send(JSON.stringify({ type:"typing", is_typing:true }));

    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        chatSocket.send(JSON.stringify({ type:"typing", is_typing:false }));
    }, 1000);
});

// ------------------------
// Notify server when leaving chat
// ------------------------
window.addEventListener("beforeunload", () => {
    if (wsReady) {
        chatSocket.send(JSON.stringify({ type:"chat_close" }));
    }
});

// ------------------------
// Auto-scroll when page loads
// ------------------------
document.addEventListener("DOMContentLoaded", function () {
    if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});