console.log("camcontrol.js loaded");

var Raspibear = Raspibear || {};
Raspibear.Camcontrol = Raspibear.Camcontrol || {};

Raspibear.Camcontrol.CamControlApp = function(){
	var init = function () {
		this.statusTimer = null
		this.onOffSwitch = $("#onOffSwitch")
		this.resSelect = $("#resolutionSelect")
		this.framerateSelect = $("#framerateSelect")
		this.camViewImg = $("#camViewImg")
		
		thisApp = this
		
		var onSwitchChange = function(){
			
			
		}
		
		this.onOffSwitch.on("change", function(event){
			$this = $(this)
			console.debug("Switch toggled: " + $this.val())
			$.ajax({url:Raspibear.Camcontrol.API_BASEURL + "switchpower/" + $this.val(), type:"GET", timeout:Raspibear.Camcontrol.AJAX_TIMEOUT}).done(function(resp){
				console.log("switchPower response: " + resp)
				thisApp.onOffSwitch.val(jQuery.parseJSON(resp))
				thisApp.onOffSwitch.flipswitch("refresh")
				// Add <img> control here
				})
		})
			
		this.resSelect.on("change", function(event){
			$this = $(this)
			console.log("ResolutionSelect changed:" + $this.val())
			$.ajax({url:Raspibear.Camcontrol.API_BASEURL + "settings/resolution" + $this.val(), type:"PUT", timeout:Raspibear.Camcontrol.AJAX_TIMEOUT}).done(function(resp){
				console.log("setresolution resp: " + resp)		
				thisApp.resSelect.val(jQuery.parseJSON(resp))
				thisApp.resSelect.selectmenu("refresh")
				});
		})		
		
		this.framerateSelect.on("change", function(event){
			$this = $(this)
			console.log("framerateSelect changed:" + $this.val())
			$.ajax({url:Raspibear.Camcontrol.API_BASEURL + "setframerate/" + $this.val(), type:"GET", timeout:Raspibear.Camcontrol.AJAX_TIMEOUT}).done(function(resp){
				console.log("setframerate resp: " + resp)		
				thisApp.framerateSelect.val(jQuery.parseJSON(resp))
				thisApp.framerateSelect.selectmenu("refresh")
				});	
		})		
	}
	
	var updateUI = function (statusDict){
		console.debug("Updating ui..")
		this.onOffSwitch.val(statusDict["power"].toString())
		this.onOffSwitch.flipswitch("refresh")
		return true	
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
	