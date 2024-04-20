import 'package:flutter/material.dart';
import 'package:frescapp_web/screens/newOrder/home_screen.dart';
import 'package:frescapp_web/screens/newOrder/order_confirmation_screen.dart';
import 'package:frescapp_web/screens/orders/orders_screen.dart';
import 'package:frescapp_web/screens/profile/profile_screen.dart';
import 'package:frescapp_web/services/product_service.dart';
import 'package:intl/intl.dart'; 

class OrderDetailScreen extends StatefulWidget {
  final List<Product> productsInCart;

  const OrderDetailScreen({super.key,  required this.productsInCart});

  @override
  // ignore: library_private_types_in_public_api
  _OrderDetailScreenState createState() => _OrderDetailScreenState();
}

class _OrderDetailScreenState extends State<OrderDetailScreen> {
  late DateTime selectedDate;
  String? selectedDeliverySlot;
  String? selectedPaymentMethod;
  late List<String> paymentMethods = ["Nequi", "Daviplata", "Transf. Bancaria", "Efectivo en la entrega"];
  late List<String> deliverySlots = ["06:00 AM - 09:00 AM", "09:00 AM - 12:00 PM", "12:00 PM - 03:00 PM", "03:00 PM - 03:59 PM"];

  @override
  void initState() {
    super.initState();
    selectedDate = DateTime.now().add(const Duration(days: 1));
    selectedDeliverySlot = 'Slot de entrega';
    selectedPaymentMethod = 'Método de pago';
  }

  @override
  Widget build(BuildContext context) {
    double total = widget.productsInCart.fold(
        0, (sum, product) => sum + (product.price_sale * product.quantity!));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Detalle del Pedido'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Center(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Text(
                'Total: \$ $total',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              const Text(
                'Fecha de Entrega:',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              SizedBox(
                width: 200,
                child: ElevatedButton(
                  onPressed: () {
                    _selectDate(context);
                  },
                  child: Text(
                    '${selectedDate.day}/${selectedDate.month}/${selectedDate.year}',
                  ),
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Slot de Entrega:',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Column(
                children: deliverySlots.map((slot) {
                  return RadioListTile<String>(
                    title: Text(slot),
                    value: slot,
                    groupValue: selectedDeliverySlot,
                    onChanged: (String? newValue) {
                      setState(() {
                        selectedDeliverySlot = newValue;
                      });
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
              const Text(
                'Medio de Pago:',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Column(
                children: paymentMethods.map((method) {
                  return RadioListTile<String>(
                    title: Text(method),
                    value: method,
                    groupValue: selectedPaymentMethod,
                    onChanged: (String? newValue) {
                      setState(() {
                        selectedPaymentMethod = newValue;
                      });
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  _confirmOrder(context);
                },
                child: const Text('Confirmar Pedido'),
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
      ),
    );
  }

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: selectedDate,
      firstDate: DateTime.now().add(const Duration(days: 1)),
      lastDate: DateTime(2101),
    );
    if (picked != null && picked != selectedDate) {
      setState(() {
        selectedDate = picked;
      });
    }
  }

  void _confirmOrder(BuildContext context) {
    List<Map<String, dynamic>> productList = widget.productsInCart.map((product) {
      return {
        'sku': product.sku,
        'name': product.name,
        'price_sale': product.price_sale,
        'quantity': product.quantity,
        'iva' : product.iva,
        'iva_value': product.iva_value
      };
    }).toList();

    Map<String, dynamic> orderDetails = {
      'products': productList,
      'total': widget.productsInCart.fold(0, (sum, product) => sum + (product.price_sale * product.quantity!)),
      'deliverySlot': selectedDeliverySlot,
      'paymentMethod': selectedPaymentMethod,
      'deliveryDate': DateFormat('yyyy-MM-dd').format(selectedDate),
    };

    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => OrderConfirmationScreen(orderDetails: orderDetails)),
    );
  }
}
