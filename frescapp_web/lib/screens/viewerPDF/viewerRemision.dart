// ignore: file_names
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: PDFViewerScreen(),
    );
  }
}

class PDFViewerScreen extends StatelessWidget {
  final String pdfUrl = "http://app.buyfrescapp.com:5000/api/order/generate_pdf/6656911a7db3eb3b3a007af0";

  const PDFViewerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PDF Viewer'),
      ),
      //SfPdfViewer.network(pdfUrl),
    );
  }
}
