
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

CodeMirror.defineMode("nasm", function() {
    var keywords = ["section", "global", "mov", "xor", "shr", "and"];
    var registers = ["eax", "ebx", "ecx", "edx", "al", "ah"];
    
    var keywordRegex = new RegExp("\\b(" + keywords.join("|") + ")\\b");
    var registerRegex = new RegExp("\\b(" + registers.join("|") + ")\\b");
    
    return {
      token: function(stream, state) {
        if (stream.match(keywordRegex))
          return "keyword";
        if (stream.match(registerRegex))
          return "variable-2";
        if (stream.match(/["'].*?["']/))
          return "string";
        if (stream.match(/;.*/))
          return "comment";
        stream.next();
      }
    };
  });

var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
    lineNumbers: true,
    mode: "nasm"
});

var prog_text = document.getElementsByClassName("program-text")[0];
editor.setSize(prog_text.width(), prog_text.height());

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

function showFile(fileId) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/compiler/file/" + fileId, true);

    xhr.onload = function() {
        if (xhr.status === 200) {
            var jsonResponse = JSON.parse(xhr.responseText);
            const name = document.getElementsByClassName('file_name')[0]
            name.textContent = jsonResponse.name;
            // const content = document.getElementsByName('content')[0]
            // content.value = jsonResponse.content;
            editor.setValue(jsonResponse.content);
            const id = document.getElementById('file-id');
            id.value = fileId;
        }
    }
    xhr.send();
}

function saveFile() {
    var xhr = new XMLHttpRequest();
    fileId = document.getElementById("file-id").value;
    xhr.open("POST", "/compiler/save-file/" + fileId + "/", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    var content = editor.getValue();
    var data = JSON.stringify({ 'content': content });
    xhr.send(data);
}


function deleteFile(fileId) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/compiler/delete-file/" + fileId + "/", true);

    xhr.onreadystatechange = function() {
        if (xhr.status === 200) {
            var listItem = document.getElementById("li-file-" + fileId);
            listItem.remove();
            if (document.getElementById("file-id").name == fileId) {
                const name = document.getElementsByClassName('file_name')[0]
                name.textContent = "";
                const content = document.getElementsByName('content')[0]
                content.value = "";
                const id = document.getElementById('file-id')
                id.name = "";
            }
        }
    }
    xhr.send();
}

function deleteDir(dirId) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/compiler/delete-dir/" + dirId + "/", true);

    xhr.onreadystatechange = function() {
        if (xhr.status === 200) {
            var listItem = document.getElementById("li-dir-" + dirId);
            listItem.remove();
        }
    }
    xhr.send();
}

function addDir(event, dirId) {
    if (event.keyCode === 13) {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/compiler/create-dir/" + dirId + "/", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                var name = document.getElementsByName('element_name')[0].value;
                if (dirId == 0) {
                    list = document.getElementsByClassName("tree")[0];
                } else {
                    dir = document.getElementById("li-dir-" + dirId);
                    list = dir.getElementsByTagName("ul")[0];
                }
                var input = document.getElementById("input-tmp");
                input.remove();
                var jsonResponse = JSON.parse(xhr.responseText);
                new_list_html = '<li class="directory" id="li-dir-' + jsonResponse.id + '">' + '<details><summary>' + name  + '<button class="fa fa-trash-o" onclick="deleteDir(' + jsonResponse.id +')"></button>' + '<button class="fa fa-file-medical" onclick="addFile(' + jsonResponse.id + ')"></button>' + '<button class="fa fa-folder-plus" onclick="createDir(' + jsonResponse.id + ')"></button>'
                new_list_html += '<label for="fileInput" id="fileLabel" class="fa fa-file-upload" onclick="handleFileSelect()"></label> <input type="file" id="fileInput" onchange="uploadFile(event, ' + jsonResponse.id + ')" style="display: none;">' + '</summary></details></li>' + list.innerHTML;
                list.innerHTML = new_list_html;
            }
        }
        var name = document.getElementsByName('element_name')[0].value;
        if (name == "") {
            name = "New folder";
        }
        var data = JSON.stringify({ 'name': name });
        xhr.send(data);
    }
    if (event.keyCode === 27) {
        if (dirId == 0) {
            list = document.getElementsByClassName("tree")[0];
        } else {
            list = document.getElementById("li-dir-" + dirId).getElementsByTagName("ul")[0];
        }
        list.getElementsByTagName("li")[0].remove();
    }
}

function createDir(dirId) {
    if (dirId == 0) {
        list = document.getElementsByClassName("tree")[0];
    }
    else {
        dir = document.getElementById("li-dir-" + dirId);
        list = dir.getElementsByTagName("ul")[0];
    }
    list.innerHTML = '<li id="input-tmp"><input type="text" onkeydown="addDir(event, ' + dirId + ')" name="element_name"></li>' + list.innerHTML;
}

