import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:frescapp_web/services/product_service.dart';
import 'package:frescapp_web/screens/newOrder/cart_screen.dart';
import 'package:frescapp_web/screens/orders/orders_screen.dart';
import 'package:frescapp_web/screens/profile/profile_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:frescapp_web/services/config_service.dart';
import 'package:http/http.dart' as http;

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ProductService productService = ProductService();
  late List<Product> displayedProducts = [];
  late List<Product> allProducts =
      []; // Mantener una lista de todos los productos
  late List<Product> productsInCart = []; // Lista de productos en el carrito
  late String userAddress = ''; // Correo electrónico del usuario
  late int productCounter = 0; // Contador de productos

  @override
  void initState() {
    super.initState();
    getUserInfo();
    getInitialProducts();
  }

ConfigService configService = ConfigService(http.Client());

Future<void> getUserInfo() async {
  final SharedPreferences prefs = await SharedPreferences.getInstance();
  try {
    // Obtiene los datos de configuración
    final Map<String, dynamic> configData = await configService.getConfigData();
    // Guarda los datos de configuración en SharedPreferences
    prefs.setString('delivery_cost', configData['delivery_cost'] ?? '0');
    prefs.setStringList('delivery_slots', List<String>.from(configData['delivery_slots'] ?? []));
    prefs.setStringList('payments_method', List<String>.from(configData['payments_method'] ?? []));
    prefs.setStringList('document_type', List<String>.from(configData['document_type'] ?? []));
    prefs.setString('contact_phone', configData['contact_phone'] ?? '');
    setState(() {
      userAddress = prefs.getString('user_address') ?? '';
    });
  } catch (e) {
    if (kDebugMode) {
      print('Error al obtener los datos de configuración: $e');
    }
  }
}

  Future<void> getInitialProducts() async {
    allProducts =
        await productService.getProducts(); // Obtener todos los productos
    for (var product in allProducts) {
      product.quantity = 0;
    }
    setState(() {
      displayedProducts =
          allProducts.toList(); // Mostrar todos los productos inicialmente
    });
  }

  void filterProducts(String query) {
    setState(() {
      if (query.isEmpty) {
        displayedProducts = allProducts
            .toList(); // Mostrar todos los productos si la consulta está vacía
      } else {
        displayedProducts = allProducts
            .where((product) =>
                product.name.toLowerCase().contains(query.toLowerCase()) ||
                product.category.toLowerCase().contains(query.toLowerCase()))
            .toList();
      }
    });
  }

  void increaseQuantity(Product product) {
    setState(() {
      product.quantity = (product.quantity! + 1);
      productCounter++;
      if (!productsInCart.contains(product)) {
        productsInCart
            .add(product); // Agregar el producto al carrito si no está presente
      }
    });
  }

  void decreaseQuantity(Product product) {
    setState(() {
      if (product.quantity! > 0) {
        product.quantity = product.quantity! - 1;
        productCounter--;
        if (product.quantity == 0) {
          productsInCart.remove(
              product); // Eliminar el producto del carrito si la cantidad es cero
        }
      }
    });
  }

  void updateCounter(int value) {
    setState(() {
      productCounter = value;
    });
  }

  void _openWhatsApp() async {
    // Número de teléfono al que se enviará el mensaje
    String phoneNumber = '+573115455042';
    // Construir la URL para abrir WhatsApp
    String url = 'https://wa.me/$phoneNumber';
    // Abrir la URL en una ventana externa (aplicación de WhatsApp)
    // ignore: deprecated_member_use
    if (await canLaunch(url)) {
      // ignore: deprecated_member_use
      await launch(url);
    } else {
      // Manejar el caso en el que WhatsApp no esté instalado
      // ignore: use_build_context_synchronously
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No se pudo abrir WhatsApp.'),
        ),
      );
    }
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
                  builder: (context) => CartScreen(
                      productsInCart: productsInCart,
                      updateCounter: updateCounter),
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
                          TextSpan(
                              text: '${product.name} - ',
                              style: const TextStyle(
                                  fontWeight: FontWeight.normal)),
                          TextSpan(
                              text:
                                  '\n \$ ${NumberFormat('#,###').format(product.price_sale)}',
                              style:
                                  const TextStyle(fontWeight: FontWeight.bold)),
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
                              decreaseQuantity(product);
                            });
                          },
                        ),
                        Text(product.quantity.toString()),
                        IconButton(
                          icon: const Icon(Icons.add),
                          onPressed: () {
                            setState(() {
                              increaseQuantity(product);
                            });
                          },
                        ),
                      ],
                    ),
                    onTap: () {
                      showDialog(
                        context: context,
                        builder: (context) {
                          return StatefulBuilder(
                            builder:
                                (BuildContext context, StateSetter setState) {
                              return AlertDialog(
                                title: Text(product.name,
                                    style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 18),
                                    textAlign: TextAlign.center),
                                content: Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Image.network(
                                      product.image,
                                      height: 200,
                                      width: 200,
                                    ),
                                    const SizedBox(height: 20),
                                    Text(product.name,
                                        style: const TextStyle(
                                            fontWeight: FontWeight.bold),
                                        textAlign: TextAlign.center),
                                    Text(
                                      ' \$  ${NumberFormat('#,###').format(product.price_sale)}',
                                      style: const TextStyle(
                                          fontWeight: FontWeight.bold),
                                      textAlign: TextAlign.center,
                                    ),
                                    Text(product.category,
                                        style: const TextStyle(
                                            fontWeight: FontWeight.bold),
                                        textAlign: TextAlign.center),

                                    Row(
                                      mainAxisAlignment:
                                          MainAxisAlignment.center,
                                      children: [
                                        IconButton(
                                          icon: const Icon(Icons.remove),
                                          onPressed: () {
                                            setState(() {
                                              decreaseQuantity(product);
                                            });
                                          },
                                        ),
                                        Text(product.quantity.toString()),
                                        IconButton(
                                          icon: const Icon(Icons.add),
                                          onPressed: () {
                                            setState(() {
                                              increaseQuantity(product);
                                            });
                                          },
                                        ),
                                      ],
                                    ),
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
          selectedItemColor:
              Colors.lightGreen.shade900, // Color de los iconos seleccionados
          unselectedItemColor:
              Colors.grey, // Color de los iconos no seleccionados
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
            BottomNavigationBarItem(
              icon: Icon(Icons.message_rounded), // Icono de WhatsApp
              label: 'WhatsApp', // Etiqueta para el botón
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
                  MaterialPageRoute(
                      builder: (context) => const ProfileScreen()),
                );
                break;
              case 3:
                _openWhatsApp(); // Función para abrir WhatsApp
                break;
            }
          },
        ),
      ),
    );
  }
}
