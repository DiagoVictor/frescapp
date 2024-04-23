import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:frescapp/screens/newOrder/home_screen.dart';
import 'package:frescapp/screens/newOrder/order_confirmation_screen.dart';
import 'package:frescapp/screens/orders/orders_screen.dart';
import 'package:frescapp/screens/profile/profile_screen.dart';
import 'package:frescapp/services/product_service.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher_string.dart';

class OrderDetailScreen extends StatefulWidget {
  final List<Product> productsInCart;

  const OrderDetailScreen({super.key, required this.productsInCart});

  @override
  // ignore: library_private_types_in_public_api
  _OrderDetailScreenState createState() => _OrderDetailScreenState();
}

class _OrderDetailScreenState extends State<OrderDetailScreen> {
  late DateTime selectedDate;
  String? selectedDeliverySlot;
  String? selectedPaymentMethod;
  late List<String> paymentMethods = [];
  late List<String> deliverySlots = [];

  @override
  void initState() {
    super.initState();
    selectedDate = DateTime.now().add(const Duration(days: 1));
    selectedDeliverySlot = 'Horario de entrega';
    selectedPaymentMethod = 'Método de pago';
    getOrderDetailsFromSharedPreferences();

  }
void getOrderDetailsFromSharedPreferences() async {
  try {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    setState(() {
      // Actualiza las listas después de obtener las preferencias compartidas
      deliverySlots = prefs.getStringList('delivery_slots') ?? [];
      paymentMethods = prefs.getStringList('payments_method') ?? [];
    });
  } catch (e) {
    if (kDebugMode) {
      print('Error al obtener preferencias compartidas: $e');
    }
  }
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
                'Total: \$ ${NumberFormat('#,###').format(total)}',
                style:
                    const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
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
                'Horario de Entrega:',
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
                _openWhatsApp(context); // Función para abrir WhatsApp
                break;
            }
          },
        ),
      ),
    );
  }

  Future<void> _selectDate(BuildContext context) async {
    DateTime now = DateTime.now();
    late DateTime primer;
    final DateTime lastDate = DateTime(now.year, now.month, now.day + 7);

    if (now.weekday == DateTime.friday && now.hour >= 18) {
      // Es viernes después de las 6 p.m.
      primer = DateTime(now.year, now.month,
          now.day + 3); // Primer día disponible es el lunes
    } else {
      // Otro día de la semana o viernes antes de las 6 p.m.
      primer = DateTime(now.year, now.month,
          now.day + 1); // El primer día disponible es el siguiente
    }

    final DateTime? picked = await showDatePicker(
      context: context,
      firstDate: primer,
      lastDate: lastDate,
      selectableDayPredicate: _isSelectableDate,
    );

    if (picked != null && picked != selectedDate) {
      setState(() {
        selectedDate = picked;
      });
    }
  }

  bool _isSelectableDate(DateTime day) {
    // Evitar seleccionar domingos
    if (day.weekday == DateTime.sunday) {
      return false;
    }

    return true;
  }

  void _confirmOrder(BuildContext context) {
    List<Map<String, dynamic>> productList =
        widget.productsInCart.map((product) {
      return {
        'sku': product.sku,
        'name': product.name,
        'price_sale': product.price_sale,
        'quantity': product.quantity,
        'iva': product.iva,
        'iva_value': product.iva_value
      };
    }).toList();

    Map<String, dynamic> orderDetails = {
      'products': productList,
      'total': widget.productsInCart.fold(
          0.0 , (sum, product) => sum + (product.price_sale * product.quantity!)),
      'deliverySlot': selectedDeliverySlot,
      'paymentMethod': selectedPaymentMethod,
      'deliveryDate': DateFormat('yyyy-MM-dd').format(selectedDate),
    };

    Navigator.push(
      context,
      MaterialPageRoute(
          builder: (context) =>
              OrderConfirmationScreen(orderDetails: orderDetails)),
    );
  }
}
