var isMaximized = false;
var isDarkMode = false;

function check() {
    event.preventDefault();
    var password = document.getElementById('password').value;
    if (password != "") {
        window.api.setCredentials(password);
    } 
    return false;
}

document.onreadystatechange = (event) => {    
    document.getElementById("username").innerText = window.api.username;
};