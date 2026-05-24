// JS - Cours

// Classes
const classview = document.querySelector('#classview');
const class_html = classview.querySelector('.html');
function loadClass(classFile) {
    classview.className = 'visible';

    // Get data
    fetch(`/api/courses/${classFile}`).then(
        (response) => {
            console.log(response)
            return response.text();
        }
    ).then( (data) => {
        // Inject
        class_html.innerHTML = data;
    }).catch( (error) => { console.warn('Error while loading class data :', error) })
}

const closeButton = document.querySelector('#classview .close');
closeButton.onclick = () => {
    classview.classList.remove('visible');
}

// Tree
async function loadTree() {

    const response = await fetch('/api/course');
    const data = await response.json();

    // Create lookup map
    const nodeMap = {};
    let root_node = null;

    data.nodes.forEach(node => {
        nodeMap[node.id] = node;
        if (!root_node) {
            root_node = node.id
        }
    });

    // Recursive renderer
    function renderNode(nodeId) {

        const nodeData = nodeMap[nodeId];

        // Create NODE Wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'wrapper';
        const node = document.createElement('div');
        node.className = 'node';
        const title = document.createElement('p');
        title.innerText = nodeData.title;
        wrapper.appendChild(node);
        node.appendChild(title);

        // Onclick
        node.addEventListener('click', () => {
            loadClass(nodeData.fname);
        })

        // CHILDREN (if any, render them)
        if (nodeData.children.length > 0) {

            const childrenContainer = document.createElement('div');
            if (nodeData.children.length > 1) {
                childrenContainer.className = 'children';
            } else {
                childrenContainer.className = "child";
            }

            nodeData.children.forEach(childId => {
            childrenContainer.appendChild(
                renderNode(childId)
            );
            });

            wrapper.appendChild(childrenContainer);
        } else {
            // Add custom class
            wrapper.classList.add('no-child');
        }

        return wrapper;
    }

    // START FROM ROOT
    const treeElement = renderNode(root_node);
    document.getElementById('tree').appendChild(treeElement);
}

loadTree();

// Moveable Map
const viewport = document.getElementById('viewport');
const tree = document.getElementById('tree');

let isDragging = false;
let startX = 0;
let startY = 0;

let currentX = 0;
let currentY = 0;

viewport.addEventListener('mousedown', (e) => {
    isDragging = true;
    startX = e.clientX - currentX;
    startY = e.clientY - currentY;
});

window.addEventListener('mouseup', () => {
    isDragging = false;
})

window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;

    currentX = e.clientX - startX;
    currentY = e.clientY - startY;

    tree.style.transform = `translate(${currentX}px, ${currentY}px)`;

})
