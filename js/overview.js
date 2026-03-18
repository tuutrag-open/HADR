document.addEventListener('DOMContentLoaded', () => {

    /* ── Scroll Reveal ── */
    if ('IntersectionObserver' in window) {
        const reveals = document.querySelectorAll('.reveal');
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            },
            { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
        );
        reveals.forEach(el => observer.observe(el));
    } else {
        document.querySelectorAll('.reveal').forEach(el => el.classList.add('visible'));
    }

    /* ── Link Preview Popup ── */
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

    const links = document.querySelectorAll('a[href]');

    links.forEach(link => {
        link.addEventListener('mouseenter', async () => {
            currentTarget = link;
            const url = link.href;
            const hrefAttr = link.getAttribute('href');

            pImg.style.display = 'none';
            pTitle.textContent = '';
            pText.innerHTML = '';

            if (hrefAttr.startsWith('#')) {
                const targetEl = document.getElementById(hrefAttr.substring(1));
                if (targetEl) {
                    pTitle.textContent = 'Reference';
                    pText.innerHTML = targetEl.innerHTML;
                } else { return; }
            } else if (url.includes('en.wikipedia.org/wiki/')) {
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
                } catch { return; }
            } else if (link.dataset.preview) {
                pTitle.textContent = link.dataset.title || 'Note';
                pText.textContent = link.dataset.preview;
            } else { return; }

            const rect = link.getBoundingClientRect();
            const vw = window.innerWidth;
            const pw = 300;
            let left = rect.left;
            if (left + pw > vw - 20) left = vw - pw - 20;
            if (left < 10) left = 10;
            popup.style.left = `${left}px`;

            if (rect.top < 250) {
                popup.classList.add('flipped');
                popup.style.top = (rect.bottom + 12) + 'px';
            } else {
                popup.classList.remove('flipped');
                popup.style.top = (rect.top - 12) + 'px';
            }
            popup.classList.add('active');
        });

        link.addEventListener('mouseleave', () => {
            currentTarget = null;
            popup.classList.remove('active', 'flipped');
        });
    });
});