// Вішаємо обробник на кнопку "Створити" в модалці
document.getElementById("btnCreate").addEventListener("click", async () => {

    // Беремо назву чату з поля вводу і прибираємо пробіли по краях
    const name = document.getElementById("chatNameInput").value.trim()
    if (!name) return  // якщо назва порожня — нічого не робимо

    // Відправляємо POST запит на сервер з назвою чату в JSON форматі
    const res = await fetch("/create_chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })  // { name: "Назва чату" }
    })

    // Якщо сервер повернув 400 — щось пішло не так
    if (res.status === 400) {
        const data = await res.json()
        if (data.error === "already_exists") {
            // Юзер вже має чат — показуємо попередження
            alert("Чат вже існує!")
        }
        return  // зупиняємо виконання
    }

    // Якщо сервер повернув 200/201 — чат успішно створено
    if (res.ok) {
        const data = await res.json()  // отримуємо { id: 1, name: "Мій чат" }

        // Показуємо блок власного чату в сайдбарі
        document.getElementById("my-chat-item").style.display = "flex"
        document.getElementById("my-chat-item").dataset.groupId = data.id
        // Вписуємо назву чату
        document.getElementById("my-chat-name").textContent = data.name
        // Вписуємо першу літеру назви в аватар
        document.getElementById("my-chat-avatar").textContent = data.name[0].toUpperCase()
        // Показуємо заголовок "Ваш чат" з кнопкою видалення
        document.querySelector(".chat_and_delete").style.display = "flex"
        // Показуємо розділювач між власним чатом і загальним списком
        document.getElementById("my-chat-hr").style.display = "block"
        // Ховаємо кнопку "+ Створити чат" — бо чат вже є
        document.getElementById("div-create-chat").style.display = "none"

        // При кліку на власний чат — відкриваємо його
        document.getElementById("my-chat-item").onclick = () => openChat(data.id, data.name)

        // Створюємо елемент чату і додаємо його на початок загального списку
        const newChatDiv = createChatItem(data.id, data.name)
        document.querySelector('.all-chats').prepend(newChatDiv)

        // Закриваємо модалку створення чату
        closeCreateModal()
    }
})