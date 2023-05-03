function setTheme(newTheme) {
    localStorage.setItem("theme", newTheme);
    document.documentElement.className = newTheme;
}

function switchTheme() {
    if (localStorage.getItem('theme') === "light") {
        setTheme("dark");
    } else {
        setTheme("light");
    }
}

(function() {
    if (localStorage.getItem('theme') === "dark") {
        setTheme("dark");
    } else {
        setTheme("light");
    }
})();

function openNav() {
    document.getElementById("plik").style.width = "100%";
}

// Get all parent list items
const parentItems = document.querySelectorAll('.directory');

// Add event listeners to each parent item
parentItems.forEach(parentItem => {
  parentItem.addEventListener('click', event => {
    // Toggle the active state of the parent item
    event.currentTarget.classList.toggle('active');
  });
});