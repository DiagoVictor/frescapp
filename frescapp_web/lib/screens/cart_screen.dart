import 'package:flutter/material.dart';
import 'package:frescapp_web/services/product_service.dart';
import 'package:frescapp_web/screens/detailCart_screen.dart';
class CartScreen extends StatefulWidget {
  final List<Product> productsInCart;

  const CartScreen({Key? key, required this.productsInCart}) : super(key: key);
  
  get total => null;

  @override
  // ignore: library_private_types_in_public_api
  _CartScreenState createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  @override
  Widget build(BuildContext context) {
    // Filtra los productos con una cantidad mayor a cero
    final List<Product> productsWithQuantity = widget.productsInCart.where((product) => product.quantity! > 0).toList();

    // Calcula el total del pedido
    double total = 0;
    for (var product in productsWithQuantity) {
      total += product.quantity! * product.price_sale; // Multiplica la cantidad por el precio de venta y lo suma al total
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Tu Pedido'),
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            ListView.builder(
              shrinkWrap: true,
              itemCount: productsWithQuantity.length,
              itemBuilder: (context, index) {
                final Product product = productsWithQuantity[index];
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Colors.white,
                    backgroundImage: NetworkImage(product.image), // Ejemplo: imagen del producto
                  ),
                  title: RichText(
                    text: TextSpan(
                      children: [
                        TextSpan(text: '${product.name} - ', style: const TextStyle(fontWeight: FontWeight.normal)),
                        TextSpan(text: '\n \$ ${product.price_sale.toStringAsFixed(0)}', style: const TextStyle(fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ),
                  subtitle: Text(product.category),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.remove),
                        onPressed: () {
                          setState(() {
                            if (product.quantity! > 0) {
                              product.quantity = product.quantity! - 1; // Disminuye la cantidad del producto
                            }
                          });
                        },
                      ),
                      Text(product.quantity.toString()), // Muestra la cantidad del producto
                      IconButton(
                        icon: const Icon(Icons.add),
                        onPressed: () {
                          setState(() {
                            product.quantity = product.quantity! + 1; // Aumenta la cantidad del producto
                          });
                        },
                      ),
                    ],
                  ),
                );
              },
            ),
            // Muestra el total del pedido
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                'Total: \$ $total',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ),
            // Botón para confirmar el pedido
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: ElevatedButton(
                onPressed: () {
                  Navigator.push(
                        context,
                        MaterialPageRoute(
                              builder: (context) => OrderDetailScreen(productsInCart: productsWithQuantity),
                        ),
                      );                },
                child: const Text('Confirmar Pedido'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
