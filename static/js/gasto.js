$(document).on("ready".inicio);
function inicio(){
	//mostrardatos();
	$("form").submit(function(event){
		event.preventDefault();
		$.ajax({
			url:$("form").attr("action"),
			type:$("form").attr("method"),
			type:$("form").serialize(),
			success:function(respuesta){
				alert(respuesta);
			}
		});
	});
}
function mostrardatos(datos) {
    $.ajax({
        url: "../gasto/mostrar_det_gasto", type: 'POST',
        data: $("#form-guardar").serialize(),
        success: function(respuesta) {
            var registro = eval(respuesta);
            html = "<hr><table id='mytable' class='table table-condensed table-bordered table-hover'>";
            html += "<thead><tr>";
            html += "<th class='info'><h5><strong>Tipo Gasto</strong></h5></th>"; 
            html += "<th class='info'><h5><strong>Descripcion</strong></h5></th>"; 
             html += "<th class='info'><h5><strong>Cantidad</strong></h5></th>";  
              html += "<th class='info'><h5><strong>Total</strong></h5></th>";
            html += "<th class='info '><h5><strong>Acciones</strong></th>";
            html += "</thead><tbody>";
            //si hay un registro
            if (registro) {
        	for (var i = 0; i < registro.length; i++) {
            html += "<tr><td>" + registro[i]["tipo_gasto"] + "</td>";
            html += "<td>" + registro[i]["descripcion"] + "</td>";
            html += "<td>" + registro[i]["cantidad"] + "</td>";
            html += "<td>" + registro[i]["monto"] + "</td>";
            html += "<td><button class='btn btn-default glyphicon glyphicon-trash ' name='btn_eliminar'id='btn_eliminar'OnClick='eliminar_det_gasto(this)' type='button' value='" + registro[i]["id_det_gasto"] + "' title='ELiminar Item'></button></td>";
            $("#det_gasto").html(html);
			document.getElementById('txt_cantidad').value = '';
            }
            tabla = document.getElementById("mytable");
            var total = 0;
				for(var i = 1; tabla.rows[i]; i++) {
				total+=Number(tabla.rows[i].cells[3].innerHTML);
				}
			$("#total").html(total);
			document.getElementById("total").value =(total);
			document.getElementById("txt_total_2").value =(total);
            //si no lo hay XD
            }else{
			var total=0;
            	html += "<tr><td></td>";
            	html += "<td></td>";
            	html += "<td></td>";
            	html += "<td></td>";
            	html += "<td></td></tr>";
				$("#total").html(total);
				$("#det_gasto").html(html);
			document.getElementById("txt_total_2").value =(total);
			document.getElementById('txt_cantidad').value = '';

            };
        }
    });
}
function guardar_det_gasto(datos){
	event.preventDefault();
	$.ajax({
		url: "../gasto/guardar_det_gasto_item", type:"POST",
		data: $("#form-guardar").serialize(),
		success:function(respuesta){
		mostrardatos("");
	}
});
}

function eliminar_det_gasto(boton){
	ID=boton.value;
	$.ajax({
		url: "../gasto/eliminar_det_gasto", type:"POST",
		data:{id:ID},
		success:function(respuesta){
			mostrardatos("");
		}
});
}
function eliminar_gasto(boton){
	var respuesta = confirm("Desea Salir?");
	if(respuesta){
	ID=boton.value;
		$.ajax({
				url: "../gasto/eliminar_gasto", type:"POST",
				data:{id:ID},
				success:function(respuesta){
		    	top.location.href="gasto";//redirection }
				}
			});
		}
	}
function cambiar_status_det_instalacion(boton){
	ID=boton.value;
	$.ajax({
		url: "/hotel/cta_corriente/cambiar_status_item_det_cta_corriente",
		type:"POST",
		data:{id:ID},
		success:function(respuesta){
			mostrardatos("");
		}
});
}
