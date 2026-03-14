import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiRoutes {
  static String get baseUrl =>
      dotenv.env['API_URL'] ?? 'https://app.buyfrescapp.com:5000/api';

  // Define todas tus rutas aquí
  static const String orders = '/order';
  static const String products = '/product';
  static const String customers = '/customer';
  static const String user = '/user';
}
