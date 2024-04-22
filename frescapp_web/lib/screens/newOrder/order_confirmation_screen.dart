import 'dart:convert';
// ignore: avoid_web_libraries_in_flutter
import 'dart:js';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:frescapp_web/screens/newOrder/home_screen.dart';
import 'package:frescapp_web/screens/orders/orders_screen.dart';
import 'package:frescapp_web/screens/profile/profile_screen.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';

class OrderConfirmationScreen extends StatelessWidget {
  final Map<String, dynamic> orderDetails;
  const OrderConfirmationScreen({super.key, required this.orderDetails});

  String generateOrderNumber() {
    Random random = Random();
    int orderNumber = random.nextInt(90000) + 10000;
    return orderNumber.toString();
  }

  String getCurrentDateTimeString() {
    DateTime now = DateTime.now();
    return now.toIso8601String();
  }

  void _openWhatsApp() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    String phoneNumber = prefs.getString('contact_phone') ?? '';
    String url = 'https://wa.me/$phoneNumber';
    // ignore: deprecated_member_use
    if (await canLaunch(url)) {
      // ignore: deprecated_member_use
      await launch(url);
    } else {
      ScaffoldMessenger.of(context as BuildContext).showSnackBar(
        const SnackBar(
          content: Text('No se pudo abrir WhatsApp.'),
        ),
      );
    }
  }

  Future<void> sendOrderDetailsToService(
      Map<String, dynamic> orderDetails) async {
    orderDetails['order_number'] = generateOrderNumber();
    orderDetails['created_at'] = getCurrentDateTimeString();
    orderDetails['updated_at'] = getCurrentDateTimeString();

    const url = 'http://127.0.0.1:5000/api/order/order';
    await http.post(
      Uri.parse(url),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(orderDetails),
    );
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, dynamic>>(
      future: getOrderDetailsFromSharedPreferences(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const CircularProgressIndicator();
        } else if (snapshot.hasError) {
          return Text('Error: ${snapshot.error}');
        } else {
          Map<String, dynamic> orderDetailsFromSharedPreferences =
              snapshot.data ?? {};
          return _buildOrderConfirmationScreen(
              context, orderDetailsFromSharedPreferences);
        }
      },
    );
  }

  Widget _buildOrderConfirmationScreen(BuildContext context,
      Map<String, dynamic> orderDetailsFromSharedPreferences) {
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
                'Fecha de Entrega: ${orderDetailsFromSharedPreferences['deliveryDate'] ?? ''}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 16),
              Text(
                'Horario de Entrega: ${orderDetailsFromSharedPreferences['deliverySlot'] ?? ''}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text(
                'Medio de Pago: ${orderDetailsFromSharedPreferences['paymentMethod'] ?? ''}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text(
                'Costo de envio: \$ ${orderDetailsFromSharedPreferences['deliveryCost']}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text(
                'Total: \$ ${NumberFormat('#,###').format(orderDetailsFromSharedPreferences['total'] ?? 0)}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 24),
              _buildCustomerInfoForm(orderDetailsFromSharedPreferences),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: () {
                  sendOrderDetailsToService(orderDetailsFromSharedPreferences);
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const HomeScreen()),
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
                _openWhatsApp();
                break;
            }
          },
        ),
      ),
    );
  }

  Widget _buildCustomerInfoForm(Map<String, dynamic> orderDetails) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Información de Facturación',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        TextFormField(
          initialValue: orderDetails['customerName'] ?? '',
          decoration: const InputDecoration(
            labelText: 'Nombre',
            border: OutlineInputBorder(),
          ),
          onChanged: (value) {
            orderDetails['customerName'] = value;
          },
        ),
        const SizedBox(height: 16),
        DropdownButtonFormField<String>(
          value: orderDetails['documentType'] ?? '',
          decoration: const InputDecoration(
            labelText: 'Tipo de Documento',
            border: OutlineInputBorder(),
          ),
          onChanged: (String? newValue) {
            orderDetails['documentType'] = newValue;
          },
          items: orderDetails["listdocumentType"].map<DropdownMenuItem<String>>((String value) {
            return DropdownMenuItem<String>(
              value: value,
              child: Text(value),
            );
          }).toList(),
        ),
        const SizedBox(height: 16),
        TextFormField(
          initialValue: orderDetails['documentNumber'] ?? '',
          decoration: const InputDecoration(
            labelText: 'Número de Documento',
            border: OutlineInputBorder(),
          ),
          onChanged: (value) {
            orderDetails['documentNumber'] = value;
          },
        ),
        const SizedBox(height: 16),
        TextFormField(
          initialValue: orderDetails['phoneNumber'] ?? '',
          keyboardType: TextInputType.phone,
          decoration: const InputDecoration(
            labelText: 'Número de Teléfono',
            border: OutlineInputBorder(),
          ),
          onChanged: (value) {
            orderDetails['phoneNumber'] = value;
          },
        ),
        const SizedBox(height: 16),
        TextFormField(
          initialValue: orderDetails['email'] ?? '',
          keyboardType: TextInputType.emailAddress,
          decoration: const InputDecoration(
            labelText: 'Correo Electrónico',
            border: OutlineInputBorder(),
          ),
          onChanged: (value) {
            orderDetails['email'] = value;
          },
        ),
        const SizedBox(height: 16),
        TextFormField(
          initialValue: orderDetails['deliveryAddress'] ?? '',
          decoration: const InputDecoration(
            labelText: 'Dirección de Entrega',
            border: OutlineInputBorder(),
          ),
          onChanged: (value) {
            orderDetails['deliveryAddress'] = value;
          },
        ),
        const SizedBox(height: 16),
        TextFormField(
          initialValue: orderDetails['deliveryAddressDetails'] ?? '',
          decoration: const InputDecoration(
            labelText: 'Detalle de Dirección',
            border: OutlineInputBorder(),
          ),
          onChanged: (value) {
            orderDetails['deliveryAddressDetails'] = value;
          },
        ),
      ],
    );
  }

  Future<Map<String, dynamic>> getOrderDetailsFromSharedPreferences() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    orderDetails['customerName'] = prefs.getString('user_name') ?? '';
    orderDetails['email'] = prefs.getString('user_email') ?? '';
    orderDetails['documentType'] = prefs.getString('user_document_type') ?? '';
    orderDetails['documentNumber'] = prefs.getString('user_document') ?? '';
    orderDetails['phoneNumber'] = prefs.getString('user_phone') ?? '';
    orderDetails['deliveryCost'] = prefs.getString('delivery_cost') ?? '';
    orderDetails["listdocumentType"] = prefs.getStringList('document_type') ?? [];
    orderDetails["deliveryAddress"] =  prefs.getString('user_address') ?? '';
    orderDetails["deliveryAddressDetails"] = '';
    return orderDetails;
  }
}
