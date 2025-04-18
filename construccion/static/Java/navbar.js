//ocultar los menu al momento de pasar a mobile
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');

    menuToggle.addEventListener('click', function() {
        mobileMenu.classList.toggle('hidden');
    });
});


$(document).ready(function() {
    let currentItem = 0;
    const items = $('.carousel-item');
    const itemCount = items.length;

    function switchItem() {
        items.eq(currentItem).removeClass('active').addClass('inactive');

        currentItem = (currentItem + 1) % itemCount;

        items.eq(currentItem).removeClass('inactive').addClass('active');
    }

    // Iniciar el carrusel
    let carouselInterval = setInterval(switchItem, 5000); // Cambia cada 5 segundos

    // Controles (Opcional)
    $('.carousel-control-next').click(function() {
        clearInterval(carouselInterval);
        switchItem();
        carouselInterval = setInterval(switchItem, 5000);
    });

    $('.carousel-control-prev').click(function() {
        clearInterval(carouselInterval);
        currentItem = (currentItem - 1 + itemCount) % itemCount;
        switchItem();
        carouselInterval = setInterval(switchItem, 5000);
    });
});