$("#toLogin").click(function(){
	$("#register").modal("hide");
	$("#register").on("hidden.bs.modal",function(){
		$("#login").modal("show");
		$("#register").off().on("hidden","hidden.bs.modal");
	})
})

$("#toReg").click(function(){
	$("#login").modal("hide");
	$("#login").on("hidden.bs.modal",function(){
		$("#register").modal("show");
		$("#login").off().on("hidden","hidden.bs.modal");
	})
})

function toLogin(){
	// $("#register").modal("hide");
	$("#register").modal("hide");
	$("#register").on("hidden.bs.modal",function(){
		$("#login").modal("show");
		$("#register").off().on("hidden","hidden.bs.modal");
	})
}

function toReg(){
	$("#login").modal("hide");
	$("#login").on("hidden.bs.modal",function(){
		$("#register").modal("show");
		$("#login").off().on("hidden","hidden.bs.modal");
	})
}


		


