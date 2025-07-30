const url = "/api/productos";
const url_img = "static/img/";

function validarIngreso(){
    const usuario = prompt("Ingrese usuario administrador");
    const pwd = prompt("Ingrese contraseña");

    if(usuario == "flory123" && pwd=="romero456"){
        alert("Bienvenido admin - podrás ingresar, ver, eliminar y editar información desde aqui")
        window.location.replace("/admin");
    }else{
        alert("Datos incorrectos...");
    }
}

async function cargarProductos() {
    const res = await fetch(url);
    const productos = await res.json();

    let txtTabla_e = "<table class='table table-secondary table-striped-columns mt-3 container'><th>Nombre</th><th>Precio</th><th>Descripcion</th><th>Categoria</th><th>Imagen</th><th>Eliminar</th><th>Editar</th>";
    let txtTabla_b = "";
    productos.forEach(p => {
         txtTabla_b += `<tr><td>${p.nombre}</td><td>${p.precio}</td><td>${p.desc}</td><td>${p.categoria}</td><td><img src="${url_img + p.imagen}" width="50px"> </td><td><button onclick="eliminar(${p.id})" class="btn btn-danger" style="margin: 2px"><i class="bi bi-trash"></i></button></td><td><button onclick="editar(${p.id}, '${p.nombre}', ${p.precio}, '${p.desc}', '${p.categoria}','${p.imagen}')" class="btn btn-warning" style="margin: 2px"><i class="bi bi-pencil-square"></i></button></td></tr>`;       
    });
    txtTabla_b += "</table>";
    document.getElementById("tabla").innerHTML = txtTabla_e + txtTabla_b;
}



async function eliminar(id){
    await fetch(`${url}/${id}`, {method: "DELETE"});
    cargarProductos();

}

async function editar(id, nombreViejo, precioViejo, descripcionVieja, categoriaVieja, imagenVieja){
 
     const nombre = prompt("Nuevo nombre: ",nombreViejo);
     const precio = prompt("Nuevo precio: ",precioViejo);
     const desc = prompt("Nueva descripcion: ",descripcionVieja);
     const categoria = prompt("Nueva Categoria: ",categoriaVieja).toLowerCase();
     const imagen = prompt("Nueva imagen: ",imagenVieja);

     if(nombre && precio && desc && categoria  && imagen ){
        await fetch(`${url}/${id}`,{
            method: "PUT",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({nombre, precio: parseFloat(precio), desc, categoria, imagen})
        });
     }else{
        alert("Ningun campo puede quedar vacio.. no se realizó el cambio");
     }
     cargarProductos();
}

document.getElementById("formulario").addEventListener("submit", async e=>{
    e.preventDefault();
    const nombre = document.getElementById("nombre").value;
    const precio = document.getElementById("precio").value;
    const desc = document.getElementById("descripcion").value;
    const categoria = document.getElementById("categoria").value;
    const imagen = document.getElementById("imagen").value;

    await fetch (url, {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({nombre, precio: parseFloat(precio), desc, categoria, imagen})
    });
    e.target.reset();
    cargarProductos();
}

);