
document.addEventListener("DOMContentLoaded", function() {
    const currentVersion = "v1.3"
    const owner = 'k3nd0x'
    const repo = 'piglet'
    const p_version = document.getElementById('version')
    fetch(`https://api.github.com/repos/${owner}/${repo}/releases/latest`)
    .then(response => response.json())
    .then(data => {
        const latestVersion = data.tag_name; // Assumes the version is stored in the tag_name field
        if (currentVersion !== latestVersion) {
            p_version.textContent = `New Version available at Github '${latestVersion}'`;
        } else {
            p_version.textContent = `Piglet - Version ${currentVersion}`;
        }
    })
    .catch(error => console.error('Error fetching the latest version:', error));
});