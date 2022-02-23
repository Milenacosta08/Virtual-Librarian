$('.carousel-inner img').replaceWith(function(i, v){
    return $('<div/>', {
        style: 'background-image: url(' + this.src + ');' + 
        'width:' + this.width + 'px;' + 
        'height:' + this.height + 'px;' ,
        class: 'fakeImg'
    })
})