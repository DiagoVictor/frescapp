import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:frescapp_web/screens/newOrder/home_screen.dart';
import 'package:frescapp_web/screens/profile/profile_screen.dart';
import 'package:frescapp_web/services/order_service.dart';
import 'package:frescapp_web/services/product_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

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

  Future<void> _fetchOrders() async {
    OrderService orderService = OrderService();
    try {
      final SharedPreferences prefs = await SharedPreferences.getInstance();
      late String userEmail = prefs.getString('user_email') ?? '';
      List<Order> fetchedOrders = await orderService.getOrders(userEmail);
      setState(() {
        orders = fetchedOrders;
      });
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
              child: CircularProgressIndicator(),
            )
          : ListView.builder(
              itemCount: orders.length,
              itemBuilder: (context, index) {
                final order = orders[index];
                return Container(
                  margin: const EdgeInsets.symmetric(
                      vertical: 8.0,
                      horizontal: 16.0), // Margen entre cada elemento

                  padding:
                      const EdgeInsets.all(16.0), // Espaciado interno del contenedor
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius:
                        BorderRadius.circular(8.0), // Bordes redondeados
                  ),

                  child: ListTile(
                    title: Text.rich(                          TextSpan(
                            style: const TextStyle(color: Colors.black87),
                            children: [
                              const TextSpan(
                                text:'Número de Orden:',
                              style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              TextSpan(text: order.orderNumber),
                            ],
                    )
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
                                text: 'Slot de Entrega: ',
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
                      // Mostrar detalles de la orden en una modal
                      showDialog(
                        context: context,
                        builder: (BuildContext context) {
                          return AlertDialog(
                            title: const Text('Detalle de la Orden'),
                            content: SizedBox(
                              height: 300, // Altura fija de la modal
                              width: double.maxFinite, // Ancho máximo
                              child: ListView(
                                children: [
                                  // Mostrar los detalles de la orden aquí
                                  Text('Order Number: ${order.orderNumber}'),
                                  Text(
                                      'Método de Pago: ${order.paymentMethod}'),
                                  Text(
                                      'Slot de Entrega: ${order.deliverySlot}'),
                                  Text(
                                      'Fecha de Entrega: ${order.deliveryDate}'),
                                  Text('Total: \$${order.total}'),
                                  // También puedes mostrar la lista de productos
                                  ListView.builder(
                                    shrinkWrap: true,
                                    itemCount: order.products.length,
                                    itemBuilder: (context, index) {
                                      final Product product =
                                          order.products[index] as Product;
                                      return Container(
                                        margin: const EdgeInsets.symmetric(
                                            vertical:
                                                8.0), // Margen entre cada elemento
                                        padding: const EdgeInsets.all(
                                            8.0), // Espaciado interno del contenedor
                                        decoration: BoxDecoration(
                                          color: Colors.lightGreen[
                                              100], // Fondo verde claro
                                          borderRadius: BorderRadius.circular(
                                              8.0), // Bordes redondeados
                                        ),
                                        child: ListTile(
                                          title:
                                              Text('Producto: ${product.name}'),
                                          subtitle: Text(
                                              'Precio: \$${product.price_sale}'),
                                          leading: Image.network(product.image),
                                        ),
                                      );
                                    },
                                  ),
                                ],
                              ),
                            ),
                            actions: [
                              TextButton(
                                onPressed: () {
                                  Navigator.of(context)
                                      .pop(); // Cerrar la modal
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
                  MaterialPageRoute(
                      builder: (context) => const ProfileScreen()),
                );
                break;
            }
          },
        ),
      ),
    );
  }
}
