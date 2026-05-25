const modal = document.getElementById("modal");

document.getElementById("openModal").addEventListener("click", () => {
    modal.classList.add("active");
});

// () => {} - стрелочная функция
document.getElementById("closeModal").addEventListener("click", () => {
    modal.classList.remove("active");
});
document.getElementById("openModal").addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.classList.remove("active");
    }
});