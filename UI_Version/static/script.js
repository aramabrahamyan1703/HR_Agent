const socket = io();

const agentBox = document.getElementById("agentBox");
const localBox = document.getElementById("localBox");
const userSubtitle = document.getElementById("userSubtitle");
const agentSubtitle = document.getElementById("agentSubtitle");

// Start Interview
function startInterview() {
    socket.emit("start_interview", {});
}

// End Turn (capture user speech)
function endTurn() {
    socket.emit("user_end_turn", {});
}

// Green border and subtitle updates
socket.on("bot_speaking", (data) => {
    agentBox.classList.add("speaking");
    agentSubtitle.textContent = data.text;
    setTimeout(() => agentBox.classList.remove("speaking"), 1500);
});

socket.on("user_speaking", (data) => {
    localBox.classList.add("speaking");
    userSubtitle.textContent = data.text;
    setTimeout(() => localBox.classList.remove("speaking"), 1500);
});
