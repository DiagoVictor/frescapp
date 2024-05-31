import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:frescapp/screens/newOrder/home_screen.dart';
import 'package:frescapp/screens/profile/profile_screen.dart';
import 'package:frescapp/services/order_service.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher_string.dart';
import 'package:intl/intl.dart';
import 'package:advance_pdf_viewer/advance_pdf_viewer.dart';


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

  void _openWhatsApp(BuildContext context) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    try {
      String name = prefs.getString('user_name') ?? '';
      String email = prefs.getString('user_email') ?? '';
      String phone = prefs.getString('user_phone') ?? '';
      String contactPhone = prefs.getString('contact_phone') ?? '';

      String message = 'Hola, soy $name y mis datos son:\nEmail: $email\nTeléfono: $phone. Tengo la siguiente duda.';

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

  // ignore: unused_element
void _viewPDF(BuildContext context, String url) {
  Navigator.push(
    context,
    MaterialPageRoute(
      builder: (context) => PDFViewerScreen(url: url),
    ),
  );
}
  void _editOrder(BuildContext context, Order order) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EditOrderScreen(order: order),
      ),
    );
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
                          TextSpan(
                            text: 'Pedido: ${index + 1} \n', // Añadir el índice
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          const TextSpan(
                            text: 'Número de Orden:   ',
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
                                text: 'Fecha de Creación: ',
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              TextSpan(
                                text: DateFormat('yyyy-MM-dd hh:mm a').format(DateTime.parse(order.createdAt)),
                              ),
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
                                text: 'Total: ',
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              TextSpan(
                                  text:
                                      '\$ ${NumberFormat('#,###').format(order.total)}'),
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
                            content: SingleChildScrollView(
                              child: SizedBox(
                                height: 500,
                                width: double.maxFinite,
                                child: SingleChildScrollView(
                                  child: Column(
                                    children: [
                                      Text('# Orden: ${order.orderNumber}'),
                                      Text('Método de Pago: ${order.paymentMethod}'),
                                      Text('Horario de Entrega: ${order.deliverySlot}'),
                                      Text('Fecha de Entrega: ${order.deliveryDate}'),
                                      Text('Total: \$ ${NumberFormat('#,###').format(order.total)}'),
                                      ListView.builder(
                                        shrinkWrap: true,
                                        physics: const NeverScrollableScrollPhysics(),
                                        itemCount: order.products.length,
                                        itemBuilder: (context, index) {
                                          final List<Map> product = order.products.cast<Map>();
                                          return ListTile(
                                            title: RichText(
                                              text: TextSpan(
                                                children: [
                                                  TextSpan(
                                                    text: '${product[index]["name"]}',
                                                    style: const TextStyle(
                                                      fontWeight: FontWeight.normal,
                                                      color: Colors.black,
                                                    ),
                                                  ),
                                                  const TextSpan(
                                                    text: '\nPrecio: ',
                                                    style: TextStyle(
                                                      fontWeight: FontWeight.bold,
                                                      color: Colors.black,
                                                    ),
                                                  ),
                                                  TextSpan(
                                                    text: '\$ ${NumberFormat('#,###').format(product[index]["price_sale"])}',
                                                    style: const TextStyle(
                                                      fontWeight: FontWeight.normal,
                                                      color: Colors.black,
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ),
                                            subtitle: RichText(
                                              text: TextSpan(
                                                children: [
                                                  const TextSpan(
                                                    text: 'Cantidad: ',
                                                    style: TextStyle(
                                                      fontWeight: FontWeight.bold,
                                                      color: Colors.black,
                                                    ),
                                                  ),
                                                  TextSpan(
                                                    text: product[index]["quantity"].toString(),
                                                    style: const TextStyle(
                                                      color: Colors.black,
                                                    ),
                                                  ),
                                                  TextSpan(
                                                    text: '\nSubtotal \$ ${NumberFormat('#,###').format((product[index]["price_sale"] ?? 0) * (product[index]["quantity"] ?? 0))}',
                                                    style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.black)
                                                  ),
                                                ],
                                              ),
                                            ),
                                          );
                                        },
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                            actions: [
                              TextButton(
                                onPressed: () {
                                  Navigator.of(context).pop();
                                },
                                child: const Text('Cerrar'),
                              ),
                              IconButton(
                                onPressed: () {
                                  _viewPDF(context,'http://app.buyfrescapp.com:5000/api/order/generate_pdf/${order.id}'
                                  ); // Llama a la función para ver el PDF de remisión
                                },
                                  icon: const Column(
                                    children: [
                                      Icon(Icons.receipt,color: Colors.green), // Icono para editar
                                      Text('Remisión'), // Texto del botón
                                    ],
                                  ),
                              ),
                                  IconButton(
                                    onPressed: order.status == 'creada'
                                        ? () {
                                            _editOrder(context, order); // Llama a la función para editar la orden
                                          }
                                        : null,
                                    icon: Column(
                                      children: [
                                        Icon(
                                          Icons.description,
                                          color: order.status == 'Facturada' ? Colors.green : Colors.grey,
                                        ), // Icono para editar
                                        const Text('Factura'), // Texto del botón
                                      ],
                                    ),
                                  ),
                                  IconButton(
                                    onPressed: order.status == 'creada'
                                        ? () {
                                            _editOrder(context, order); // Llama a la función para editar la orden
                                          }
                                        : null,
                                    icon: Column(
                                      children: [
                                        Icon(
                                          Icons.edit,
                                          color: order.status == 'Creada' ? Colors.green : Colors.grey,
                                        ), // Icono para editar
                                        const Text('Editar'), // Texto del botón
                                      ],
                                    ),
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
          selectedItemColor: Colors.lightGreen.shade900, // Color de los iconos seleccionados
          unselectedItemColor: Colors.grey, // Color de los iconos no seleccionados
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
      ),
    );
  }
}

class PDFViewerScreen extends StatelessWidget {
  final String url;

  // ignore: use_super_parameters
  const PDFViewerScreen({Key? key, required this.url}) : super(key: key);

 @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Remisión Orden'),
      ),
      body: FutureBuilder<PDFDocument>(
        future: PDFDocument.fromURL('http://app.buyfrescapp.com:5000/api/order/generate_pdf/6658fc32a5e68b3b66af5184'),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          } else if (snapshot.hasError) {
            return const Center(
              child: Text('Error al cargar el PDF'),
            );
          } else if (snapshot.hasData) {
            return PDFViewer(document: snapshot.data!);
          } else {
            return const Center(
              child: Text('No se pudo cargar el PDF'),
            );
          }
        },
      ),
    );
  }
}

class EditOrderScreen extends StatelessWidget {
  final Order order;

  // ignore: use_super_parameters
  const EditOrderScreen({Key? key, required this.order}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Aquí agregarías el código para editar la orden
    return Scaffold(
      appBar: AppBar(
        title: const Text('Editar Orden'),
      ),
      body: Center(
        child: Text('Editar orden: ${order.orderNumber}'), // Placeholder para la edición de la orden
      ),
    );
  }
}
