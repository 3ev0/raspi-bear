function getStringWidthPixels(str, fontSizeStr) {
	var span = document.createElement("span");
    span.innerText = str;
    span.style.visibility = "hidden";
    span.style.fontSize = fontSizeStr;

    var body = document.getElementsByTagName("body")[0];
    body.appendChild(span);
    var textWidth = span.offsetWidth;
    body.removeChild(span);

    return textWidth;
}


