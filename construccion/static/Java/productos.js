const vendidoCards = document.querySelectorAll('.vendidos-card');

vendidoCards.forEach(card => {
    card.addEventListener('click', () => {
        console.log(`vendido "${card.dataset.titulo}" clicked!`);
        
    });
});