// Підключаємось до сервера через WebSocket
const socket = io()

// id поточної відкритої кімнати — null якщо жоден чат не відкритий
let linkGroupId = null

// Спрацьовує коли з'єднання з сервером встановлено
socket.on("connect", () => {
    console.log("Ви підключились")
})

// Спрацьовує коли з'єднання з сервером розірвано
socket.on("disconnect", () => {
    console.log("Ви відключились")
})

// юзер підключився — ставимо зелену крапку
socket.on("user_status_online", (data) => {
    const status_dot = document.querySelector(`.user-item[data-user-id="${data.user_id}"] .user-status`)
    if (status_dot) {
        status_dot.classList.add("online")
    
        currentOnline++
        updateUserCount()
    }
})

// юзер відключився — прибираємо зелену крапку
socket.on("user_status_offline", (data) => {
    const status_dot = document.querySelector(`.user-item[data-user-id="${data.user_id}"] .user-status`)
    if (status_dot) {
        status_dot.classList.remove("online")

        currentOnline--
        updateUserCount()
    } 
})

function updateUserCount() {
    const all_users = document.querySelector(".count_users span").textContent = formatUsers(currentTotal)
    const online = document.querySelector(".count_users_online span").textContent = `${currentOnline} онлайн`
}
function formatUsers(count) {
    if (count % 10 === 1 && count % 100 !== 11) return `${count} користувач`
    if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) return `${count} користувача`
    return `${count} користувачів`
}
            

// Відкриває чат по кліку на контейнер чату в сайдбарі
function openChat(groupId, groupName) {
    // якщо раніше був відкритий інший чат — виходимо з його кімнати
    if (linkGroupId) {
        socket.emit("leave_room", { groupId: linkGroupId })
    }

    linkGroupId = groupId

    // показуємо хедер і поле вводу які були приховані до відкриття чату
    document.querySelector('.chat-header').style.display = 'flex'
    document.querySelector('.chat-input-area').style.display = 'flex'
    // вставляємо назву чату в заголовок
    document.querySelector('.chat-title').textContent = groupName

    // підключаємось до кімнати на сервері
    socket.emit("join_room", { groupId: linkGroupId, userId: CURRENT_USER_ID })

    // завантажуємо історію повідомлень цього чату
    fetch(`/get_messages/${groupId}`)
        .then(res => res.json())
        .then(messages => {
            const chatMessages = document.getElementById('chatMessages')
            chatMessages.innerHTML = ''  // очищаємо попередні повідомлення
            messages.forEach(msg => addMessage(msg.text, msg.author, msg.user_id, msg.time))
            chatMessages.scrollTop = chatMessages.scrollHeight  // скролимо вниз
        })

    // вішаємо події на кнопки відправки — тут вони вже є в DOM
    const sendBtn = document.querySelector('.send-btn')
    const messageInput = document.querySelector('.chat-input')

    // замінюємо кнопку на її копію щоб прибрати старі слухачі і не дублювати їх
    sendBtn.replaceWith(sendBtn.cloneNode(true))
    const newSendBtn = document.querySelector('.send-btn')
    newSendBtn.addEventListener('click', sendMessage)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendMessage()  // відправка по Enter
    })

    
    // завантажуємо список учасників чату
    fetch(`/get_members/${groupId}`)
        .then(res => res.json()) // парсимо JSON відповідь від сервера
        .then(members => {
            const res_list = document.querySelector(".users_list")
            res_list.innerHTML = '' // очищаємо попередній список

            if (!members || members.length === 0) return

            currentTotal = members[0].all_users
            currentOnline = members[0].count_online_user
            updateUserCount()

            // для кожного учасника створюємо елемент
            // members.forEach(member => {
            //     // беремо перші літери кожного слова імені для аватара
            //     // наприклад "Іван Петренко" → "ІП"
            //     const initial = member.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
            //     res_list.innerHTML += `
            //         <div class="user-item ${member.is_owner ? 'owner' : ''}" data-user-id="${member.id}">
            //             <div class="user-avatar-wrapper">
            //                 <div class="user-avatar">${initial}</div>
            //                 <span class="user-status ${member.is_online ? 'online' : ''}"></span>
            //             </div>
            //             <span class="user-name">${member.name}</span>
            //         </div>
            //     `
            // })
            members.forEach(member => {
                // беремо перші літери кожного слова імені для аватара
                // наприклад "Іван Петренко" → "ІП"
                const initial = member.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)    
                const div = document.createElement('div')
                div.className = `user-item ${member.is_owner ? 'owner' : ''}`
                div.dataset.userId = member.id
                div.onclick = () => openUserInfo(member.id)
                div.innerHTML = `
                    <div class="user-avatar-wrapper">
                        <div class="user-avatar">${initial}</div>
                        <span class="user-status ${member.is_online ? 'online' : ''}"></span>
                    </div>
                    <span class="user-name">${member.name}</span>
                `
                res_list.appendChild(div)
            })
            if (window.innerWidth <= 480) {
                switchToTab(1)
            }
        })
}

