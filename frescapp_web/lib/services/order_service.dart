import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frescapp/api_routes.dart';

class OrderService {
  Future<List<Order>> getOrders(email) async {
    final response = await http.get(Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.orders}/orders_customer/$email'));

    if (response.statusCode == 200) {
      List<dynamic> orderDataList = jsonDecode(response.body);
      // Mapear los datos recibidos a una lista de objetos Order
      List<Order> orders = orderDataList.map((data) => Order.fromMap(data)).toList();
      return orders;
    } else {
      throw Exception('Failed to load orders');
    }
  }
}

class Order {
  final String id;
  final String orderNumber;
  final String customerEmail;
  final String customerPhone;
  final String customerDocumentNumber;
  final String customerDocumentType;
  final String customerName;
  final String deliveryDate;
  final String status;
  final String createdAt;
  final String updatedAt;
  final List<String> products;
  final double total;
  final String deliverySlot;
  final String paymentMethod;

  Order({
    required this.id,
    required this.orderNumber,
    required this.customerEmail,
    required this.customerPhone,
    required this.customerDocumentNumber,
    required this.customerDocumentType,
    required this.customerName,
    required this.deliveryDate,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    required this.products,
    required this.total,
    required this.deliverySlot,
    required this.paymentMethod,
  });

  factory Order.fromMap(Map<String, dynamic> map) {
    return Order(
      id: map['id'],
      orderNumber: map['order_number'],
      customerEmail: map['customer_email'],
      customerPhone: map['customer_phone'],
      customerDocumentNumber: map['customer_documentNumber'],
      customerDocumentType: map['customer_documentType'],
      customerName: map['customer_name'],
      deliveryDate: map['delivery_date'],
      status: map['status'],
      createdAt: map['created_at'],
      updatedAt: map['updated_at'],
      products: (map['products'] as List).cast<String>(),
      total: map['total'],
      deliverySlot: map['deliverySlot'],
      paymentMethod: map['paymentMethod'],
    );

  }
}
