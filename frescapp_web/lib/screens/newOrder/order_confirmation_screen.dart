import 'dart:convert';
import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:frescapp/models/order.dart';
import 'package:frescapp/screens/newOrder/home_screen.dart';
import 'package:frescapp/screens/orders/orders_screen.dart';
import 'package:frescapp/screens/profile/profile_screen.dart';
import 'package:frescapp/services/order_service.dart';
import 'package:frescapp/api_routes.dart';
import 'package:frescapp/services/discount_service.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher_string.dart';

// ignore: must_be_immutable
class OrderConfirmationScreen extends StatefulWidget {
  static List<DropdownMenuItem<String>> listDocumentType = [];
  final Order orderDetails;

  const OrderConfirmationScreen({super.key, required this.orderDetails});

  @override
  // ignore: library_private_types_in_public_api
  _OrderConfirmationScreenState createState() =>
      _OrderConfirmationScreenState();
}

class _OrderConfirmationScreenState extends State<OrderConfirmationScreen> {
  final TextEditingController _codeController = TextEditingController();

  @override
  void initState() {
    super.initState();
    getOrderDetailsFromSharedPreferences();
  }

  Future<Order> getOrderDetailsFromSharedPreferences() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    try {
      final String customerId = prefs.getString('user_id') ?? '';
      final response = await http.get(Uri.parse(
          '${ApiRoutes.baseUrl}${ApiRoutes.customers}/customer/$customerId'));
      if (response.statusCode == 200) {
        var userData = jsonDecode(response.body);
        widget.orderDetails.customerName = userData['name'];
        widget.orderDetails.customerPhone = userData['phone'];
        widget.orderDetails.customerDocumentNumber = userData['document'];
        widget.orderDetails.customerDocumentType = userData['document_type'];
        widget.orderDetails.deliveryAddress = userData['address'];
        widget.orderDetails.customerEmail = userData['email'];
        widget.orderDetails.deliveryCost =
            (prefs.getDouble('delivery_cost') ?? 0) as double?;
      } else {
        throw Exception('Failed to load user data');
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error fetching user data: $e');
      }
    }