function openUserInfo(userId) {
    console.log('openUserInfo викликано', userId)
    fetch(`/get_user/${userId}`)
    .then(res => res.json()) // парсимо JSON відповідь від сервера
        .then(user => {
            console.log('user data:', user)
            const initial = user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
            document.querySelector('.info-avatar').textContent = initial
            document.querySelector('.info-name').textContent = user.name
            document.querySelector('.info-username').textContent = `@${user.email.split('@')[0]}`

            const values = document.querySelectorAll('.info-value')
            values[0].textContent = formatBirthDate(user.birth_date)
            values[1].textContent = formatGender(user.gender)

            document.querySelector('.info-user').style.display = "flex"

            if (window.innerWidth <= 480) {
                switchToTab(2)
            }
        })
}

// закрити по хрестику
document.getElementById("infoClose").addEventListener("click", () => {
    document.querySelector(".info-user").style.display = "none"

})

function formatBirthDate(dateStr) {
    if (!dateStr) return 'Не вказано'
    
    const date = new Date(dateStr)
    const today = new Date()
    
    // рахуємо вік
    let age = today.getFullYear() - date.getFullYear()
    const monthDiff = today.getMonth() - date.getMonth()
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < date.getDate())) {
        age--
    }
    
    // форматуємо дату українською
    const formatted = date.toLocaleDateString('uk-UA', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    })
    
    return `${formatted} (${age} років)`
}

function formatGender(gender) {
    if (!gender) return 'Не вказано'
    if (gender === 'male') return 'Чоловік'
    if (gender === 'female') return 'Жінка'
    return gender
}


// Спрацьовує коли сервер підтверджує підключення до кімнати
socket.on("join_room", (data) => {
    console.log(data.message)
})

// Спрацьовує коли сервер підтверджує вихід з кімнати
socket.on("leave_room", (data) => {
    console.log(data.message)
})

// Відправляє повідомлення в поточний відкритий чат
function sendMessage() {
    const messageInput = document.querySelector('.chat-input')
    const text = messageInput.value.trim()
    if (!text) return          // не відправляємо порожні повідомлення
    if (!linkGroupId) return   // не відправляємо якщо чат не відкритий

    // відправляємо подію на сервер — сервер збереже в БД і розішле всім учасникам кімнати
    socket.emit("send_message", { groupId: linkGroupId, text: text })
    messageInput.value = ""  // очищаємо поле вводу
}

// Спрацьовує коли сервер надсилає нове повідомлення всім учасникам кімнати
socket.on("new_message", (data) => {
    addMessage(data.text, data.author, data.userId, data.time)
    document.getElementById('chatMessages').scrollTop = document.getElementById('chatMessages').scrollHeight

    // оновлюємо превʼю останнього повідомлення в сайдбарі
    updateChatPreview(linkGroupId, data.text)
})

// Оновлює текст останнього повідомлення і час в елементі чату в сайдбарі
function updateChatPreview(groupId, text) {
    // шукаємо елемент чату по data-group-id атрибуту
    const item = document.querySelector(`.chat-item2[data-group-id="${groupId}"]`)
    if (!item) return
    const preview = item.querySelector('.chat-preview')
    const time = item.querySelector('.chat-time')
    if (preview) preview.textContent = text
    if (time) time.textContent = 'щойно'
}

// Створює і додає div повідомлення в контейнер чату
function addMessage(text, author, userId, time) {
    // порівнюємо як числа — userId може прийти як рядок
    const isOwn = Number(userId) === Number(CURRENT_USER_ID)
    const chatMessages = document.getElementById('chatMessages')

    // ховаємо заглушку "Виберіть чат" якщо вона ще є
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
                const chatItem = document.querySelector(`.chat-item2[data-group-id="${linkGroupId}"]`)
                if (chatItem) chatItem.remove()


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
