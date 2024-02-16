document.addEventListener('DOMContentLoaded', function () {
    const navItems = document.querySelectorAll('.nav-item');
    const currentPath = window.location.pathname;

    navItems.forEach((navItem) => {
        const navLink = navItem.querySelector('.nav-link');
        const href = navLink.getAttribute('href');

        if (currentPath === href) {
            navItem.classList.add('active');
            navLink.setAttribute('aria-expanded', 'true');

            const submenu = navItem.querySelector('.multi-level');
            if(submenu){
                submenu.classList.add('show', 'active');
            }
            
        }

        // Check child nav items
        const childNavItems = navItem.querySelectorAll('.nav-item');
        childNavItems.forEach((childNavItem) => {
            const childNavLink = childNavItem.querySelector('.nav-link');
            const childHref = childNavLink.getAttribute('href');

            if (currentPath === childHref) {
                navItem.classList.add('active');
                navLink.setAttribute('aria-expanded', 'true');

                const submenu = navItem.querySelector('.multi-level');
                submenu.classList.add('show', 'active');
            }
        });
    });

    const collapsedSections = document.querySelectorAll('.multi-level');
    collapsedSections.forEach((section) => {
        section.addEventListener('show.bs.collapse', function () {
            section.classList.add('show', 'active');
        });

        section.addEventListener('hide.bs.collapse', function () {
            section.classList.remove('show', 'active');
        });
    });
});
