document.getElementById('new-tab').addEventListener('click', () => {
    fetch('/tabs', { method: 'POST' })
        .then(response => response.json())
        .then(data => console.log('New Tab:', data));
});

document.getElementById('reload').addEventListener('click', () => {
    const currentTabId = 0; // Assume first tab
    fetch('/reload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tab_id: currentTabId })
    }).then(response => response.json())
      .then(data => console.log('Reload:', data));
});
