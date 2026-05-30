document.getElementById("deleteBtnConfirm").addEventListener("click", async () => {
    const res = await fetch("/delete_chat", { method: "DELETE" });
    if (res.ok) {
        location.reload();
    }
});

// function deleteChat() {
//     document.querySelector('.chat_and_delete').style.display = 'none';
//     document.getElementById('my-chat-item').style.display = 'none';
//     document.getElementById('my-chat-hr').style.display = 'none';
//     document.getElementById('div-create-chat').style.display = 'block';
// }