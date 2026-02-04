class CartManager {
  static final CartManager _instance = CartManager._internal();
  factory CartManager() => _instance;
  CartManager._internal();

  final List<Map<String, dynamic>> _items = [];
  int? currentFamilyId;

  List<Map<String, dynamic>> get items => _items;

  void addToCart(Map<String, dynamic> product, int quantity, int familyId) {
    if (currentFamilyId != null && currentFamilyId != familyId) {
      // Clear cart if adding from a different family (simple rule for now)
      _items.clear();
    }
    currentFamilyId = familyId;

    // Check if item exists
    final index = _items.indexWhere(
      (item) => item['product']['id'] == product['id'],
    );
    if (index >= 0) {
      _items[index]['quantity'] += quantity;
    } else {
      _items.add({'product': product, 'quantity': quantity});
    }
  }

  void removeFromCart(int productId) {
    _items.removeWhere((item) => item['product']['id'] == productId);
    if (_items.isEmpty) {
      currentFamilyId = null;
    }
  }

  void clearCart() {
    _items.clear();
    currentFamilyId = null;
  }

  double get totalAmount {
    return _items.fold(0, (sum, item) {
      final price = (item['product']['price'] as num).toDouble();
      return sum + (price * item['quantity']);
    });
  }
}
