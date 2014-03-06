console.log("Mediaplayer.js loaded");

var Raspibear = Raspibear || {};

Raspibear.Jukebox = function(){
	
	var init = function () {
		this.statusTimer = null
		
		this.playButton = $("#mplayer-playbutton")
		this.volSlider = $("#mplayer-volslider")
		this.skip2endButton = $("#mplayer-endbutton")
		this.skip2startButton = $("#mplayer-skipbutton")
		this.stopButton =  $("#mplayer-stopbutton")
		this.progressBar = $("#sliderProgress")
		this.songTitleBox = $("#divSongTitle")
		
		thisJukebox = this
		
		thisJukebox.volSlider.on("slidestop", function(event, ui){
			console.log("Volslider set")
			$this = $(this)
			$.ajax({url:API_BASEURL + "setvol/" + $this.val(), type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){
				console.log("Setvol response: " + resp)
				thisJukebox.volSlider.val(jQuery.parseJSON(resp))
				thisJukebox.volSlider.slider("refresh")
				})
		})
			
		this.playButton.on("click", function(event){
			console.log("Play clicked")
			$.ajax({url:API_BASEURL + "play", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){
				console.log("play resp: " + resp)		
				thisJukebox.updateUI(jQuery.parseJSON(resp))	
				});
			console.log("play cmd sent")
			return false
		})
		
		this.skip2endButton.click(function(event){
			console.log("clicked end")
			$.ajax({url:API_BASEURL + "skip2end", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){
				console.log("skip2end resp: " + resp)
				thisJukebox.updateUI(jQuery.parseJSON(resp))
				});
			console.log("skip2end cmd sent")
			return false
		})
		
		this.skip2startButton.click(function(event){
			console.log("clicked skip2start")
			$.ajax({url:API_BASEURL + "skip2start", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){
				console.log("skip2start resp: " + resp)
				thisJukebox.updateUI(jQuery.parseJSON(resp))
				});
			console.log("skip2start cmd sent")
			return false
		})
		
		this.stopButton.click(function(event){
			console.log("click stop")
			$.ajax({url:API_BASEURL + "stop", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){
				console.log("stop resp: " + resp)
				thisJukebox.updateUI(jQuery.parseJSON(resp))
				});
			console.log("stop cmd sent")
			return false
		})
		
		console.debug("Retrieving status...")
		$.ajax({url:API_BASEURL + "status", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){
			console.log("Status received: " + resp)
			return thisJukebox.updateUI(jQuery.parseJSON(resp))
			})
	}
	
	var updatePauseUI = function(pauseOn){
		thisJukebox = this
		this.playButton.off("click");
		if(pauseOn){
			this.playButton.attr("src", URL_PLAYBUTTON);
			this.playButton.on("click", function(event){
				console.log("Play clicked")
				$.ajax({url:API_BASEURL + "pause", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){
					console.log("Pause resp: " + resp)
					thisJukebox.updateUI(jQuery.parseJSON(resp))
					});
				console.log("Pause-toggle cmd sent")
				return false
			})
		}
		else{
			this.playButton.attr("src", URL_PAUSEBUTTON);
			this.playButton.on("click", function(event){
				console.log("pause clicked")
				$.ajax({url:API_BASEURL + "pause", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){
					console.log("Pause resp: " + resp)
					thisJukebox.updateUI(jQuery.parseJSON(resp))
				});
				console.log("Pause cmd sent")
				return false
			})
		}
	}
	
	var updateStopUI = function() {		
		this.playButton.attr("src", URL_PLAYBUTTON);
		this.playButton.off("click")
		this.playButton.click(function(event){
			$.ajax({url:API_BASEURL + "play", type:"GET", timeout:AJAX_TIMEOUT}).done(function(resp){
				console.log("play resp: " + resp)		
				thisJukebox.updateUI(jQuery.parseJSON(resp))	
				});
			return false
		})
	};
	
	var updateUI = function (statusDict){
		//Set play status
		if(!statusDict.playing){
			this.updateStopUI()
		}
		//Set pause status
		else{
			this.updatePauseUI(statusDict.paused)		
		}	
			
		//Set volume
		this.volSlider.val(statusDict.vol).slider("refresh")
		
		
		//Set songstatus
		if(this.songTitleBox.html() != statusDict.song){
			this.songTitleBox.html(statusDict.song)
			updateMarqueeRange(this.songTitleBox.get(0))
		}
		this.progressBar.attr("max", statusDict.totaltime)
		this.progressBar.val(statusDict.progress).slider("refresh")	
		return true	
	};
	
	var startStatusTimer = function (){
		this_ = this
		this.statusTimer = setInterval(function(){
			console.debug("Retrieving status...")
			$.ajax({url:API_BASEURL + "status",type:"GET",timeout:AJAX_TIMEOUT}).done(function(resp){
				console.debug("Status received: " + resp)
				return this_.updateUI(jQuery.parseJSON(resp))
				})
		}, STATUS_INTERVAL)
		console.log("jukebox timer " + this.statusTimer + " started")
		return true;
	}
	
	var stopStatusTimer = function(){
		clearInterval(this.statusTimer)
		console.log("jukebox timer " + this.statusTimer + " stopped")
		return true;
	}
		
	var public = {
			init: init,
			updateUI: updateUI,
			updateStopUI: updateStopUI,
			updatePauseUI: updatePauseUI,
			startStatusTimer: startStatusTimer,
			stopStatusTimer: stopStatusTimer
	};
	return public;
};


$(document).ajaxError(function(event, request, settings, exception){
	if(request.status == 404 || request.status == 500)
		$("#errorMsg").html("Error accessing URL " + settings.url + ":<br>" + request.responseText)
	else
		$("#errorMsg").html("Error accessing URL " + settings.url + ":<br>" + exception)
	$("#errorPopup").popup("open")
})

$("#jukebox").on("pagehide", function(event, ui){
	console.debug("pagehide")
	Raspibear.jb.stopStatusTimer()
})

$("#jukebox").on("pageinit", function(event, ui){
	console.debug("pageinit")
	Raspibear.jb = new Raspibear.Jukebox()
	Raspibear.jb.init()
	
});

$("#jukebox").on("pageshow", function(event, ui){
	console.debug("pageshow")
	Raspibear.jb.startStatusTimer()
});
	