import 'package:flutter/material.dart';
import 'package:frescapp_web/services/product_service.dart';
import 'package:frescapp_web/screens/cart_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ProductService productService = ProductService();
  late List<Product> displayedProducts = [];
  late List<Product> products = [];
  @override
  void initState() {
    super.initState();
    getInitialProducts();
  }

  Future<void> getInitialProducts() async {
    products = await productService.getProducts();
      for (var product in products) {
        product.quantity = 0;
      }
    setState(() {
      displayedProducts = products;
    });
  }

void filterProducts(String query) {
  setState(() {
    if (query.isEmpty) {
      // Si la consulta está vacía, muestra todos los productos
      displayedProducts = products.toList();
    } else {
      // Filtra los productos por nombre o categoría según la consulta
      displayedProducts = products.where((product) =>
        product.name.toLowerCase().contains(query.toLowerCase()) ||
        product.category.toLowerCase().contains(query.toLowerCase())
      ).toList();
    }
  });
}
  void increaseQuantity(Product product) {
    setState(() {
      product.quantity = (product.quantity! + 1);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dirección de entrega'),
        actions: [
          IconButton(
            icon: const Icon(Icons.shopping_cart),
            onPressed: () {
               Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => CartScreen(productsInCart: displayedProducts),
                  ),
                );
            },
          ),
        ],
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.all(10),
            child: TextField(
              onChanged: filterProducts,
              decoration: const InputDecoration(
                hintText: 'Buscar productos...',
                prefixIcon: Icon(Icons.search),
                border: OutlineInputBorder(),
              ),
            ),
          ),
          Expanded(
            child: ListView.builder(
              itemCount: displayedProducts.length,
              itemBuilder: (context, index) {
                final product = displayedProducts[index];
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

                  // Aquí puedes agregar más detalles del producto si lo deseas
                  onTap: () {
                    // Acción cuando se presiona un producto
                    // Puedes implementar la lógica para mostrar detalles del producto, etc.
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