    return widget.orderDetails;
  }

  Future<bool> validateCode(String code, String email) async {
    final DiscountService discountService = DiscountService();
    double? descuento = await discountService.validateCode(code,email) as double?;
    setState(() {
        widget.orderDetails.discount = ((descuento!/100) * widget.orderDetails.total!);
        widget.orderDetails.total = widget.orderDetails.total! - widget.orderDetails.discount!;
    });
    return widget.orderDetails.discount as double > 0.0;
  }

  String generateOrderNumber() {
    Random random = Random();
    int orderNumber = random.nextInt(90000) + 10000;
    return orderNumber.toString();
  }

  String getCurrentDateTimeString() {
    DateTime now = DateTime.now();
    return now.toIso8601String();
  }

  void _openWhatsApp(BuildContext context) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    try {
      String name = prefs.getString('user_name') ?? '';
      String email = prefs.getString('user_email') ?? '';
      String phone = prefs.getString('user_phone') ?? '';
      String contactPhone = prefs.getString('contact_phone') ?? '';

      String message =
          'Hola, soy $name y mis datos son:\nEmail: $email\nTeléfono: $phone. Tengo la siguiente duda.';

      String encodedMessage = Uri.encodeComponent(message);
      String url = 'whatsapp://send?phone=$contactPhone&text=$encodedMessage';

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
  Future<void> sendOrderDetailsToService(Order orderDetails) async {
    if (orderDetails.orderNumber == null ||
        orderDetails.orderNumber!.isEmpty ||
        orderDetails.orderNumber == '') {
      orderDetails.orderNumber = generateOrderNumber();
      orderDetails.createdAt = getCurrentDateTimeString();
      orderDetails.updatedAt = getCurrentDateTimeString();
    }
    final OrderService orderService = OrderService();
    try {
      await orderService.createOrder(
          orderDetails.orderNumber ?? '', orderDetails);
    } catch (e) {
      if (kDebugMode) {
        print('Error al enviar detalles del pedido al servicio: $e');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return _buildOrderConfirmationScreen(context);
  }

  Widget _buildOrderConfirmationScreen(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Confirmar Pedido'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Text(
                'Detalles del Pedido',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 32),
              Text(
                'Fecha de Entrega: ${widget.orderDetails.deliveryDate ?? ''}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 16),
              Text(
                'Horario de Entrega: ${widget.orderDetails.deliverySlot ?? ''}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text(
                'Medio de Pago: ${widget.orderDetails.paymentMethod ?? ''}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text(
                'Costo de envío: \$ ${widget.orderDetails.deliveryCost ?? 0}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text(
                'Descuento: \$ ${(NumberFormat('#,###').format(widget.orderDetails.discount as double))}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text(
                'Total: \$ ${NumberFormat('#,###').format(widget.orderDetails.total!)}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 24),
              _buildCustomerInfoForm(),
              const SizedBox(height: 16),
              _buildValidationSection(),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () async {
                  // Llamada a servicio para enviar los detalles de la orden
                  await sendOrderDetailsToService(widget.orderDetails);

                  // Mostrar SnackBar de confirmación
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Orden creada exitosamente'),
                    ),
                  );

                  // Navegación a la pantalla de pedidos
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const OrdersScreen()),
                  );
                },
                child: const Text('Finalizar'),
              ),
            ],
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: BottomNavigationBar(
          currentIndex: 0,
          selectedItemColor: Colors.lightGreen.shade900,
          unselectedItemColor: Colors.grey,
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
              icon: Icon(Icons.chat),
              label: 'WhatsApp',
            ),
          ],
          onTap: (int index) {
            switch (index) {
              case 0:
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => HomeScreen(order: widget.orderDetails)),
                );
                break;
              case 1:
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) =>  OrdersScreen(order: widget.orderDetails)),
                );
                break;
              case 2:
                Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => ProfileScreen(order: widget.orderDetails)),
                );
                break;
              case 3:
                _openWhatsApp(context);
                break;
            }
          },
        ),
      ),
    );
  }

  Widget _buildCustomerInfoForm() {
    return FutureBuilder<Order>(
      future: getOrderDetailsFromSharedPreferences(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const CircularProgressIndicator();
        } else if (snapshot.hasError) {
          return Text('Error: ${snapshot.error}');
        } else if (!snapshot.hasData || snapshot.data == null) {
          return const Text('No se encontraron datos de facturación.');
        } else {
          Order orderDetails = snapshot.data!;
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Información de Facturación',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: orderDetails.customerName ?? '',
                decoration: const InputDecoration(
                  labelText: 'Nombre',
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) {
                  orderDetails.customerName = value;
                },
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: orderDetails.customerDocumentType ?? '',
                decoration: const InputDecoration(
                  labelText: 'Tipo de Documento',
                  border: OutlineInputBorder(),
                ),
                onChanged: (String? newValue) {
                  orderDetails.customerDocumentType = newValue;
                },
                items: <String>['', 'CC', 'NIT', 'PA', 'TI']
                    .map<DropdownMenuItem<String>>(
                      (String value) => DropdownMenuItem<String>(
                        value: value,
                        child: Text(value),
                      ),
                    )
                    .toList(),
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: orderDetails.customerDocumentNumber ?? '',
                decoration: const InputDecoration(
                  labelText: 'Número de Documento',
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) {
                  orderDetails.customerDocumentNumber = value;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: orderDetails.customerPhone ?? '',
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(
                  labelText: 'Número de Teléfono',
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) {
                  orderDetails.customerPhone = value;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: orderDetails.customerEmail ?? '',
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                  labelText: 'Correo Electrónico',
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) {
                  orderDetails.customerEmail = value;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: orderDetails.deliveryAddress ?? '',
                decoration: const InputDecoration(
                  labelText: 'Dirección de Entrega',
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) {
                  orderDetails.deliveryAddress = value;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: orderDetails.deliveryAddressDetails ?? '',
                decoration: const InputDecoration(
                  labelText: 'Detalle de Dirección',
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) {
                  orderDetails.deliveryAddressDetails = value;
                },
              ),
            ],
          );
        }
      },
    );
  }

  Widget _buildValidationSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Validar Código',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _codeController,
                decoration: const InputDecoration(
                  labelText: 'Código',
                  border: OutlineInputBorder(),
                ),
              ),
            ),
            const SizedBox(width: 8),
            ElevatedButton(
              onPressed: () async {
                String code = _codeController.text;
                String email = widget.orderDetails.customerEmail ?? '';
                bool isValid = await validateCode(code, email);
                // ignore: use_build_context_synchronously
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                        isValid ? 'Código válido' : 'Código no válido'),
                  ),
                );
              },
              child: const Icon(Icons.search),
            ),
          ],
        ),
      ],
    );
  }
}
