const productCards = document.querySelectorAll('.product-card');

productCards.forEach(card => {
    card.addEventListener('click', () => {
        console.log(`Producto "${card.dataset.titulo}" clicked!`);
        
    });
});