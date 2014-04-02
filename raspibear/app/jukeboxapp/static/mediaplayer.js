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
		this.playlistView = $("#playlistViewDiv")
		
		thisJukebox = this
		
		thisJukebox.volSlider.on("slidestop", function(event, ui){
			console.log("Volslider set")
			$this = $(this)
			$.ajax({url:API_BASEURL + "setvol", 
					type:"PUT", 
					timeout:AJAX_TIMEOUT,
					data:{"volume":$this.val()}}).done(function(resp){
				console.log("Setvol response: " + resp)
				thisJukebox.volSlider.val(jQuery.parseJSON(resp))
				thisJukebox.volSlider.slider("refresh")
				})
		})
			
		this.playButton.on("click", function(event){
			console.log("Play clicked")
			$.ajax({url:API_BASEURL + "play", 
					type:"POST", 
					timeout:AJAX_TIMEOUT,
					data:{"song_idx":0}
				}).done(function(resp){
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
		
		console.debug("Retrieving status...")
		$.ajax({url:API_BASEURL + "status", 
				type:"GET", 
				timeout:AJAX_TIMEOUT
				}).done(function(resp){
					console.log("Status received: " + resp)
					return thisJukebox.updateUI(jQuery.parseJSON(resp))
				})
		
		console.debug("Retrieving playlists...")
		$.ajax({url:API_BASEURL + "playlists", 
				type:"GET", 
				timeout:AJAX_TIMEOUT}).done(function(resp){
			console.log("Playlists received: " + resp)
			return thisJukebox.updatePlaylistSelect(jQuery.parseJSON(resp))
			})
		
	}
	
	var updatePlaylistSelect = function(playlists){
		thisJukebox = this
		
		pdiv = $("#playlistSelectDiv")
		pdiv.html("")
		var s = $("<select id='playlistSelect'></select>")
		for(var idx in playlists){
			$("<option />", {value:idx, text: playlists[idx]}).appendTo(s)
		}
		s.appendTo(pdiv)
		s.on("change", function(event){
			console.log("Playlist selected: " + s.val())
			$.ajax({url:API_BASEURL + "playlist",
					type:"POST",
					timeout:AJAX_TIMEOUT,
					data:{"playlist_idx":s.val()}}).done(function(resp){
						console.log("Playlistselect resp: " + resp)
						thisJukebox.updatePlaylistView(jQuery.parseJSON(resp))
					})
		})
		s.selectmenu()
		console.log("Playlist selected: " + s.val())
		$.ajax({url:API_BASEURL + "playlist",
					type:"POST",
					timeout:AJAX_TIMEOUT,
					data:{"playlist_idx":s.val()}
		}).done(function(resp){
			console.log("Playlistselect resp: " + resp)
			thisJukebox.updatePlaylistView(jQuery.parseJSON(resp))
			})
	}
	
	var updatePlaylistView = function(oPlaylist){
		console.debug("Building playlist view for playlist '" + oPlaylist.name + "'")
		var ul = $("<ol id='playlistViewList' data-role='listView'></ol>")
		for(var idx in oPlaylist.songs){
			songnum = parseInt(idx)+1
			li = $("<li id='song" + idx + "' ><a data-role='button' href='#' class='ui-btn ui-corner-all'>" + oPlaylist.songs[idx].name + "</a></li>")
			li.on("click", function(event){
				songidx = this.id.substring(4)
				console.debug("selected song " + songidx)
				$.ajax({url:API_BASEURL + "play", 
						type:"POST", 
						timeout:AJAX_TIMEOUT,
						data:{"song_idx":songidx}})
				.done(function(resp){
					console.log("play resp: " + resp)		
					thisJukebox.updateUI(jQuery.parseJSON(resp))	
					});
				console.log("play cmd sent")
				return false
			})
			li.appendTo(ul)			
		}
		this.playlistView.append(ul)
		ul.listview()		
		
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
		this.progressBar.attr("max", 100)
		this.progressBar.val(0).slider("refresh")	
		this.songTitleBox.html("...")
		updateMarqueeRange(this.songTitleBox.get(0))
		
		$("#playlistViewList li").attr("class", "")
				
		
		this.playButton.attr("src", URL_PLAYBUTTON);
		this.playButton.off("click")
		this.playButton.click(function(event){
			$.ajax({url:API_BASEURL + "play", 
					type:"POST", 
					timeout:AJAX_TIMEOUT, 
					data:{"song_idx":0}
					}).done(function(resp){
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
			if(this.songTitleBox.html() != statusDict.cur_song){
				this.songTitleBox.html(statusDict.cur_song)
				updateMarqueeRange(this.songTitleBox.get(0))
			}
			if(statusDict.cur_song_idx >= 0){
				$("#playlistViewList li.current").attr("class", "")
				var sid = "song" + statusDict.cur_song_idx
				$("#playlistViewList li#" + sid).attr("class", "current")
			}
			
			this.progressBar.attr("max", statusDict.duration)
			this.progressBar.val(statusDict.progress).slider("refresh")	
			
			this.updatePauseUI(statusDict.paused)		
		}	
			
		//Set volume
		this.volSlider.val(statusDict.vol).slider("refresh")
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
			updatePlaylistSelect: updatePlaylistSelect,
			updatePlaylistView: updatePlaylistView,
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
	