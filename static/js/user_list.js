// ------------------------
// Open chat
// ------------------------
function openChat(userId) {
    window.location.href = "/chat/" + userId + "/";
}

// ------------------------
// Connect to NotificationConsumer WebSocket
// ------------------------
const notifSocket = new WebSocket(`ws://${window.location.host}/ws/notifications/`);

notifSocket.onopen = () => console.log("Notification socket connected");

notifSocket.onmessage = (e) => {
    const data = JSON.parse(e.data);

    // Update unread counts
    if (data.type === "unread_counts") {
        Object.entries(data.counts).forEach(([userId, count]) => {
            const li = document.getElementById(`user-${userId}`);
            if (li) {
                const badge = li.querySelector(".unread-badge");
                badge.style.display = count > 0 ? "inline-block" : "none";
                badge.innerText = count;
            }
        });
    }

    if (data.type === "unread_update") {
        const userId = data.user_id;
        const count = data.count;
        const li = document.getElementById(`user-${userId}`);
        if (li) {
            const badge = li.querySelector(".unread-badge");
            badge.style.display = count > 0 ? "inline-block" : "none";
            badge.innerText = count;
        }
    }

    // Update online/offline status
    if (data.type === "user_status") {
        const userId = data.user_id;
        const li = document.getElementById(`user-${userId}`);
        if (li) {
            const statusText = li.querySelector(".status-text");
            if (statusText) {
                statusText.innerText = data.is_online ? "🟢 Online" : "⚫ Offline";
            }
        }
    }
};

notifSocket.onclose = () => console.log("Notification socket closed");

// ------------------------
// Logout with WebSocket notification
// ------------------------
const logoutBtn = document.getElementById("logout-btn");
const logoutForm = document.getElementById("logout-form");

logoutBtn.addEventListener("click", function(e){
    e.preventDefault(); // prevent immediate form submit

    if (notifSocket.readyState === WebSocket.OPEN) {
        // Tell server user is logging out
        notifSocket.send(JSON.stringify({ type: "user_logout" }));
    }

    // Small delay to ensure WebSocket message is sent
    setTimeout(() => logoutForm.submit(), 100);
});