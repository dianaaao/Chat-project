// 1. Юзер натискає "Створити"
document.getElementById("btnCreate").addEventListener("click", async () => {

    // 2. Беремо назву з input
    const name = document.getElementById("chatNameInput").value.trim();

    // fetch — це вбудована JS функція для відправки HTTP запитів до сервера без перезавантаження сторінки. Вона повертає проміс, який резолвиться в об'єкт Response, що містить відповідь від сервера.
    // 3. Відправляємо на сервер
    const res = await fetch("/create_chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    });

    // 4. Обробляємо відповідь
    if (res.status === 400) {
        const data = await res.json();
        if (data.error === "already_exists") {
            alert("Чат вже існує!");
        }
        return;
    }

    if (res.ok) {
        location.reload(); // оновлюємо сторінку
    }
});


