import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:frescapp/screens/newOrder/home_screen.dart';
import 'package:frescapp/screens/orders/orders_screen.dart';
import 'package:frescapp/screens/profile/profile_screen.dart';
import 'package:frescapp/models/product.dart' ;
import 'package:frescapp/screens/newOrder/detail_cart_screen.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher_string.dart';
import 'package:frescapp/models/order.dart' as orden;

class CartScreen extends StatefulWidget {
  final List<Product> productsInCart;
  final orden.Order order;

  const CartScreen(
      {super.key,
      required this.productsInCart,
      required void Function(int value) updateCounter, required this.order}
      );

  @override
  // ignore: library_private_types_in_public_api
  _CartScreenState createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  void _openWhatsApp(BuildContext context) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    try {
      String name = prefs.getString('user_name') ?? '';
      String email = prefs.getString('user_email') ?? '';
      String phone = prefs.getString('user_phone') ?? '';
      String contactPhone = prefs.getString('contact_phone') ?? '';

      String message =
          'Hola, soy $name y mis datos son:\nEmail: $email\nTeléfono: $phone. Tengo la siguiente duda.';

      // Codificar el mensaje para que se pueda enviar correctamente en la URL
      String encodedMessage = Uri.encodeComponent(message);

      // Construir la URL para abrir WhatsApp con el mensaje predefinido
      String url = 'whatsapp://send?phone=$contactPhone&text=$encodedMessage';

      // Lanzar la URL para abrir WhatsApp
      await launchUrlString(url);
    } catch (error) {
      if (kDebugMode) {
        print('Error opening WhatsApp: $error');
      }
      // ignore: use_build_context_synchronously
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Error al abrir WhatsApp.'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    // Filtra los productos con una cantidad mayor a cero
    final List<Product> productsWithQuantity = widget.productsInCart 
        .where((product) => product.quantity! > 0).cast<Product>()
        .toList();

    // Calcula el total del pedido
    double total = 0;
    for (var product in productsWithQuantity) {
      total += product.quantity! *
          product.priceSale!; // Multiplica la cantidad por el precio de venta y lo suma al total
    }    return Scaffold(
      appBar: AppBar(
        title: const Text('Tu Pedido'),
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            ListView.builder(
              shrinkWrap: true,
              physics:
                  const NeverScrollableScrollPhysics(), // Para evitar que el ListView ocupe todo el espacio disponible
              itemCount: productsWithQuantity.length,
              itemBuilder: (context, index) {
                final Product product = productsWithQuantity[index];
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Colors.white,
                    backgroundImage: NetworkImage(
                        product.image ?? ''), // Ejemplo: imagen del producto
                  ),
                  title: RichText(
                    text: TextSpan(
                      children: [
                        TextSpan(
                            text: '${product.name ?? ''} - ',
                            style: const TextStyle(
                                fontWeight: FontWeight.normal,
                                color: Colors.black)),
                        TextSpan(
                            text:
                                '\nPrecio \$ ${NumberFormat('#,###').format(product.priceSale ?? 0)}',
                            style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.black)),
                        TextSpan(
                            text:
                                '\nSubtotal \$ ${NumberFormat('#,###').format((product.priceSale ?? 0) * (product.quantity ?? 0))}',
                            style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.black))
                      ],
                    ),
                  ),
                  subtitle: Text(product.category ?? ''),
                  onTap: () {
                    showDialog(
                     context: context,
                      builder: (context) {
                        return StatefulBuilder(
                          builder:
                              (BuildContext context, StateSetter setState) {
                            return AlertDialog(
                              title: Text(product.name as String,
                                  style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 18),
                                  textAlign: TextAlign.center),
                              content: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Image.network(
                                    product.image as String,
                                    height: 200,
                                    width: 200,
                                  ),
                                  const SizedBox(height: 20),
                                  Text(product.name as String,
                                      style: const TextStyle(
                                          fontWeight: FontWeight.bold),
                                      textAlign: TextAlign.center),
                                  Text(
                                    ' \$  ${NumberFormat('#,###').format(product.priceSale)}',
                                    style: const TextStyle(
                                        fontWeight: FontWeight.bold),
                                    textAlign: TextAlign.center,
                                  ),
                                  Text(product.category as String,
                                      style: const TextStyle(
                                          fontWeight: FontWeight.bold),
                                      textAlign: TextAlign.center),
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
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(
                        icon: const Icon(Icons.remove),
                        onPressed: () {
                          setState(() {
                            if (product.quantity! > 0) {
                              product.quantity = product.quantity! -
                                  1; // Disminuye la cantidad del producto
                            }
                          });
                        },
                      ),
                      Text(product.quantity
                          .toString()), // Muestra la cantidad del producto
                      IconButton(
                        icon: const Icon(Icons.add),
                        onPressed: () {
                          setState(() {
                            product.quantity = product.quantity! +
                                1; // Aumenta la cantidad del producto
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
                'Total: \$ ${NumberFormat('#,###').format(total)}',
                style:
                    const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
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
                      builder: (context) => OrderDetailScreen(
                          productsInCart: productsWithQuantity,
                          order : widget.order),
                    ),
                  );
                },
                child: const Text('Confirmar Pedido'),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
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
            icon: Icon(Icons.chat), // Icono de WhatsApp
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
                MaterialPageRoute(builder: (context) => const ProfileScreen()),
              );
              break;
            case 3:
              _openWhatsApp(context); // Función para abrir WhatsApp
              break;
          }
        },
      ),
    );
  }
}
