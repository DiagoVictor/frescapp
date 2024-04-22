import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:frescapp/screens/newOrder/home_screen.dart';
import 'package:frescapp/screens/profile/profile_screen.dart';
import 'package:frescapp/services/order_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:intl/intl.dart';

class OrdersScreen extends StatefulWidget {
  const OrdersScreen({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _OrdersScreenState createState() => _OrdersScreenState();
}

class _OrdersScreenState extends State<OrdersScreen> {
  List<Order> orders = [];
  @override
  void initState() {
    super.initState();
    _fetchOrders();
  }

  void _openWhatsApp() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    String phoneNumber = prefs.getString('contact_phone') ?? '';
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

  Future<void> _fetchOrders() async {
    OrderService orderService = OrderService();
    try {
      final SharedPreferences prefs = await SharedPreferences.getInstance();
      String userEmail = prefs.getString('user_email') ?? '';
      List<Order>? fetchedOrders = await orderService.getOrders(userEmail);
      if (fetchedOrders.isNotEmpty) {
        fetchedOrders.sort((a, b) => b.deliveryDate.compareTo(a.deliveryDate));
        setState(() {
          orders = fetchedOrders;
        });
      } else {
        // Si el servicio retorna null, mostrar mensaje y un ícono
        // ignore: use_build_context_synchronously
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Row(
              children: [
                Icon(Icons.warning),
                SizedBox(width: 8),
                Text('No se ha realizado ningún pedido.'),
              ],
            ),
          ),
        );
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error fetching orders: $e');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pedidos'),
      ),
      body: orders.isEmpty
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.shopping_cart_outlined,
                    size: 48,
                    color: Colors.grey,
                  ),
                  SizedBox(height: 16),
                  Text(
                    "No se ha realizado ningún pedido.",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            )
          : ListView.builder(
              itemCount: orders.length,
              itemBuilder: (context, index) {
                final order = orders[index];
                return Container(
                  margin: const EdgeInsets.symmetric(
                      vertical: 8.0, horizontal: 16.0),
                  padding: const EdgeInsets.all(16.0),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(8.0),
                  ),
                  child: ListTile(
                    title: Text.rich(
                      TextSpan(
                        style: const TextStyle(color: Colors.black87),
                        children: [
                          const TextSpan(
                            text: '# Orden:   ',
                            style: TextStyle(fontWeight: FontWeight.bold),
                          ),
                          TextSpan(text: order.orderNumber),
                        ],
                      ),
                    ),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text.rich(
                          TextSpan(
                            style: const TextStyle(color: Colors.black87),
                            children: [
                              const TextSpan(
                                text: 'Método de Pago: ',
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              TextSpan(text: order.paymentMethod),
                            ],
                          ),
                        ),
                        Text.rich(
                          TextSpan(
                            style: const TextStyle(color: Colors.black87),
                            children: [
                              const TextSpan(
                                text: 'Horario de Entrega: ',
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              TextSpan(text: order.deliverySlot),
                            ],
                          ),
                        ),
                        Text.rich(
                          TextSpan(
                            style: const TextStyle(color: Colors.black87),
                            children: [
                              const TextSpan(
                                text: 'Fecha de Entrega: ',
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              TextSpan(text: order.deliveryDate),
                            ],
                          ),
                        ),
                        Text.rich(
                          TextSpan(
                            style: const TextStyle(color: Colors.black87),
                            children: [
                              const TextSpan(
                                text: 'Cantidad de Productos: ',
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              TextSpan(text: '${order.products.length}'),
                            ],
                          ),
                        ),
                        Text.rich(
                          TextSpan(
                            style: const TextStyle(color: Colors.black87),
                            children: [
                              const TextSpan(
                                text: 'Estado: ',
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              TextSpan(text: order.status),
                            ],
                          ),
                        ),
                        Text.rich(
                          TextSpan(
                            style: const TextStyle(color: Colors.black87),
                            children: [
                              const TextSpan(
                                text: 'Total: \$',
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              TextSpan(text: '${order.total}'),
                            ],
                          ),
                        ),
                      ],
                    ),
                    onTap: () {
                      showDialog(
                        context: context,
                        builder: (BuildContext context) {
                          return AlertDialog(
                            title: const Text('Detalle de la Orden'),
                            content: SizedBox(
                              height: 300,
                              width: double.maxFinite,
                              child: ListView(children: [
                                Text('# Orden: ${order.orderNumber}'),
                                Text('Método de Pago: ${order.paymentMethod}'),
                                Text('Horario de Entrega: ${order.deliverySlot}'),
                                Text('Fecha de Entrega: ${order.deliveryDate}'),
                                Text(
                                    'Total: \$ ${NumberFormat('#,###').format(order.total)}'),
                                ListView.builder(
                                    shrinkWrap: true,
                                    itemCount: order.products.length,
                                    itemBuilder: (context, index) {
                                      final List<Map> product =
                                          order.products.cast<Map>();
                                      return ListTile(
                                          title: RichText(
                                            text: TextSpan(
                                              children: [
                                                TextSpan(
                                                  text:
                                                      '${product[index]["name"]}',
                                                  style: const TextStyle(
                                                      fontWeight:
                                                          FontWeight.normal),
                                                ),
                                                const TextSpan(
                                                  text: '\nPrecio: ',
                                                  style: TextStyle(
                                                      fontWeight:
                                                          FontWeight.bold),
                                                ),
                                                TextSpan(
                                                  text:
                                                      '\$ ${NumberFormat('#,###').format(product[index]["price_sale"])}',
                                                  style: const TextStyle(
                                                      fontWeight:
                                                          FontWeight.normal),
                                                ),
                                              ],
                                            ),
                                          ),
                                          subtitle: RichText(
                                              text: TextSpan(children: [
                                            const TextSpan(
                                              text: 'Cantidad: ',
                                              style: TextStyle(
                                                  fontWeight: FontWeight.bold),
                                            ),
                                            TextSpan(
                                                text: product[index]["quantity"].toString()),
                                          ])));
                                    }),
                              ]),
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
                  ),
                );
              },
            ),
      bottomNavigationBar: SafeArea(
        child: BottomNavigationBar(
          currentIndex: 1,
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
