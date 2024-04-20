import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:frescapp_web/api_routes.dart';

class ProductService {

  Future<List<Product>> getProducts() async {
    // Hacer la solicitud HTTP para obtener los datos de los productos desde el endpoint
    final response = await http.get(Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.products}/products'));

    // Verificar si la solicitud fue exitosa (código de estado 200)
    if (response.statusCode == 200) {
      // Decodificar los datos JSON de la respuesta
      List<dynamic> productData = jsonDecode(response.body);
      
      // Mapear los datos decodificados a objetos de tipo Product
      List<Product> products = productData.map((data) => Product.fromMap(data)).toList();

      return products;
    } else {
      // Si la solicitud falla, lanzar una excepción o devolver una lista vacía
      throw Exception('Failed to load products');
    }
  }
}

class Product {
  final String name;
  final String unit;
  final String sku;
  final String category;
  // ignore: non_constant_identifier_names
  final int price_sale;
  // ignore: non_constant_identifier_names
  final int price_purchase;
  final double discount;
  final double margen;
  final bool iva;
  // ignore: non_constant_identifier_names
  final double iva_value;
  final String description;
  final String image;
  final String status;
  int? quantity; 
  Product({
    required this.name,
    required this.unit,
    required this.sku,
    required this.category,
    // ignore: non_constant_identifier_names
    required this.price_sale,
    // ignore: non_constant_identifier_names
    required this.price_purchase,
    required this.discount,
    required this.margen,
    required this.iva,
    // ignore: non_constant_identifier_names
    required this.iva_value,
    required this.description,
    required this.image,
    required this.status,
    required this.quantity
  });

  factory Product.fromMap(Map<String, dynamic> map) {
    return Product(
      name: map['name'],
      unit: map['unit'],
      sku: map['sku'],
      category: map['category'],
      price_sale: map['price_sale'], 
      price_purchase: map['price_purchase'], 
      discount: map['discount'], 
      margen: map['margen'], 
      iva:  map['iva'],
      iva_value: map['iva_value'],
      description: map['description'], 
      image: map['image'], 
      status: map['status'],
      quantity: map['quantity']
    );
  }

  toJson() {}
}
