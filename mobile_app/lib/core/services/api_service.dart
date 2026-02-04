import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Use 10.0.2.2 for Android Emulator to access localhost
  static const String baseUrl = 'http://10.0.2.2:3000/api';

  static Future<Map<String, dynamic>> login(
    String email,
    String password,
  ) async {
    try {
      final response = await http.post(
        Uri.parse(
          '$baseUrl/users/login',
        ), // Assuming login route exists or using register for demo if login not created yet
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        throw Exception('فشل تسجيل الدخول: ${response.body}');
      }
    } catch (e) {
      throw Exception('خطأ في الاتصال: $e');
    }
  }

  static Future<List<dynamic>> getFamilies() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/shop/families'));
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('فشل جلب البيانات');
      }
    } catch (e) {
      throw Exception('خطأ في الاتصال: $e');
    }
  }

  static Future<List<dynamic>> getProducts(int familyId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/shop/products/family/$familyId'),
      );
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('فشل جلب المنتجات');
      }
    } catch (e) {
      throw Exception('خطأ في الاتصال: $e');
    }
  }
  static Future<void> createOrder({
    required int buyerId,
    required int familyId,
    required List<Map<String, dynamic>> items,
    required String deliveryAddress,
    String? notes,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/orders'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'buyer_id': buyerId,
          'family_id': familyId,
          'items': items,
          'delivery_address': deliveryAddress,
          'notes': notes,
        }),
      );

      if (response.statusCode != 201) {
        throw Exception('فشل إنشاء الطلب: ${response.body}');
      }
    } catch (e) {
      throw Exception('خطأ في الاتصال: $e');
    }
  }
}
