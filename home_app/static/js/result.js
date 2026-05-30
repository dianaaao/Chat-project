// Чекаємо поки браузер повністю завантажить HTML сторінку
// DOMContentLoaded — спрацьовує коли вся структура HTML готова
window.addEventListener("DOMContentLoaded", async () => {
    
    // Запитуємо Flask: чи є у поточного юзера власний чат?
    // Flask дивиться flask_login.current_user і шукає Group по owner_id
    const res = await fetch("/my_chat");
    
    // Парсимо відповідь:
    // якщо чат є    → data = { id: 1, name: "Мій чат" }
    // якщо чату нема → data = {}
    const data = await res.json();

    // Перевіряємо чи прийшов id (тобто чат існує)
    if (data.id) {
        
        // Показуємо блок з чатом (в HTML він hidden за замовчуванням)
        document.getElementById("my-chat-item").style.display = "flex";
        
        // Вписуємо назву чату в span з id="my-chat-name"
        document.getElementById("my-chat-name").textContent = data.name;
        
        // Показуємо заголовок "Ваш чат" разом з кнопкою видалення (кошик)
        document.querySelector(".chat_and_delete").style.display = "flex";
        
        // Показуємо розділювач <hr> під власним чатом
        document.getElementById("my-chat-hr").style.display = "block";
        
        // В аватар вставляємо першу літеру назви чату у верхньому регістрі
        // наприклад "general" → "G"
        document.getElementById("my-chat-avatar").textContent = data.name[0].toUpperCase();
        
        // Ховаємо кнопку "+ Створити чат" — бо чат вже є, другий створити не можна
        document.getElementById("div-create-chat").style.display = "none";
    }
    // Якщо data.id немає — нічого не робимо, кнопка "Створити чат" залишається видимою
});