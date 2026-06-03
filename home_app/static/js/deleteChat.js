
document.getElementById("deleteBtnConfirm").addEventListener("click", async () => {
    const result = await fetch("/delete_chat", {method: "DELETE"});
    if (result.ok) {
        location.reload();
    }
    
});