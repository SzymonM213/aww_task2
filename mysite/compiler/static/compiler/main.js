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

function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("trapezium");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

document.getElementById("defaultOpen").click();

function showDep(evt, procName) {
    var i, depcontent, tablinks;
    depcontent = document.getElementsByClassName("dependent-content");
    for (i = 0; i < depcontent.length; i++) {
      depcontent[i].style.display = "none";
    }
    document.getElementById(procName).style.display = "block";
}

document.getElementById("defaultChosen").click();

function downloadNasm() {
    const text = document.getElementById("to-download").textContent;
    const filename = document.getElementById("nasm-filename").textContent;
    const blob = new Blob([text], {type: "text/plain;charset=utf-8"});
    saveAs(blob, filename);
}

function saveAs(blob, filename) {
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}