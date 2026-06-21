document.getElementById("deleteBtnConfirm").addEventListener("click", async () => {
    const res = await fetch("/delete_chat", { method: "DELETE" });
    if (res.ok) {
        const myChatId = document.getElementById('my-chat-item').dataset.groupId

        // ховаємо власний чат і показуємо кнопку створення без перезавантаження
        document.querySelector('.chat_and_delete').style.display = 'none'
        document.getElementById('my-chat-item').style.display = 'none'
        document.getElementById('my-chat-hr').style.display = 'none'
        document.getElementById('div-create-chat').style.display = 'block'

        // видаляємо чат зі списку всіх чатів якщо він там показаний
        const chatItem = document.querySelector(`.chat-item2[data-group-id="${myChatId}"]`)
        if (chatItem) chatItem.remove()

        document.getElementById('deleteModalOverlay').style.display = 'none'
    }
});

// function deleteChat() {
//     document.querySelector('.chat_and_delete').style.display = 'none';
//     document.getElementById('my-chat-item').style.display = 'none';
//     document.getElementById('my-chat-hr').style.display = 'none';
//     document.getElementById('div-create-chat').style.display = 'block';
// }