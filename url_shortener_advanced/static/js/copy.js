function copy() {
    const input = document.getElementById("short");
    input.select();
    document.execCommand("copy");
    alert("Copied!");
}
