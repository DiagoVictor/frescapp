import 'dart:convert';

class ConfigService {
  get http => null;

  Future<Map<String, dynamic>> getConfigData() async {
    final response = await http.get(Uri.parse('http://localhost:5000/api/config/configOrder'));
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
    final Map<String, dynamic> configData = await getConfigData();
    final List<String> paymentMethodData = configData['payment_method'];
    return paymentMethodData.cast<String>();
  }

  Future<Map<String, List<String>>> getDeliverySlots() async {
    final Map<String, dynamic> configData = await getConfigData();
    final List<String> slotData = configData['slot'];
    //return slotData.cast<String>();
    return {"slot":["a","b"]};
  }
}
