function openCreateModal() {
    document.getElementById('modalOverlay').style.display = "flex";
    document.getElementById('chatNameInput').value = "";
    document.getElementById('chatNameInput').focus();
    
}

function closeCreateModal() {
    document.getElementById('modalOverlay').style.display = "none";

}

function submitCreateChat() {
    const name = document.getElementById('chatNameInput').value.trim();
    if (!name) return;
    
    document.getElementById('my-chat-name').textContent = name;
    document.querySelector('.chat_and_delete').style.display = "flex";
    document.getElementById('my-chat-item').style.display = "flex";
    document.getElementById('my-chat-hr').style.display = "block";
    document.getElementById('div-create-chat').style.display = "none";

    closeCreateModal();

}

document.getElementById('modalClose').addEventListener('click', closeCreateModal)
document.getElementById('btnCancel').addEventListener('click', closeCreateModal)
document.getElementById('btnCreate').addEventListener('click', submitCreateChat)
document.getElementById('chatNameInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') submitCreateChat();
    if (e.key === 'Escape') closeCreateModal();
});



