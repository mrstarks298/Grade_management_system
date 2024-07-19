document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar
    document.getElementById('sidebarToggle').addEventListener('click', function() {
        var sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('active');
        this.classList.toggle('active');
        
        // Toggle the arrow direction
        var arrowIcon = this.querySelector('i');
        if (sidebar.classList.contains('active')) {
            arrowIcon.classList.remove('bx-chevron-left');
            arrowIcon.classList.add('bx-chevron-right');
        } else {
            arrowIcon.classList.remove('bx-chevron-right');
            arrowIcon.classList.add('bx-chevron-left');
        }
    });

    // Toggle dark mode
    document.getElementById('darkModeToggle').addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        if (document.body.classList.contains('dark-mode')) {
            this.innerHTML = '<i class="bx bx-sun"></i>';
        } else {
            this.innerHTML = '<i class="bx bx-moon"></i>';
        }
        
        // Save preference to localStorage
        if (document.body.classList.contains('dark-mode')) {
            localStorage.setItem('darkMode', 'enabled');
        } else {
            localStorage.removeItem('darkMode');
        }
    });

    // Load dark mode preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        document.getElementById('darkModeToggle').innerHTML = '<i class="bx bx-sun"></i>';
    }
});

function displayGrades(uploadId) {
    window.location.href = "/display_grades?upload_id=" + encodeURIComponent(uploadId);
}