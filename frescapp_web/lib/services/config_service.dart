import 'dart:convert';
import 'package:frescapp_web/api_routes.dart';

class ConfigService {
  get http => null;

  Future<Map<String, dynamic>> getConfigData() async {
    final response = await http.get(Uri.parse('${ApiRoutes.baseUrl}/config/configOrder'));
    if (response.statusCode == 200) {
      // Decodifica la respuesta JSON
      final dynamic responseData = jsonDecode(response.body);
      if (responseData is Map<String, dynamic>) {
        return responseData;
      } else {
        throw Exception('Invalid data format');
      }
    } else {
      throw Exception('Failed to load config data');
    }
  }

  Future<List<String>> getPaymentMethods() async {
    final Map<String, dynamic> configData = getConfigData() as Map<String, dynamic>;
    final List<String> paymentMethodData = configData['payment_method'];
    return paymentMethodData.cast<String>();
  }

  getDeliverySlots() async {
    List<String> configData = getConfigData() as List<String>;
    return configData[0];
  }
}
