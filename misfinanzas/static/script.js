function toggleMenu() {
    const menu = document.getElementById('dropdown-menu');
    menu.classList.toggle('active');
}

// para que se cierre si haces clic fuera
document.addEventListener('click', function(e) {
    const userInfo = document.querySelector('.user-info');
    if (!userInfo.contains(e.target)) {
        document.getElementById('dropdown-menu').classList.remove('active');
    }
});