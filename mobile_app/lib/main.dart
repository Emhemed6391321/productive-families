import 'package:flutter/material.dart';
import 'package:mobile_app/features/auth/screens/login_screen.dart';

void main() {
  runApp(const ProductiveFamiliesApp());
}

class ProductiveFamiliesApp extends StatelessWidget {
  const ProductiveFamiliesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'الأسر المنتجة',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        fontFamily: 'Cairo',
        primarySwatch: Colors.teal, // Premium Color
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF0F766E), secondary: const Color(0xFFD97706)),
        useMaterial3: true,
      ),
      builder: (context, child) {
        return Directionality(
          textDirection: TextDirection.rtl,
          child: child!,
        );
      },
      home: const LoginScreen(),
    );
  }
}
