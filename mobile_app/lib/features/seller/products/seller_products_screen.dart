import 'package:flutter/material.dart';

class SellerProductsScreen extends StatefulWidget {
  const SellerProductsScreen({super.key});

  @override
  State<SellerProductsScreen> createState() => _SellerProductsScreenState();
}

class _SellerProductsScreenState extends State<SellerProductsScreen> {
  // Mock data
  final List<Map<String, dynamic>> products = [
    {'name': 'كبسة سعودية', 'price': 45, 'active': true},
    {'name': 'جريش باللبن', 'price': 30, 'active': true},
    {'name': 'كليجا القصيم', 'price': 50, 'active': false},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('منتجاتي', style: TextStyle(color: Colors.black)),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Add product logic
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('واجهة إضافة المنتج قادمة قريباً')),
          );
        },
        backgroundColor: Colors.blue,
        child: const Icon(Icons.add),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: products.length,
        itemBuilder: (context, index) {
          final product = products[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: ListTile(
              leading: Container(
                width: 50,
                height: 50,
                decoration: BoxDecoration(
                  color: Colors.grey[200],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.fastfood, color: Colors.grey),
              ),
              title: Text(
                product['name'],
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Text('${product['price']} ر.س'),
              trailing: Switch(
                value: product['active'],
                activeColor: Colors.green,
                onChanged: (val) {
                  setState(() {
                    product['active'] = val;
                  });
                },
              ),
            ),
          );
        },
      ),
    );
  }
}
