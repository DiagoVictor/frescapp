import 'package:flutter/material.dart';
import 'package:frescapp_web/services/product_service.dart';
import 'package:frescapp_web/services/config_service.dart';

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
  final ConfigService configService = ConfigService();

  @override
  void initState() {
    super.initState();
    selectedDate = DateTime.now();
    selectedDeliverySlot = 'Slot de entrega';
    selectedPaymentMethod = 'Método de pago';
    fetchConfigData();
  }

  Future<void> fetchConfigData() async {
    paymentMethods = await configService.getPaymentMethods();
    deliverySlots = (await configService.getDeliverySlots()) as List<String>;
    setState(() {}); // Actualiza el estado para reflejar los datos obtenidos
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
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
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
            // Aquí iría el selector de fecha (DatePicker, por ejemplo)
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
                // Lógica para confirmar el pedido
              },
              child: const Text('Confirmar Pedido'),
            ),
          ],
        ),
      ),
    );
  }
}
