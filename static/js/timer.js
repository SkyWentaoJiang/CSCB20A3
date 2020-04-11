var timeout = 5;
function showError() {
    document.getElementById("second_show").innerHTML = timeout;
    timeout--;
    if (timeout == 0) {
        window.location.href = "/";
    } else {
        setTimeout("showError()", 1000);
    }
}
showError();