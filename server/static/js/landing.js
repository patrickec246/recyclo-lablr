// Credit to Diaco M. Lotfollahi for his beautiful 'Autumn Falling Leaves' with GSAP

var total = 15;
var container = document.getElementById("pageBackground");
var w = window.innerWidth;
var h = window.innerHeight;
 
 for (i=0; i<total; i++){ 
   var Div = document.createElement('div');
   TweenLite.set(Div,{attr:{class:'leaf'},x:R(0,w),y:R(-200,-150),z:R(-200,200)});
   container.appendChild(Div);
   animm(Div);
 }
 
 function animm(elm){   
   TweenMax.to(elm,R(6,15),{y:h+100,ease:Linear.easeNone,repeat:-1,delay:-15});
   TweenMax.to(elm,R(4,8),{x:'+=100',rotationZ:R(0,180),repeat:-1,yoyo:true,ease:Sine.easeInOut});
   TweenMax.to(elm,R(2,8),{rotationX:R(0,360),rotationY:R(0,360),repeat:-1,yoyo:true,ease:Sine.easeInOut,delay:-5});
 };

function R(min,max) {return min+Math.random()*(max-min)};

// Statistics
function update_trash_statistics() {
	$.get("/stats", function(data) {
		d = JSON.parse(data);
		$("#totalImages").text(d.total_images);
		$("#totalLabels").text(d.total_labels);
	});
}

setInterval(update_trash_statistics, 5000);

$(document).ready(update_trash_statistics);