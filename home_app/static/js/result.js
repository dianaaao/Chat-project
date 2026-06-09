// Масив класів кольорів для аватарів — використовується щоб кожен чат мав свій колір
const avatarColors = ['av-blue', 'av-teal', 'av-green', 'av-red', 'av-gray', 'av-purple']

// Визначає колір аватара на основі назви чату
// Перебирає кожен символ назви і обчислює хеш — однакова назва завжди дає однаковий колір
function getColor(name) {
    let h = 0
    for (let c of name) h = (h * 31 + c.charCodeAt(0)) % avatarColors.length
    return avatarColors[h]
}

// Перетворює ISO дату в зручний формат "скільки часу тому"
// Наприклад: "щойно", "5m ago", "2h ago", "3d ago"
function timeAgo(isoString) {
    if (!isoString) return ''
    const diff = Math.floor((Date.now() - new Date(isoString)) / 1000) // різниця в секундах
    if (diff < 60) return 'щойно'
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`            // менше години
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`         // менше доби
    return `${Math.floor(diff / 86400)}d ago`                          // більше доби
}

// Створює HTML-елемент одного чату в сайдбарі
// id — id групи в БД, name — назва, lastMessage — останнє повідомлення, lastTime — час останнього повідомлення
function createChatItem(id, name, lastMessage = '', lastTime = '') {
    const div = document.createElement('div')
    div.dataset.groupId = id        // зберігаємо id групи в data-атрибуті для подальшого пошуку
    div.className = 'chat-item2'
    div.onclick = () => openChat(id, name)  // при кліку відкриваємо чат
    div.innerHTML = `
        <div class="avatar ${getColor(name)}">${name[0].toUpperCase()}</div>
        <div class="chat-info">
            <div class="chat-row">
                <span class="chat-name">${name}</span>
                <span class="chat-time">${timeAgo(lastTime)}</span>
            </div>
            <p class="chat-preview">${lastMessage}</p>
        </div>
    `
    return div
}

// Чекаємо поки браузер повністю завантажить HTML сторінку
window.addEventListener("DOMContentLoaded", async () => {

    // Запитуємо сервер список всіх чатів з останніми повідомленнями
    const res = await fetch("/get_chats")
    const chats = await res.json()
    const allChats = document.querySelector('.all-chats')

    // Очищаємо статичні заглушки які були в HTML
    allChats.innerHTML = ''

    // Для кожного чату створюємо елемент і додаємо в список
    chats.forEach(chat => {
        allChats.appendChild(createChatItem(chat.id, chat.name, chat.last_message, chat.last_time))
    })

    // Запитуємо сервер чи є у поточного юзера власний чат
    const myRes = await fetch("/my_chat")
    const data = await myRes.json()

    // Якщо власний чат існує — показуємо його блок в сайдбарі
    if (data.id) {
        document.getElementById("my-chat-item").style.display = "flex"
        document.getElementById("my-chat-name").textContent = data.name
        document.querySelector(".chat_and_delete").style.display = "flex"
        document.getElementById("my-chat-hr").style.display = "block"
        document.getElementById("my-chat-avatar").textContent = data.name[0].toUpperCase()
        document.getElementById("div-create-chat").style.display = "none"  // ховаємо кнопку "Створити чат"

        // Додаємо обробник кліку — при натисканні на власний чат відкриваємо його
        document.getElementById("my-chat-item").onclick = () => openChat(data.id, data.name)
    }
})