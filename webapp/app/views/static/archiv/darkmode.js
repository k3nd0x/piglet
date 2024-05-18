/*    window.addEventListener('DOMContentLoaded', (event) => {
    const btn = document.getElementById("dm");

    const body = document.getElementById("body-pd");

    const currentTheme = localStorage.getItem("theme");

    if (currentTheme === "light") {
        document.body.classList.add("light-theme");
        localStorage.setItem("theme", "light");
    } else {
        document.body.classList.add("dark-theme");
        localStorage.setItem("theme", "dark");
    }

    btn.addEventListener("click", function() {
        document.body.classList.toggle("dark-theme");
        document.body.classList.toggle("light-theme");

        let theme = "light";
        if (document.body.classList.contains("dark-theme")) {
            theme = "dark";
        }
        localStorage.setItem("theme", theme);

    });
});
*/

window.addEventListener('DOMContentLoaded', (event) => {
    const btn = document.getElementById("dm");
    const body = document.getElementById("body-pd");
    const currentTheme = localStorage.getItem("theme");

    btn.addEventListener("click", function() {
        if (body.classList.contains("light-theme")) {
            theme = "dark";
            body.classList.add("dark-theme")
            body.classList.remove("light-theme")
        } else {
            theme = "light";
            body.classList.add("light-theme")
            body.classList.remove("dark-theme")
        }
        localStorage.setItem("theme", theme);
    });

    // Apply the stored theme immediately on page load
    if (currentTheme === "light") {
        document.body.classList.add("light-theme");
    } else {
        document.body.classList.add("dark-theme");
    }
});
