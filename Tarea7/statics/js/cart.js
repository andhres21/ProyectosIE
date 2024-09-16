document.addEventListener('DOMContentLoaded', function() {
    var cartCount = document.getElementById('cart-count');  // El contador del carrito en la esquina superior
    var addToCartButtons = document.querySelectorAll('.add-to-cart');  // Todos los botones de agregar al carrito

    // Agregar evento a todos los botones de "Agregar al carrito"
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();  // Evitar que la página recargue
            var productId = this.getAttribute('data-product-id');  // Obtener el ID del producto
            addToCart(productId);  // Llamar a la función para agregar al carrito
        });
    });

    // Función para agregar un producto al carrito
    function addToCart(productId) {
        var url = '/add_to_cart/';  // La URL del backend para manejar el carrito (modifícala según tu URL)
        var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;  // Obtener el token CSRF

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Incluir el token CSRF para seguridad
            },
            body: JSON.stringify({'product_id': productId})  // Enviar el ID del producto al backend
        })
        .then(response => response.json())
        .then(data => {
            var currentCount = data.cart_count;  // Obtener el nuevo total de productos en el carrito desde el servidor
            cartCount.textContent = currentCount;  // Actualizar el contador en la interfaz
        })
        .catch(error => {
            console.error('Error:', error);  // Mostrar cualquier error en la consola
        });
    }
});
