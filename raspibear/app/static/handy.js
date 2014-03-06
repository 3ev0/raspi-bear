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

String.prototype.lpad = function(padString, length) {
	var str = this;
    while (str.length < length)
        str = padString + str;
    return str;
}
 
//pads right
String.prototype.rpad = function(padString, length) {
	var str = this;
    while (str.length < length)
        str = str + padString;
    return str;
}

function sec_to_timestr(secs){
	hours = Math.floor(secs/(60*60))
	minutes = Math.floor(secs/(60))
	seconds = secs % 60
	return String(hours).lpad("0",2) + ":" + String(minutes).lpad("0",2) + ":" + String(seconds).lpad("0",2)
	
}


function updateMarqueeRange(element) {
	var marqueeRule = "";
	for (var i = 0 ; i < document.styleSheets.length ; i++) {
        var rules = document.styleSheets[i].cssRules;
        for (var j = 0 ; j < rules.length ; j++) {
            var rule = rules[j];
            if (rule.type == window.CSSRule.WEBKIT_KEYFRAMES_RULE && rule.name == "marquee") {
                marqueeRule = rule;
            }
        }
    }
    
    if (null == marqueeRule) {
        return;
    }

    // remove the old animation (if any)
    element.style.webkitAnimationName = "none";
    var textWidth = getStringWidthPixels(element.innerText, window.getComputedStyle(element).fontSize);
    elementWidth = element.offsetWidth;
    marqueeRule.deleteRule("0%");
    marqueeRule.deleteRule("100%");
    
    //console.log("textwidth: " + textWidth + " elementWidth: " + elementWidth)
	
    if(textWidth > elementWidth){
    	// update the values of our keyframe animation
    	marqueeRule.insertRule('0% { text-indent: 0px; }');
    	marqueeRule.insertRule('100% { text-indent: ' + -textWidth + 'px; }');
    }
    
    // re-assign the animation (to make it run)
    element.style.webkitAnimationName = "marquee";
}