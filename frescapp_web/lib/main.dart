import 'package:flutter/material.dart';
import 'package:frescapp_web/screens/login_screen.dart';
import 'package:frescapp_web/routes.dart';


void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Frescapp',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0x0097d700)),
        useMaterial3: true,
      ),
      home: const LoginScreen(), // Cambia MyHomePage por LoginScreen
      onGenerateRoute: Routes.generateRoute
    );
  }
}