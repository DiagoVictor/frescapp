import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:frescapp/api_routes.dart'; 
import 'package:frescapp/screens/newOrder/home_screen.dart';
import 'package:frescapp/screens/forgot_password_screen.dart'; // Importar la pantalla para olvidar la contraseña

class LoginScreen extends StatelessWidget {
  LoginScreen({super.key});

  // Controladores de texto para los campos de entrada de correo electrónico y contraseña
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  Future<void> _saveUserInfo(dynamic user) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    prefs.setString('user_id', user['user_data']['_id']);
    prefs.setString('user_phone', user['user_data']['phone']);
    prefs.setString('user_name', user['user_data']['name']);
    prefs.setString('user_document', user['user_data']['document']);
    prefs.setString('user_document_type', user['user_data']['document_type']);
    prefs.setString('user_address', user['user_data']['address']);
    prefs.setString('user_restaurant_name', user['user_data']['restaurant_name']);
    prefs.setString('user_email', user['user_data']['email']);
    prefs.setString('user_status', user['user_data']['status']);
    prefs.setString('user_created_at', user['user_data']['created_at']);
    prefs.setString('user_updated_at', user['user_data']['updated_at']);
    prefs.setString('user_category', user['user_data']['category']);
    prefs.setString('token', user['token']);
  }

  Future<void> _login(BuildContext context, String email, String password) async {
    if (email.isEmpty || password.isEmpty) {
      // Mostrar mensaje de error si falta correo electrónico o contraseña
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Por favor, ingrese correo electrónico y contraseña'),
        ),
      );
      return;
    }

    try {
      final response = await http.post(
        Uri.parse('${ApiRoutes.baseUrl}${ApiRoutes.user}/login'), // Endpoint del login
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8'
        },
        body: jsonEncode(<String, String>{
          'user': email,
          'password': password,
        }),
      );
      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        // Guardar el correo electrónico y la contraseña en las preferencias compartidas
        _saveUserInfo(responseData);
        Navigator.push(
          // ignore: use_build_context_synchronously
          context,
          MaterialPageRoute(builder: (context) => const HomeScreen()),
        );

      } else {
        // Mostrar mensaje de error si el inicio de sesión falla
        // ignore: use_build_context_synchronously
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Error al iniciar sesión, correo electrónico o contraseña incorrectos'),
          ),
        );
      }
    } catch (e) {
      // Mostrar mensaje de error si hay un error de red u otro error
      // ignore: use_build_context_synchronously
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: $e'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        color: Colors.grey[900], // Fondo gris oscuro
        child: Center(
          child: SizedBox(
            width: MediaQuery.of(context).size.width * 0.8, // 80% del ancho de la pantalla
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Image.asset(
                  'web/assets/images/start_icon.png', // Ruta de la imagen
                  width: 300, // Ancho de la imagen
                  height: 300, // Alto de la imagen
                ),
                const SizedBox(height: 40),

                TextField(
                  controller: emailController, // Asignar el controlador de texto para el correo electrónico
                  decoration: const InputDecoration(
                    hintText: 'Correo o Teléfono',
                    prefixIcon: Icon(Icons.person),
                    hintStyle: TextStyle(color: Colors.white), // Color blanco para el texto de sugerencia
                  ),
                  style: const TextStyle(color: Colors.white), // Color blanco para el texto de entrada
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: passwordController, // Asignar el controlador de texto para la contraseña
                  obscureText: true, // Ocultar texto
                  decoration: const InputDecoration(
                    hintText: 'Contraseña',
                    prefixIcon: Icon(Icons.lock),
                    hintStyle: TextStyle(color: Colors.white), // Color blanco para el texto de sugerencia
                  ),
                  style: const TextStyle(color: Colors.white), // Color blanco para el texto de entrada
                ),
                const SizedBox(height: 40),
                ElevatedButton(
                  onPressed: () {
                    // Acción cuando se presiona el botón de inicio de sesión
                    _login(context, emailController.text, passwordController.text);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green, // Fondo verde 
                  ),
                  child: const Text(
                    'Iniciar sesión',
                    style: TextStyle(color: Colors.white), // Texto blanco
                  ),
                ),
                const SizedBox(height: 20),
                TextButton(
                  onPressed: () {
                    // Navegar a la pantalla de registro
                    Navigator.of(context).pushNamed('/register');
                  },
                  child: const Text(
                    '¿No tienes una cuenta? Regístrate aquí',
                    style: TextStyle(color: Colors.white), // Texto blanco
                  ),
                ),
                TextButton(
                  onPressed: () {
                    // Navegar a la pantalla para olvidar la contraseña
                    Navigator.of(context).push(MaterialPageRoute(builder: (context) => ForgotPasswordScreen()));
                  },
                  child: const Text(
                    '¿Olvidaste tu contraseña?',
                    style: TextStyle(color: Colors.white), // Texto blanco
                  ),
                ),

              ],
            ),
          ),
        ),
      ),
    );
  }
}
