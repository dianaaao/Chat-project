const tabHistory = []

function switchToTab(index) {
    const panels = [
        document.querySelector('.your-chats'),
        document.querySelector('.general-chat'),
        document.querySelector('.users')
    ]
    const buttons = [
        document.getElementById('tab-chats'),
        document.getElementById('tab-general'),
        document.getElementById('tab-users')
    ]

    const currentIndex = panels.findIndex(p => p && p.classList.contains('tab-active'))
    if (currentIndex !== -1 && currentIndex !== index) {
        tabHistory.push(currentIndex)
    }

    panels.forEach((p, i) => p && p.classList.toggle('tab-active', i === index))
    buttons.forEach((b, i) => b && b.classList.toggle('tab-active', i === index))

    updateBackButton()
}

function goBack() {
    if (tabHistory.length === 0) return
    const prev = tabHistory.pop()

    const panels = [
        document.querySelector('.your-chats'),
        document.querySelector('.general-chat'),
        document.querySelector('.users')
    ]
    const buttons = [
        document.getElementById('tab-chats'),
        document.getElementById('tab-general'),
        document.getElementById('tab-users')
    ]

    panels.forEach((p, i) => p && p.classList.toggle('tab-active', i === prev))
    buttons.forEach((b, i) => b && b.classList.toggle('tab-active', i === prev))

    updateBackButton()
}

function updateBackButton() {
    const btn = document.querySelectorAll('.btn-back')
    console.log('updateBackButton', btn, tabHistory.length, window.innerWidth)
    if (!btn) return
    const isMobile = window.innerWidth <= 480
    document.querySelectorAll('.btn-back').forEach(btn => {
        btn.style.display = (isMobile && tabHistory.length > 0) ? 'flex' : 'none'
    })
}

document.addEventListener('DOMContentLoaded', function () {
    switchToTab(0)
    tabHistory.length = 0 // чистим после инициализации

    document.getElementById('tab-chats')?.addEventListener('click', () => switchToTab(0))
    document.getElementById('tab-general')?.addEventListener('click', () => switchToTab(1))
    document.getElementById('tab-users')?.addEventListener('click', () => switchToTab(2))
    document.querySelectorAll('.btn-back').forEach(btn => {
        btn.addEventListener('click', goBack)
    })

    // клик на название чата в хедере → открывает users
    document.querySelector('.chat-title')?.addEventListener('click', () => {
        if (window.innerWidth <= 480) switchToTab(2)
    })
})