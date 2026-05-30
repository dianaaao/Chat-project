// Відкрити модалку видалення
document.getElementById('delete-btn').addEventListener('click', () => {
    document.getElementById('deleteModalOverlay').style.display = 'flex';
});

// Закрити модалку видалення
function closeDeleteModal() {
    document.getElementById('deleteModalOverlay').style.display = 'none';
}

document.getElementById('deleteModalClose').addEventListener('click', closeDeleteModal);
document.getElementById('deleteBtnCancel').addEventListener('click', closeDeleteModal);

// Підтвердження видалення
document.getElementById('deleteBtnConfirm').addEventListener('click', () => {
    document.querySelector('.chat_and_delete').style.display = 'none';
    document.getElementById('my-chat-item').style.display = 'none';
    document.getElementById('my-chat-hr').style.display = 'none';
    document.getElementById('div-create-chat').style.display = 'block';
    closeDeleteModal();
});