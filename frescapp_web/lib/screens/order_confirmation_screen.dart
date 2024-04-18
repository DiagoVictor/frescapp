import 'package:flutter/material.dart';
import 'package:frescapp_web/screens/home_screen.dart';
import 'package:frescapp_web/screens/orders_screen.dart';
import 'package:frescapp_web/screens/profile_screen.dart';
// ignore: depend_on_referenced_packages

class OrderConfirmationScreen extends StatelessWidget {
  final Map<String, dynamic> orderDetails;

  const OrderConfirmationScreen({super.key, required this.orderDetails});

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
              // Formulario para información del cliente
              _buildCustomerInfoForm(),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: () {
                  // Lógica para finalizar el pedido
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

  Widget _buildCustomerInfoForm() {
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
        ),
        const SizedBox(height: 16),
        DropdownButtonFormField<String>(
          decoration: const InputDecoration(
            labelText: 'Tipo de Documento',
            border: OutlineInputBorder(),
          ),
          value: 'Cédula',
          onChanged: (String? newValue) {},
          items: <String>['Cédula', 'Pasaporte', 'Carné de Identidad']
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
        ),
        const SizedBox(height: 16),
        TextFormField(
          keyboardType: TextInputType.phone,
          decoration: const InputDecoration(
            labelText: 'Número de Teléfono',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 16),
        TextFormField(
          keyboardType: TextInputType.emailAddress,
          decoration: const InputDecoration(
            labelText: 'Correo Electrónico',
            border: OutlineInputBorder(),
          ),
        ),
      ],
    );
  }
}
