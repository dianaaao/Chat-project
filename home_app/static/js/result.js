window.addEventListener("DOMContentLoaded", async () => {
    const result = await fetch("/my_chat");
    const data = await result.json();

    if (data.id) {
        document.getElementById("my-chat-item").style.display = "flex";
        document.getElementById("my-chat-name").textContent = data.name;
        document.querySelector(".chat_and_delete").style.display = "flex";
        document.getElementById("my-chat-hr").style.display = "block"
        document.getElementById("my-chat-avatar").textContent = data.name[0].toUpperCase(); 
        document.getElementById("div-create-chat").style.display = "none";
    }

});