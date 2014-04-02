console.log("camcontrol.js loaded");

var Raspibear = Raspibear || {};
Raspibear.Camcontrol = Raspibear.Camcontrol || {};

Raspibear.Camcontrol.CamControlApp = function(){
	var init = function () {
		this.statusTimer = null
		this.onOffSwitch = $("#onOffSwitch")
		this.resSelect = $("#resolutionSelect")
		this.framerateSelect = $("#framerateSelect")
		this.camViewImg = $("#camviewImg")
		this.updatingUI = false
		this.switchedOn = false
		
		thisApp = this
		
		this.onOffSwitch.on("change", function(event){
			if(thisApp.updatingUI){
				return false
			}
			$this = $(this)
			console.debug("Switch toggled: " + $this.val())
			$.ajax({url:Raspibear.Camcontrol.API_BASEURL + "switchpower/" + $this.val(), type:"GET", timeout:Raspibear.Camcontrol.AJAX_TIMEOUT}).done(function(resp){
				thisApp.updatingUI = true
				console.log("switchPower response: " + resp)
				thisApp.updateUI(jQuery.parseJSON(resp))
				thisApp.updatingUI = false //if a 200 is not received, updating is never set to false, making the switch not respond
			})
			
		})
			
		this.resSelect.on("change", function(event){
			$this = $(this)
			console.log("ResolutionSelect changed:" + $this.val())
			$.ajax({url:Raspibear.Camcontrol.API_BASEURL + "settings/resolution", 
					type:"PUT", 
					timeout:Raspibear.Camcontrol.AJAX_TIMEOUT,
					data:{"resolution":$this.val()}
					}).done(function(resp){
				console.log("setresolution resp: " + resp)		
				thisApp.updateUI(jQuery.parseJSON(resp))
			});
		})		
		
		this.framerateSelect.on("change", function(event){
			$this = $(this)
			console.log("framerateSelect changed:" + $this.val())
			$.ajax({url:Raspibear.Camcontrol.API_BASEURL + "settings/fps", 
					type:"PUT", 
					timeout:Raspibear.Camcontrol.AJAX_TIMEOUT,
					data:{"fps":$this.val()}
					}).done(function(resp){
				console.log("setframerate resp: " + resp)
				thisApp.updateUI(jQuery.parseJSON(resp))
			});	
		})		
	}
	
	var updateViewImg = function (enable, port){
		if(enable){
			src = "http://" + Raspibear.Camcontrol.SERVERHOST + ":" + port + "/?action=stream"
		}
		else{
			src = ""
		}
		this.camViewImg.attr("src", src)
		console.debug("ViewImg updated to " + this.camViewImg.attr("src"))	
	}
	
	var updateUI = function (statusDict){
		this.onOffSwitch.val(statusDict["power"].toString())
		this.onOffSwitch.flipswitch("refresh")
		this.resSelect.val(statusDict["config"]["resolution"])
		this.resSelect.selectmenu("refresh")
		this.framerateSelect.val(statusDict["config"]["fps"])
		this.framerateSelect.selectmenu("refresh")
				
		this.updateViewImg(statusDict["power"], statusDict["config"]["port"])
	};
	
	var startStatusTimer = function (){		
		this_ = this
		this.statusTimer = setInterval(function(){
			console.debug("Retrieving status...")
			$.ajax({url:Raspibear.Camcontrol.API_BASEURL + "status",type:"GET",timeout:Raspibear.Camcontrol.AJAX_TIMEOUT}).done(function(resp){
				console.debug("Status received: " + resp)
				return this_.updateUI(jQuery.parseJSON(resp))
				})
		}, Raspibear.Camcontrol.STATUS_INTERVAL)		
		console.debug("camcontrol timer " + this.statusTimer + " started")
		return true;
	}
	
	var stopStatusTimer = function(){
		clearInterval(this.statusTimer)
		console.debug("camcontrol timer " + this.statusTimer + " stopped")
		return true;
	}
		
	var public = {
			init: init,
			updateUI: updateUI,
			startStatusTimer: startStatusTimer,
			stopStatusTimer: stopStatusTimer,
			updateViewImg: updateViewImg
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

$("#webcam").on("pagehide", function(event, ui){
	console.debug("pagehide")
	Raspibear.Camcontrol.ccApp.stopStatusTimer()
})

$("#webcam").on("pageinit", function(event, ui){
	console.debug("pageinit")
	Raspibear.Camcontrol.ccApp = new Raspibear.Camcontrol.CamControlApp()
	Raspibear.Camcontrol.ccApp.init()
	
});

$("#webcam").on("pageshow", function(event, ui){
	console.debug("pageshow")
	Raspibear.Camcontrol.ccApp.startStatusTimer()
	$.ajax({url:Raspibear.Camcontrol.API_BASEURL + "status",type:"GET",timeout:Raspibear.Camcontrol.AJAX_TIMEOUT}).done(function(resp){
				console.debug("Status received: " + resp)
				return Raspibear.Camcontrol.ccApp.updateUI(jQuery.parseJSON(resp))
				})
});
	