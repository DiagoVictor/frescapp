import 'dart:convert';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:frescapp_web/screens/newOrder/home_screen.dart';
import 'package:frescapp_web/screens/orders/orders_screen.dart';
import 'package:frescapp_web/screens/profile/profile_screen.dart';

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

  Future<void> sendOrderDetailsToService(Map<String, dynamic> orderDetails) async {
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
                'Fecha de Entrega: ${orderDetails['deliveryDate']}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 16),
              Text(
                'Slot de Entrega: ${orderDetails['deliverySlot']}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text(
                'Medio de Pago: ${orderDetails['paymentMethod']}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 8),
              Text(
                'Total: \$ ${orderDetails['total']}',
                style: const TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 24),
              _buildCustomerInfoForm(orderDetails),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: () {
                  sendOrderDetailsToService(orderDetails);
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
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.home),
              label: 'Inicio',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.shopping_bag),
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

  Widget _buildCustomerInfoForm(Map<String, dynamic> orderDetails) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Información del Cliente',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),
        TextFormField(
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
          decoration: const InputDecoration(
            labelText: 'Tipo de Documento',
            border: OutlineInputBorder(),
          ),
          value: '',
          onChanged: (String? newValue) {
            orderDetails['documentType'] = newValue;
          },
          items: <String>['', 'Cédula', 'NIT', 'Pasaporte', 'Carnét de Identidad']
              .map<DropdownMenuItem<String>>((String value) {
            return DropdownMenuItem<String>(
              value: value,
              child: Text(value),
            );
          }).toList(),
        ),
        const SizedBox(height: 16),
        TextFormField(
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
          keyboardType: TextInputType.emailAddress,
          decoration: const InputDecoration(
            labelText: 'Correo Electrónico',
            border: OutlineInputBorder(),
          ),
          onChanged: (value) {
            orderDetails['email'] = value;
          },
        ),
      ],
    );
  }
}
