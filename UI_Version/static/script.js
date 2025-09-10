const socket = io();

const agentBox = document.getElementById("agentBox");
const localBox = document.getElementById("localBox");
const userSubtitle = document.getElementById("userSubtitle");
const agentSubtitle = document.getElementById("agentSubtitle");

const startBtn = document.getElementById("startBtn");
const endBtn = document.getElementById("endBtn");

// Start Interview
function startInterview() {
    socket.emit("start_interview", {});
    startBtn.style.display = "none";
    endBtn.style.display = "inline-block";
}

// End Turn
function endTurn() {
    socket.emit("user_end_turn", {});
}

// End Call
function endCall() {
    socket.emit("end_call", {});
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

socket.on("call_ended", (data) => {
    alert(data.text);
});
