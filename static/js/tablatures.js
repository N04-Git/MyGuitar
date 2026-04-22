// JS - Tablatures page
const tabs_container = document.querySelector('.tablatures');
const search_name = document.querySelector('.search #name input');
const search_sort = document.querySelector('.search #sort select');

// Globals
let PAGE_SETTINGS = {'text': '', 'sort':''};

// Functions
function add_tablature(tablature) {
    const item = document.createElement('div');
    item.classList.add('item');

    const title = document.createElement('h3');
    title.innerText = tablature.title;
    item.appendChild(title);

    const author = document.createElement('h4');
    author.innerText = tablature.artist;
    item.appendChild(author);

    const download_btn = document.createElement('button');
    const img = document.createElement('img');
    img.src = 'static/images/ui/download.png';
    download_btn.appendChild(img);
    item.appendChild(download_btn);
    tabs_container.appendChild(item);

    download_btn.onclick = () => {
        // Trigger download
        const a = document.createElement('a');
        a.href = "/api/" + tablature.filepath;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}

function refresh_tablatures() {

    PAGE_SETTINGS['text'] = search_name.value;
    PAGE_SETTINGS['sort'] = search_sort.value;

    // API
    call_api('/tabs', PAGE_SETTINGS)
    .then(tabs => {
        // Reset & Update
        tabs_container.innerHTML = '';
        tabs.forEach(tab => {
            add_tablature(tab);
        });
    })
}

// Events
search_name.addEventListener('input', () => {
    refresh_tablatures();
})

search_sort.addEventListener('change', () => {
    refresh_tablatures();
})

refresh_tablatures();