import 'package:flutter/material.dart';
import 'package:frescapp_web/services/product_service.dart';
import 'package:frescapp_web/screens/cart_screen.dart';
import 'package:frescapp_web/screens/orders_screen.dart';
import 'package:frescapp_web/screens/profile_screen.dart';


class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  // ignore: library_private_types_in_public_api
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
        displayedProducts = products.toList();
      } else {
        displayedProducts = products.where((product) =>
            product.name.toLowerCase().contains(query.toLowerCase()) ||
            product.category.toLowerCase().contains(query.toLowerCase())).toList();
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
      body: SafeArea(
      child: Column(
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
                  onTap: () {
                    // Acción cuando se presiona un producto
                    // Puedes implementar la lógica para mostrar detalles del producto, etc.
                  },
                );
              },
            ),
          ),
        ],
      )
      ),
      bottomNavigationBar: SafeArea(
      child: BottomNavigationBar(
        currentIndex: 0,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Inicio',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.shopping_cart),
            label: 'Pedidos',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Perfil',
          ),
        ],
        onTap: (int index) {
          switch (index) {
            case 0:
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const HomeScreen()),
              );
              break;
            case 1:
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const OrdersScreen()),   
              );           
              break;
            case 2:
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ProfileScreen()),   
              );           
              break;
          }
        },
      ),
      )
    );
  }
}
