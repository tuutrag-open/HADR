document.addEventListener('DOMContentLoaded', () => {

    /* --- Popup Setup & Injection --- */
    const popup = document.createElement('div');
    popup.className = 'wiki-popup';
    popup.innerHTML = `
        <img src="" alt="Preview">
        <div class="wiki-content">
            <h4></h4>
            <p></p>
        </div>
    `;
    document.body.appendChild(popup);

    const pImg = popup.querySelector('img');
    const pTitle = popup.querySelector('h4');
    const pText = popup.querySelector('p');
    let currentTarget = null;

    /* --- Event Listeners --- */
    const links = document.querySelectorAll('a[href]');

    links.forEach(link => {
        link.addEventListener('mouseenter', async (e) => {
            currentTarget = link;
            const url = link.href;
            const hrefAttr = link.getAttribute('href');

            /* Reset Content */
            pImg.style.display = 'none';
            pTitle.textContent = '';
            pText.innerHTML = ''; 

            /* --- Logic Branches --- */

            /* Case 1: Internal Citations & Footnotes */
            if (hrefAttr.startsWith('#')) {
                const targetId = hrefAttr.substring(1); 
                const targetEl = document.getElementById(targetId);
                
                if (targetEl) {
                    pTitle.textContent = "Reference";
                    pText.innerHTML = targetEl.innerHTML; 
                } else {
                    return; 
                }
            }
            
            /* Case 2: Wikipedia API */
            else if (url.includes('en.wikipedia.org/wiki/')) {
                const title = url.split('/').pop();
                try {
                    const res = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${title}`);
                    const data = await res.json();
                    if (currentTarget !== link) return;

                    pTitle.textContent = data.title;
                    pText.textContent = data.extract;
                    if (data.thumbnail?.source) {
                        pImg.src = data.thumbnail.source;
                        pImg.style.display = 'block';
                    }
                } catch (err) { return; }
            }

            /* Case 3: Manual Data Preview */
            else if (link.dataset.preview) {
                pTitle.textContent = link.dataset.title || "Note";
                pText.textContent = link.dataset.preview;
            } 

            /* No Match */
            else {
                return; 
            }

            /* --- Positioning & Collision Detection --- */
            const rect = link.getBoundingClientRect();
            const viewportWidth = window.innerWidth;
            
            /* Horizontal Clamping */
            const popupWidth = 300; 
            let leftPos = rect.left;
            
            if (leftPos + popupWidth > viewportWidth - 20) {
                leftPos = viewportWidth - popupWidth - 20; 
            }
            if (leftPos < 10) {
                leftPos = 10;
            }
            popup.style.left = `${leftPos}px`;

            /* Vertical Flipping */
            const estimatedHeight = 250; 
            const spaceAbove = rect.top;

            if (spaceAbove < estimatedHeight) {
                popup.classList.add('flipped');
                popup.style.top = (rect.bottom + 12) + 'px';
            } else {
                popup.classList.remove('flipped');
                popup.style.top = (rect.top - 12) + 'px';
            }

            popup.classList.add('active');
        });

        /* Mouse Leave */
        link.addEventListener('mouseleave', () => {
            currentTarget = null;
            popup.classList.remove('active');
            popup.classList.remove('flipped');
        });
    });
});