document.getElementById('changeAvatarBtn').addEventListener('click', () => {
    // клік по невидимому input відкриває системний діалог вибору файлу
    document.getElementById('avatarInput').click()
})

document.getElementById('avatarInput').addEventListener('change', (e) => {
    const file = e.target.files[0]
    if (!file) return

    // перевірка формату на клієнті (додатково до серверної перевірки)
    const allowed = ['image/png', 'image/jpeg', 'image/webp']
    if (!allowed.includes(file.type)) {
        alert('Підтримуються лише формати: png, jpg, jpeg, webp')
        return
    }

    // FormData — спеціальний об'єкт для відправки файлів через fetch
    const formData = new FormData()
    formData.append('avatar', file)

    fetch('/upload_avatar', {
        method: 'POST',
        body: formData  // без Content-Type — браузер сам виставить multipart/form-data
    })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                updateAvatarDisplay(data.avatar_url)
            } else {
                alert('Не вдалося завантажити зображення')
            }
        })
})

document.getElementById('deleteAvatarBtn').addEventListener('click', () => {
    fetch('/delete_avatar', { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                resetAvatarDisplay()
            }
        })
})

// оновлює і модалку, і хедер одночасно після завантаження нової аватарки
function updateAvatarDisplay(avatarUrl) {
    const preview = document.getElementById('avatarPreview')
    const header = document.getElementById('headerAvatar')

    preview.innerHTML = `<img src="${avatarUrl}?t=${Date.now()}" alt="avatar">`
    header.innerHTML = `<img src="${avatarUrl}?t=${Date.now()}" alt="avatar">`
}

// повертає літери замість фото після видалення аватарки
function resetAvatarDisplay() {
    const initials = document.getElementById('avatarPreview').dataset.initials || 'AA'
    document.getElementById('avatarPreview').innerHTML = `<p>${initials}</p>`
    document.getElementById('headerAvatar').innerHTML = `<p>${initials}</p>`
}