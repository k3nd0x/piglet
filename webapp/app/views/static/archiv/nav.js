document.addEventListener("DOMContentLoaded", function(event) {

    menue_mode = localStorage.getItem("menue") || "maxi"
    const showNavbar = (toggleId, navId, bodyId, headerId) => {
    const toggle = document.getElementById(toggleId),
    nav = document.getElementById(navId),
    bodypd = document.getElementById(bodyId),
    headerpd = document.getElementById(headerId)
	if (menue_mode == "mini"){
		if (nav.classList.contains('show_nav')){
			nav.classList.remove('show_nav')
		}
			    // change icon
		if (toggle.classList.contains('bx-chevron-left')){
			toggle.classList.remove('bx-chevron-left')
		}
		if (!toggle.classList.contains('bx-chevron-right')){
			toggle.classList.add('bx-chevron-right')
		}
			    // add padding to body
		if (bodypd.classList.contains('body-pd')){
			bodypd.classList.remove('body-pd')
		}
			    // add padding to header
		if (headerpd.classList.contains('body-pd')){
			headerpd.classList.remove('body-pd')
		}

	}else if (menue_mode == "maxi"){
		if (!nav.classList.contains('show_nav')){
			nav.classList.add('show_nav')
		}
		if (!toggle.classList.contains('bx-chevron-left')){
			toggle.classList.add('bx-chevron-left')
		}
		if (toggle.classList.contains('bx-chevron-right')){
			toggle.classList.remove('bx-chevron-right')
		}
		if (!bodypd.classList.contains('body-pd')){
			bodypd.classList.add('body-pd')
		}
		if (!headerpd.classList.contains('body-pd')){
			headerpd.classList.add('body-pd')
		}
	}
        if (toggle && nav && bodypd && headerpd ) {
            toggle.addEventListener('click', () => {
		nav.classList.toggle('show_nav')

		toggle.classList.toggle('bx-chevron-left')
		toggle.classList.toggle('bx-chevron-right')

		bodypd.classList.toggle('body-pd')

		headerpd.classList.toggle('body-pd')

		if (menue_mode == "mini"){
			localStorage.setItem("menue", "maxi");
		}else if (menue_mode == "maxi"){
			localStorage.setItem("menue", "mini");
		}

            })
        }
    }
    showNavbar('header-toggle', 'nav-bar', 'body-pd', 'header')

    /*===== LINK ACTIVE =====*/
    const linkColor = document.querySelectorAll('.nav_link')

    function colorLink() {
        if (linkColor) {
            linkColor.forEach(l => l.classList.remove('active'))
            this.classList.add('active')
        }
    }
    linkColor.forEach(l => l.addEventListener('click', colorLink))

    // Your code to run since DOM is loaded and ready
});
