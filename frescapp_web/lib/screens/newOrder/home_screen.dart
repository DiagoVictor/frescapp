import 'package:flutter/material.dart';
import 'package:frescapp_web/services/product_service.dart';
import 'package:frescapp_web/screens/newOrder/cart_screen.dart';
import 'package:frescapp_web/screens/orders/orders_screen.dart';
import 'package:frescapp_web/screens/profile/profile_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ProductService productService = ProductService();
  late List<Product> displayedProducts = [];
  late List<Product> allProducts = []; // Mantener una lista de todos los productos
  late List<Product> productsInCart = []; // Lista de productos en el carrito
  late String userAddress = ''; // Correo electrónico del usuario
  late int productCounter = 0; // Contador de productos

  @override
  void initState() {
    super.initState();
    getUserInfo();
    getInitialProducts();
  }

  Future<void> getUserInfo() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    setState(() {
      userAddress = prefs.getString('user_address') ?? '';
    });
  }

  Future<void> getInitialProducts() async {
    allProducts = await productService.getProducts(); // Obtener todos los productos
    for (var product in allProducts) {
      product.quantity = 0;
    }
    setState(() {
      displayedProducts = allProducts.toList(); // Mostrar todos los productos inicialmente
    });
  }

  void filterProducts(String query) {
    setState(() {
      if (query.isEmpty) {
        displayedProducts = allProducts.toList(); // Mostrar todos los productos si la consulta está vacía
      } else {
        displayedProducts = allProducts.where((product) =>
            product.name.toLowerCase().contains(query.toLowerCase()) ||
            product.category.toLowerCase().contains(query.toLowerCase())).toList();
      }
    });
  }

  void increaseQuantity(Product product) {
    setState(() {
      product.quantity = (product.quantity! + 1);
      productCounter++;
      if (!productsInCart.contains(product)) {
        productsInCart.add(product); // Agregar el producto al carrito si no está presente
      }
    });
  }

  void decreaseQuantity(Product product) {
    setState(() {
      if (product.quantity! > 0) {
        product.quantity = product.quantity! - 1;
        productCounter--;
        if (product.quantity == 0) {
          productsInCart.remove(product); // Eliminar el producto del carrito si la cantidad es cero
        }
      }
    });
  }

  void updateCounter(int value) {
    setState(() {
      productCounter = value;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(userAddress), // Usar el nombre dinámico del app bar
        actions: [
          IconButton(
            icon: const Icon(Icons.shopping_cart),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => CartScreen(productsInCart: productsInCart, updateCounter: updateCounter),
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
                      backgroundImage: NetworkImage(product.image),
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
                          onPressed: () => decreaseQuantity(product),
                        ),
                        Text(product.quantity.toString()),
                        IconButton(
                          icon: const Icon(Icons.add),
                          onPressed: () => increaseQuantity(product),
                        ),
                      ],
                    ),
                    onTap: () {
                      showDialog(
                        context: context,
                        builder: (context) {
                          return AlertDialog(
                            title: Text(product.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                            content: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Image.network(
                                  product.image,
                                  height: 200,
                                  width: 200,
                                ),
                                const SizedBox(height: 20),
                                Text('Nombre: ${product.name}', style: const TextStyle(fontWeight: FontWeight.bold)),
                                Text('Precio: \$${product.price_sale}', style: const TextStyle(fontWeight: FontWeight.bold)),
                                Text('Categoría: ${product.category}', style: const TextStyle(fontWeight: FontWeight.bold)),
                                // Agregar más atributos aquí según sea necesario
                              ],
                            ),
                            actions: [
                              TextButton(
                                onPressed: () {
                                  Navigator.of(context).pop();
                                },
                                child: const Text('Cerrar'),
                              ),
                            ],
                          );
                        },
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
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
      ),
    );
  }
}
