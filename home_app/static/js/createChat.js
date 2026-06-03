document.getElementById("btnCreate").addEventListener("click", async () => {
    const name = document.getElementById("chatNameInput").value.trim();

    const result = await fetch("/create_chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
    });

    if (result.status === 400){
        const data = await result.json();
        if (data.console.error === "already_exists") {
            alert("Чат вже існує!");
        }
        return;
    }
    
    if (result.ok) {
        location.reload();
    }
}); 