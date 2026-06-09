const socket = io();

let linkGroupId = null

socket.on('connect', () => {
    console.log('Connected to server')
});

socket.on('disconnect', () => {
    console.log('Disconnected from server')
});

function openChat(groupId, groupName) {
    if (linkGroupId) {
        socket.emit('leave_room', { 'groupId': linkGroupId });
    }
    linkGroupId = groupId
    document.querySelector('.chat-header').style.display = "flex"
    document.querySelector('.chat-input-area').style.display = "flex"
    document.querySelector('.chat-title').textContent = groupName

    socket.emit('join_room', { 
        groupId: linkGroupId,
        userId: CURRENT_USER_ID

    });

    fetch(`/get_messages/${groupId}`)
        .then(response => response.json())
        .then(messages => {
            const chatMessages = document.getElementById('chatMessages')
            chatMessages.innerHTML = ''  // очищаємо попередні повідомлення
            messages.forEach(msg => addMessage(msg.text, msg.author, msg.user_id, msg.time))
            chatMessages.scrollTop = chatMessages.scrollHeight  // скролимо вниз
        })

    const sendButton = document.querySelector('.send-btn');
    const messageInput = document.querySelector('.chat-input');

    sendButton.replaceWith(sendButton.cloneNode(true));
    const newSendButton = document.querySelector('.send-btn');
    newSendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') sendMessage();
    });

}

socket.on('join_room', (data) => {
    console.log('Connected');
});

socket.on('leave_room', (data) => {
    console.log('Disconnected');
});

function sendMessage() {
    const messageInput = document.querySelector('.chat-input')
    const text = messageInput.value.trim()
    
    if (!text) return

    if (!linkGroupId) return

    socket.emit("send_message", {
        groupId: linkGroupId,
        text: text,
    })
    
    messageInput.value = ""
}

socket.on('new_message', (data) => {
    if (data.group_id === linkGroupId) {
        addMessage(data.text, data.author, data.user_id, data.time)
        document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight 
    }
});
        
function addMessage(text, author, userId, time) {
    const isOwn = Number(userId) === Number(CURRENT_USER_ID)
    const chatMessages = document.getElementById('chatMessages')
    const placeholder = document.querySelector('.choose-chat')
    if (placeholder) placeholder.style.display = 'none'
    const div = document.createElement('div')

    // власні повідомлення отримують додатковий клас message-own для виділення стилями
    div.className = 'message' + (isOwn ? ' message-own' : '')
    div.innerHTML = `
        <div class="avatar ${isOwn ? 'av-teal' : 'av-blue'}">${author[0].toUpperCase()}</div>
        <div class="message-body ${isOwn ? 'message-body-own' : ''}">
            <div class="message-top">
                <span class="message-author">${isOwn ? 'You' : author}</span>
                <span class="message-time">${time}</span>
            </div>
            <p class="message-text">${text}</p>
        </div>
    `
    chatMessages.appendChild(div)
    
}
// Чекаємо поки DOM повністю завантажиться перед тим як вішати події на елементи
document.addEventListener('DOMContentLoaded', () => {

    // показуємо/ховаємо міні-меню при кліку на іконку три крапки
    document.getElementById('moreInfoBtn').addEventListener('click', (e) => {
        e.stopPropagation()  // зупиняємо спливання щоб не спрацював document.click нижче
        const menu = document.getElementById('miniMenu')
        menu.style.display = menu.style.display === 'none' ? 'block' : 'none'
    })

    // закриваємо міні-меню при кліку будь-де на сторінці
    document.addEventListener('click', () => {
        document.getElementById('miniMenu').style.display = 'none'
    })

    // кнопка "Вийти" в міні-меню — закриває міні-меню і відкриває модалку підтвердження
    document.getElementById('leaveMenuBtn').addEventListener('click', () => {
        document.getElementById('miniMenu').style.display = 'none'
        document.getElementById('leaveModalOverlay').style.display = 'flex'
    })

    // закрити модалку виходу по хрестику
    document.getElementById('leaveModalClose').addEventListener('click', () => {
        document.getElementById('leaveModalOverlay').style.display = 'none'
    })

    // закрити модалку виходу по кнопці "Скасувати"
    document.getElementById('leaveBtnCancel').addEventListener('click', () => {
        document.getElementById('leaveModalOverlay').style.display = 'none'
    })

    // підтвердження виходу з чату
    document.getElementById('leaveBtnConfirm').addEventListener('click', () => {
        if (!linkGroupId) return  // якщо чат не відкритий — нічого не робимо

        // повідомляємо сервер що юзер виходить з кімнати
        socket.emit('leave_room', { groupId: linkGroupId })

        // видаляємо юзера з групи в БД через POST запит
        fetch(`/join_chat/${linkGroupId}/leave`, { method: 'POST' })
            .then(() => {
                linkGroupId = null  // скидаємо поточний чат
                document.getElementById('leaveModalOverlay').style.display = 'none'
                // ховаємо хедер і поле вводу
                document.querySelector('.chat-header').style.display = 'none'
                document.querySelector('.chat-input-area').style.display = 'none'
                document.querySelector('.chat-title').textContent = ''
                // показуємо заглушку замість повідомлень
                document.getElementById('chatMessages').innerHTML = `
                    <div class="choose-chat">
                        <p class="choose-chat-text">Виберіть чат</p>
                        <p class="choose-chat-subtext">Приєднайтеся до кімнати та почніть розмову</p>
                    </div>
                `
            })
    })

})