function addFile(event, dirId) {
    if (event.keyCode === 13) {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/compiler/create-file/" + dirId + "/", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                var name = document.getElementsByName('element_name')[0].value;
                if (dirId == 0) {
                    list = document.getElementsByClassName("tree")[0];
                } else {
                    dir = document.getElementById("li-dir-" + dirId);
                    list = dir.getElementsByTagName("ul")[0];
                }
                var input = document.getElementById("input-tmp");
                input.remove();
                var jsonResponse = JSON.parse(xhr.responseText);
                new_list_html = '<li id="li-file-' + jsonResponse.id + '"><button class="file" type="submit" name="new_file" value="' + jsonResponse.id + '" onclick = "showFile(' + jsonResponse.id + ')">' + name + '<button class="fa fa-trash-o" onclick="deleteFile(' + jsonResponse.id + ')"></button>' + '</button></li>' + list.innerHTML;
                list.innerHTML = new_list_html;
            }
        }
        var name = document.getElementsByName('element_name')[0].value;
        if (name == "") {
            name = "New file";
        }
        var data = JSON.stringify({ 'name': name });
        xhr.send(data);
    }
    if (event.keyCode === 27) {
        if (dirId == 0) {
            list = document.getElementsByClassName("tree")[0];
        } else {
            list = document.getElementById("li-dir-" + dirId).getElementsByTagName("ul")[0];
        }
        list.getElementsByTagName("li")[0].remove();
    }
}

function createFile(dirId) {
    if (dirId == 0) {
        list = document.getElementsByClassName("tree")[0];
    }
    else {
        dir = document.getElementById("li-dir-" + dirId);
        dir.click();
        list = dir.getElementsByTagName("ul")[0];
    }
    list.innerHTML = '<li id="input-tmp"><input type="text" onkeydown="addFile(event, ' + dirId + ')" name="element_name"></li>' + list.innerHTML;
}

function handleFileSelect(dirId) {
    document.getElementById('fileInput-' + dirId).click();
}

function uploadFile(event, dirId) {
    const reader = new FileReader();
    
    var file = event.target.files[0];
    reader.onload = function(event) {
        const fileContent = event.target.result;
        const fileName = file.name;        
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/compiler/create-file/" + dirId + "/", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                var jsonResponse = JSON.parse(xhr.responseText);
                if (dirId == 0) {
                    list = document.getElementsByClassName("tree")[0];
                } else {
                    dir = document.getElementById("li-dir-" + dirId);
                    list = dir.getElementsByTagName("ul")[0];
                }
                new_list_html = '<li id="li-file-' + jsonResponse.id + '"><button class="file" type="submit" name="new_file" value="' + jsonResponse.id + '" onclick = "showFile(' + jsonResponse.id + ')">' + file.name + '<button class="fa fa-trash-o" onclick="deleteFile(' + jsonResponse.id + ')"></button>' + '</button></li>' + list.innerHTML;
                list.innerHTML = new_list_html;
            }
        } 
        var data = JSON.stringify({ 'name': fileName , 'content': fileContent});
        xhr.send(data);
    };
    reader.readAsText(event.target.files[0]);
}

function compile() {
    var file = document.getElementById("file-id");
    var fileId = file.value;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/compiler/compile/" + fileId + "/", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var jsonResponse = JSON.parse(xhr.responseText);
            document.getElementsByClassName("code-fragment")[0].innerHTML = jsonResponse.result_display;
            document.getElementsByClassName("code-fragment-raw")[0].innerHTML = jsonResponse.result;
            document.getElementById("nasm-filename").innerHTML = jsonResponse.file_name.replace(".c", "") + ".asm";
            // var xhr2 = new XMLHttpRequest();
            // xhr2.open("POST", "/compiler/create-file/" + jsonResponse.result + "/", true);
            // xhr2.send();
        }
    }
    xhr.send();
}

function sectionDisplay(sectionId) {
    var section = document.getElementById("section-" + sectionId);
    var content = section.getElementsByClassName("asm-section-content")[0];
    if (content.style.display === "none") {
        content.style.display = "block";
    } else {
        content.style.display = "none";
    }
}

function hideSections() {
    var sections = document.getElementsByClassName("asm-section-content");
    for (var i = 0; i < sections.length; i++) {
        sections[i].style.display = "none";
    }
}

function showSections() {
    var sections = document.getElementsByClassName("asm-section-content");
    for (var i = 0; i < sections.length; i++) {
        sections[i].style.display = "block";
    }
}

function colorLine(lineNumber) {
    var content = document.getElementsByName('content')[0].value;
    var lines = content.split("\n");
    var new_lines = "";
    for (var i = 0; i < lines.length; i++) {
        if (i + 1 == lineNumber) {
            new_lines += '->' + lines[i] + '<-\n';
        } else {
            new_lines += lines[i] + '\n';
        }
    }
    // var xhr2 = new XMLHttpRequest();
    // xhr2.open("POST", "/compiler/create-file/" + 420 + "/", true);
    // xhr2.send();
    document.getElementsByName('content')[0].value = new_lines;
}

function unColorLine(lineNumber) {
    var content = document.getElementsByName('content')[0].value;
    var lines = content.split("\n");
    var new_lines = "";
    for (var i = 0; i < lines.length; i++) {
        if (i + 1 == lineNumber) {
            new_lines += lines[i].replace('->', '').replace('<-', '') + '\n';
        } else {
            new_lines += lines[i] + '\n';
        }
    }
    document.getElementsByName('content')[0].value = new_lines;
}

