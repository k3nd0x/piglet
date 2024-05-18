    document.addEventListener("DOMContentLoaded", function() {

    const nav_bar = document.getElementById('nav-bar');
    const nav_list = document.getElementById('nav-list');
    const header = document.getElementById('header');
    const body = document.body;
    const chevron = document.getElementById('chevron-icon');

    menu_mode = localStorage.getItem("menu") || "maxi"

    function closeMenue() {
        menu_mode = localStorage.getItem("menu") || "maxi"

        if ( menu_mode == "mini") {
			localStorage.setItem("menu", "maxi");
        } else {
            localStorage.setItem("menu", 'mini')
        }
        nav_bar.classList.toggle('show-nav');
        header.classList.toggle('body-pd');
        body.classList.toggle('body-pd');

        if ( chevron.classList.contains('bx-chevron-left') ) {
            chevron.classList.remove('bx-chevron-left')
            chevron.classList.add('bx-chevron-right')
        } else {
            chevron.classList.remove('bx-chevron-right')
            chevron.classList.add('bx-chevron-left')

        }
        nav_list.classList.toggle('show-nav');


    }

    document.getElementById('close-menu').addEventListener('click', closeMenue);

    if ( menu_mode == "mini" ) {
        nav_bar.classList.remove('show-nav');
        header.classList.remove('body-pd');
        body.classList.remove('body-pd');
        chevron.classList.remove('bx-chevron-left')
        chevron.classList.add('bx-chevron-right')
        nav_list.classList.remove('show-nav');
    } else {
        nav_bar.classList.add('show-nav');
        header.classList.add('body-pd');
        body.classList.add('body-pd');
        chevron.classList.add('bx-chevron-left')
        chevron.classList.remove('bx-chevron-right')
        nav_list.classList.add('show-nav');

    }
});