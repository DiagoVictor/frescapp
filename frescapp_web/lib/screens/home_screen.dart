import 'package:flutter/material.dart';
import 'package:frescapp_web/services/product_service.dart'; // Importa el archivo donde se define ProductService

class HomeScreen extends StatelessWidget {
  final ProductService productService = ProductService(); // Instancia ProductService

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dirección de entrega'),
        actions: [
          IconButton(
            icon: const Icon(Icons.shopping_cart),
            onPressed: () {
              // Acción cuando se presiona el ícono del carrito
              // Aquí puedes redirigir al usuario al carrito de compras
            },
          ),
        ],
      ),
      body: FutureBuilder<List<Product>>(
        future: productService.getProducts(), // Llama al método getProducts para obtener la lista de productos
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator()); // Muestra un indicador de carga mientras se obtienen los productos
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}')); // Muestra un mensaje de error si ocurre algún problema
          } else {
            List<Product> products = snapshot.data!; // Obtiene la lista de productos del snapshot
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Padding(
                  padding: EdgeInsets.all(10),
                  child: TextField(
                    decoration: InputDecoration(
                      hintText: 'Buscar productos...',
                      prefixIcon: Icon(Icons.search),
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                Expanded(
                  child: ListView.builder(
                    itemCount: products.length, // Usa la longitud de la lista de productos
                    itemBuilder: (context, index) {
                      Product product = products[index]; // Obtiene el producto en el índice actual
                      return ListTile(
                        leading: CircleAvatar(
                          backgroundColor: Colors.white,
                          backgroundImage: AssetImage('products/${product.sku}.png'), // Ejemplo: imagen del producto
                        ),
                        title: RichText(
                          text: TextSpan(
                            children: [
                              TextSpan(text: '${product.name} - ', style: const TextStyle(fontWeight: FontWeight.normal)),
                              TextSpan(text: '\$ ${product.price_sale.toStringAsFixed(0)}', style: const TextStyle(fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ),
                        subtitle: Text(product.category), // Usa la categoría del producto
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.remove),
                              onPressed: () {
                                // Acción cuando se presiona el botón de disminuir cantidad
                                // Puedes implementar la lógica para disminuir la cantidad del producto
                              },
                            ),
                            const Text('1'), // Ejemplo: cantidad del producto
                            IconButton(
                              icon: const Icon(Icons.add),
                              onPressed: () {
                                // Acción cuando se presiona el botón de aumentar cantidad
                                // Puedes implementar la lógica para aumentar la cantidad del producto
                              },
                            ),
                          ],
                        ),
                        onTap: () {
                          // Acción cuando se presiona un producto
                          // Puedes implementar la lógica para mostrar detalles del producto, etc.
                        },
                      );
                    },
                  ),
                ),
              ],
            );
          }
        },
      ),
    );
  }
}
