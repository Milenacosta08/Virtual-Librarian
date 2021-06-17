function funcao1(){
	let ele = document.getElementById('botao');

  let sim = document.createElement('a');
  sim.id = 'sim';
  sim.innerHTML = 'Sim';
  sim.href = '/delete';


  ele.innerHTML = '';
  ele.appendChild(sim);

  setTimeout(function(){
  	let ele = document.getElementById('botao');
    let sim = document.getElementById('sim');
    sim.remove();
    ele.innerHTML="Excluir";
  }, 5000);
}

//FUNÇÃO QUE REDIRECIONA PARA A ROTA DE APAGAR NOTIFICAÇÕES
function deletNotif(id_noti){
    window.location.href = "/delete/notificacao/"+id_noti;
}