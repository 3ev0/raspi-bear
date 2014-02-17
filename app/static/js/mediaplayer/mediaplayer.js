STATUS_INTERVAL = 1000
AJAX_TIMEOUT=5000

MPLAYER_HOST = "http://pi-beer.home.local:11111"

URL_IMGDIR = "images/mediaplayer"
URL_PLAYBUTTON = URL_IMGDIR + "/mplayer_play.png"
URL_PAUSEBUTTON = URL_IMGDIR + "/mplayer_pause.png"
URL_MUTEBUTTON = URL_IMGDIR + "/mplayer_mute.png"
URL_UNMUTEBUTTON = URL_IMGDIR + "/mplayer_speaker.png"

var statplaying = false
var statmute = false
var statpause = false

var status_timer = null

console.log("Mediaplayer.js loaded")

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

$(document).ajaxError(function(event, request, settings, exception){
	if(request.status == 404 || request.status == 500)
		$("#errorMsg").html("Error accessing URL " + settings.url + ":<br>" + request.responseText)
	else
		$("#errorMsg").html("Error accessing URL " + settings.url + ":<br>" + exception)
	$("#errorPopup").popup("open")
})

$(document).delegate("#jukebox", "pagehide", function(event, ui){
	console.log("jukebox page hidden")
	clearInterval(status_timer)
})

$(document).delegate("#jukebox", "pageinit", function(){
	
	status_timer = setInterval(function(){
		console.debug("Retrieving status...")
		$.ajax({url:MPLAYER_HOST + "/status",type:"GET",timeout:AJAX_TIMEOUT}).done(function(resp){cbStatus(resp)})
	}, STATUS_INTERVAL)
	
	$("#mplayer-volslider").on("slidestop", function(event, ui){
		console.log("Volslider set")
		$this = $(this)
		$.ajax({url:MPLAYER_HOST + "/setvol/" + $this.val(), type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){cbVolume(resp, $this)})
	})
		
	$("#mplayer-playbutton").click(function(event){
		console.log("Play clicked")
		$this = $(this)
		$.ajax({url:MPLAYER_HOST + "/play", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){cbPlay(resp)});
		console.log("play cmd sent")
		return false
	})
	
	$("#mplayer-endbutton").click(function(event){
		console.log("clicked end")
		$.ajax({url:MPLAYER_HOST + "/skip2end", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){cbSkipEnd(resp);});
		$this = $(this)
		event.stopPropagation();
		console.log("skip2end cmd sent")
		return false
	})
	
	$("#mplayer-skipbutton").click(function(event){
		console.log("clicked skip2start")
		$this = $(this)
		$.ajax({url:MPLAYER_HOST + "/skip2start", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){cbSkipStart(resp);});
		console.log("skip2start cmd sent")
		event.stopPropagation();
		return false
	})
	
	$("#mplayer-stopbutton").click(function(event){
		console.log("click stop")
		$this = $(this)
		$.ajax({url:MPLAYER_HOST + "/stop", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){cbStop(resp);});
		console.log("stop cmd sent")
		event.stopPropagation();
		return false
	})
	
	console.log("jukebox page loaded")
	
	console.debug("Retrieving status...")
	$.ajax({url:MPLAYER_HOST + "/status", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){cbStatus(resp)})
	
})
	
function uiStatusUpdate(statusDict){
	//Set play status
	if(!statusDict.playing){
		statusStop()
	}
	//Set pause status
	else{
		statusPause(statusDict.paused)		
	}	
		
	//Set volume
	volslider = $("#mplayer-volslider")
	volslider.val(statusDict.vol).slider("refresh")
	
	
	//Set songstatus
	divs = $("#divSongTitle")
	if(divs.html() != statusDict.song){
		divs.html(statusDict.song)
		updateMarqueeRange(divs.get(0))
	}
	$("#sliderProgress").attr("max", statusDict.totaltime)
	$("#sliderProgress").val(statusDict.progress).slider("refresh")	
	return true	
}

function sec_to_timestr(secs){
	hours = Math.floor(secs/(60*60))
	minutes = Math.floor(secs/(60))
	seconds = secs % 60
	return String(hours).lpad("0",2) + ":" + String(minutes).lpad("0",2) + ":" + String(seconds).lpad("0",2)
	
}

function statusPause(pause){
	var playbutton = $("#mplayer-playbutton");
	playbutton.off("click");
	if(pause){
		playbutton.attr("src", URL_PLAYBUTTON);
		playbutton.click(function(event){
			console.log("Play clicked")
			$this = $(this)
			$.ajax({url:MPLAYER_HOST + "/pause", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){cbPause(resp)});
			console.log("Pause-toggle cmd sent")
			return false
		})
	}
	else{
		playbutton.attr("src", URL_PAUSEBUTTON);
		playbutton.click(function(event){
			console.log("pause clicked")
			$this = $(this) 
			$.ajax({url:MPLAYER_HOST + "/pause", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){cbPause(resp)});
			console.log("Pause cmd sent")
			return false
		})
	}
}

	
function statusStop(){
	var playb = $("#mplayer-playbutton")
	playb.attr("src", URL_PLAYBUTTON);
	playb.off("click")
	playb.click(function(event){
		$.ajax({url:MPLAYER_HOST + "/play", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){cbPlay(resp)});
		event.stopPropagation();
		return false
	})
}

function cbPlay(resp){
	console.log("play resp: " + resp)		
	uiStatusUpdate(jQuery.parseJSON(resp))	
}

function cbPause(resp){
	console.log("Pause resp: " + resp)
	uiStatusUpdate(jQuery.parseJSON(resp))
	
}

function cbStop(resp){
	console.log("stop resp: " + resp)
	uiStatusUpdate(jQuery.parseJSON(resp))
}


function cbSkipStart(resp){
	console.log("skip2start resp: " + resp)
	uiStatusUpdate(jQuery.parseJSON(resp))
}

function cbSkipEnd(resp){
	console.log("skip2end resp: " + resp)
	uiStatusUpdate(jQuery.parseJSON(resp))
}

function cbVolume(resp, volslider){
	console.log("Setvol response: " + resp)
	newvol = jQuery.parseJSON(resp)
	volslider.val(newvol)
	volslider.slider("refresh")
}

function cbStatus(resp){
	console.log("Status received: " + resp)
	statusDict = jQuery.parseJSON(resp)
	return uiStatusUpdate(statusDict)
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
    
    console.log("textwidth: " + textWidth + " elementWidth: " + elementWidth)
	
    if(textWidth > elementWidth){
    	// update the values of our keyframe animation
    	marqueeRule.insertRule('0% { text-indent: 0px; }');
    	marqueeRule.insertRule('100% { text-indent: ' + -textWidth + 'px; }');
    }
    
    // re-assign the animation (to make it run)
    element.style.webkitAnimationName = "marquee";
}