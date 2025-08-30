document.addEventListener('DOMContentLoaded', function() {
    loadContributors();
    loadEssays();
});

async function loadContributors() {
    try {
        const response = await fetch('authors.txt');
        const contributorsText = await response.text();
        
        const contributorsElement = document.getElementById('contributors');
        const authors = contributorsText.trim().split('\n');
        contributorsElement.textContent = authors.join(' · ');
        
    } catch (error) {
        console.error('Error loading contributors:', error);
    }
}

async function loadEssays() {
    try {
        const response = await fetch('log.json');
        const essays = await response.json();
        
        const essaysListElement = document.getElementById('essays-list');
        essaysListElement.innerHTML = '';
        
        essays.forEach((essay, index) => {
            const essayItem = createEssayItem(essay, index);
            essaysListElement.appendChild(essayItem);
        });
        
    } catch (error) {
        console.error('Error loading essays:', error);
    }
}

function createEssayItem(essay, index) {
    const listItem = document.createElement('li');
    listItem.className = 'essay-item';
    
    const dateElement = document.createElement('div');
    dateElement.className = 'essay-date';
    const formattedRelativeDate = formatDate(essay.date);
    const formattedActualDate = formatActualDate(essay.date);
    dateElement.innerHTML = `${formattedRelativeDate} <span class="pipe">|</span> ${formattedActualDate}`;
    
    const titleElement = document.createElement('a');
    titleElement.className = 'essay-title';
    titleElement.href = `/log/log-paper-${index + 1}.pdf`;
    titleElement.textContent = essay.title;
    titleElement.target = '_blank'; 
    
    const authorElement = document.createElement('div');
    authorElement.className = 'essay-author';
    authorElement.textContent = essay.contributors.join(', ');
    
    listItem.appendChild(dateElement);
    listItem.appendChild(titleElement);
    listItem.appendChild(authorElement);
    
    return listItem;
}

function formatDate(dateString) {
    const essayDate = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - essayDate);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
        return 'today';
    } else if (diffDays === 1) {
        return '1 day ago';
    } else if (diffDays < 30) {
        return `${diffDays} days ago`;
    } else if (diffDays < 365) {
        const diffMonths = Math.floor(diffDays / 30);
        if (diffMonths === 1) {
            return 'about 1 month ago';
        } else {
            return `about ${diffMonths} months ago`;
        }
    } else {
        const diffYears = Math.floor(diffDays / 365);
        if (diffYears === 1) {
            return 'about 1 year ago';
        } else {
            return `about ${diffYears} years ago`;
        }
    }
}

function formatActualDate(dateString) {
    const essayDate = new Date(dateString);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return essayDate.toLocaleDateString('en-US', options);
}