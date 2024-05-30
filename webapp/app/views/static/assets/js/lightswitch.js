    document.addEventListener("DOMContentLoaded", function() {
        const body = document.body;
        let header = null;
        let table = null;
        try {
            header = document.getElementById('header');
            table = document.getElementsByClassName('table-piglet')
        } catch (error) {
            header = null;
            table = null;
        }
        const html = document.documentElement;

        function switchLight() {
            const theme = localStorage.getItem("theme") || "light"
            if ( header !== null ){
                header.classList.toggle("dark")
            }
            if ( theme === "light") {
                html.setAttribute('data-bs-theme', 'dark')
                localStorage.setItem("theme", "dark");
                for (var i = 0; i < table.length; i++) {
                    table[i].classList.add('table-dark')
                }
            } else if ( theme === "dark") {
                for (var i = 0; i < table.length; i++) {
                    table[i].classList.remove('table-dark')
                }
                localStorage.setItem("theme", 'light')
                html.removeAttribute('data-bs-theme')
            }
        }
        try {
            document.getElementById('light-switch').addEventListener('click', switchLight);
        } catch ( error ){
        }

        const theme = localStorage.getItem("theme") || "light"
        if ( theme == "dark"){
            body.classList.toggle("dark")

            if (header !== null ) {
                header.classList.toggle("dark")
            }
            html.setAttribute('data-bs-theme', 'dark')
            for (var i = 0; i < table.length; i++) {
                table[i].classList.add('table-dark')
            }
        } else {
            for (var i = 0; i < table.length; i++) {
                table[i].classList.remove('table-dark')
            }
            html.removeAttribute('data-bs-theme')

        }
    });