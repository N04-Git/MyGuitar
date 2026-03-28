// Handle Header buttons
const containers = document.querySelectorAll('header > .container');

const current = window.location.pathname;

containers.forEach((container) => {
    Array.from(container.children).forEach( (child) => {
        // Map each option with its corresponding url
        const target = child.getAttribute('data-url');
        if (target) {
            child.addEventListener('click', (event) => {
                event.preventDefault();
                window.location.href = target;
            })

            // Select current
            if (target == current) {
                child.classList.add('select');
            }

        } else {
            console.warn('No url for :', child);
        }
    })
})