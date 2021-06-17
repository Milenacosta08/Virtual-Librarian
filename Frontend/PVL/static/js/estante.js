// PRÉVIA DA CAPA DO LIVRO DO MODAL
const $ = document.querySelector.bind(document);

const previewImg = $('.previa');
const fileChooser = $('.file-chooser');
const fileButton = $('.file-button');

fileButton.onclick = () => fileChooser.click();

fileChooser.onchange = e => {
    const fileToUpload = e.target.files.item(0);
    const reader = new FileReader();
    reader.onload = e => previewImg.src = e.target.result;
    reader.readAsDataURL(fileToUpload);
};

// PRÉVIA DOS DANOS DO LIVRO
const previewImg2 = $('.previa2');
const fileChooser2 = $('.file-chooser2');
const fileButton2 = $('.file-button2');

fileButton2.onclick = () => fileChooser2.click();

fileChooser2.onchange = e => {
    const fileToUpload2 = e.target.files.item(0);
    const reader2 = new FileReader();
    reader2.onload = e => previewImg2.src = e.target.result;
    reader2.readAsDataURL(fileToUpload2);
};


// EXIBIR CAMPO "PRECO" NO FORMULÁRIO DE CADASTRO DE LIVROS
function showPreco(valor){
    const preco = document.getElementById('preco');
    const dano = document.getElementById('danos');
    const condicao = document.getElementById('condicoes');

	if(valor == "Venda"){
		preco.removeAttribute("hidden");
		dano.removeAttribute("hidden");
		condicao.removeAttribute("hidden");
	}
    else if(valor == "Troca"){
		dano.removeAttribute("hidden");
		condicao.removeAttribute("hidden");
	}
    else{
        preco.setAttribute("hidden", true);
        dano.setAttribute("hidden", true);
        condicao.setAttribute("hidden", true);
    }
}