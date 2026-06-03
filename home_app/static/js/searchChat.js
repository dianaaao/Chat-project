document.querySelector(".line input").addEventListener("input", async (e) => {
    const query = e.target.value.trim();

    const conteiner = document.querySelector(".all-chats");
    const originalHTML = conteiner.innerHTML;

    if (!query) {
        location.reload();
        conteiner.innerHTML = originalHTML
        return
    }

    // Відправляємо GET запит на Flask з параметром q (текст пошуку)
    // encodeURIComponent — щоб кирилиця і спецсимволи не зламали URL
    // наприклад "Мій чат" → "M%D0%B8%D0%B9%20%D1%87%D0%B0%D1%82"
    const res = await fetch(`/search_chats?q=${encodeURIComponent(query)}`);
    
    // Парсимо відповідь від Flask з JSON в JS масив
    // chats = [{ id: 1, name: "..." }, { id: 2, name: "..." }]
    const chats = await res.json();

    // Перезаписуємо вміст контейнера результатами пошуку
    // .map() — перетворює кожен об'єкт чату в HTML рядок
    // .join("") — склеює масив рядків в один великий рядок
    container.innerHTML = chats.map(c => `
        <div class="chat-item2" data-id="${c.id}" onclick="confirmJoin(${c.id}, '${c.name}')">
            
            <!-- Аватар: перша літера назви чату у верхньому регістрі -->
            <div class="avatar av-blue">${c.name[0].toUpperCase()}</div>
            
            <div class="chat-info">
                <div class="chat-row">
                    <!-- Назва чату -->
                    <span class="chat-name">${c.name}</span>
                </div>
                <!-- Підказка що треба натиснути -->
                <p class="chat-preview">Натисніть щоб приєднатись</p>
            </div>
        </div>
    `).join("");
});



function confirmJoin(chatId, chatName) {
    if (confirm(`Приєднатись до чату "${chatName}"?`)) {
        // Якщо юзер натиснув "ОК" — відправляємо POST запит на сервер
        // Flask додає юзера в UserGroup і повертає { ok: true }
        fetch(`/join_chat/${chatId}`, { method: "POST" })
            // .then() — виконується після того як сервер відповів
            // перезавантажуємо сторінку щоб відобразились нові чати юзера
            .then(() => location.reload());
    }
}